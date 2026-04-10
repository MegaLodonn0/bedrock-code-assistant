"""
parser/treesitter_parser.py — Multi-language parser using tree-sitter v0.25+.

tree-sitter 0.25 removed the deprecated `language.query().captures()` API.
This implementation uses direct AST node traversal (walk by node type), which
is more stable and works identically across all tree-sitter-language-pack versions.

Languages with RICH extraction (functions + classes + imports):
    python, javascript, typescript, tsx, go, java, kotlin,
    rust, c, cpp, c_sharp, ruby

Languages with MODULE-level extraction:
    All other languages supported by tree-sitter-language-pack.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Iterator

from src.core.code_map.languages import RICH_LANGUAGES
from src.core.code_map.parser.base import BaseParser
from src.core.code_map.symbols import ParseResult, Symbol, SymbolKind

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Node type sets per language category
# ---------------------------------------------------------------------------

# Python
_PY_FUNC_TYPES    = {"function_definition"}
_PY_CLASS_TYPES   = {"class_definition"}
_PY_IMPORT_TYPES  = {"import_statement", "import_from_statement"}

# JavaScript / TypeScript
_JS_FUNC_TYPES    = {"function_declaration", "function_expression", "arrow_function"}
_JS_METHOD_TYPES  = {"method_definition"}
_JS_CLASS_TYPES   = {"class_declaration", "class_expression"}
_JS_IMPORT_TYPES  = {"import_statement"}

# Go
_GO_FUNC_TYPES    = {"function_declaration"}
_GO_METHOD_TYPES  = {"method_declaration"}
_GO_STRUCT_TYPES  = {"type_spec"}       # refined further by child type check
_GO_IMPORT_TYPES  = {"import_spec"}

# Java / Kotlin
_JAVA_CLASS_TYPES       = {"class_declaration", "interface_declaration", "enum_declaration"}
_JAVA_METHOD_TYPES      = {"method_declaration", "constructor_declaration"}
_JAVA_IMPORT_TYPES      = {"import_declaration"}

_KT_CLASS_TYPES         = {"class_declaration", "object_declaration"}
_KT_FUNC_TYPES          = {"function_declaration"}
_KT_IMPORT_TYPES        = {"import_header"}

# Rust
_RUST_FUNC_TYPES        = {"function_item"}
_RUST_STRUCT_TYPES      = {"struct_item", "enum_item", "impl_item"}
_RUST_IMPORT_TYPES      = {"use_declaration"}

# C / C++
_C_FUNC_TYPES           = {"function_definition"}
_C_IMPORT_TYPES         = {"preproc_include"}

# C#
_CS_CLASS_TYPES         = {"class_declaration", "interface_declaration", "struct_declaration"}
_CS_METHOD_TYPES        = {"method_declaration", "constructor_declaration"}
_CS_IMPORT_TYPES        = {"using_directive"}

# Ruby
_RUBY_CLASS_TYPES       = {"class", "module"}
_RUBY_FUNC_TYPES        = {"method", "singleton_method"}
_RUBY_IMPORT_TYPES      = {"call"}   # require / require_relative


class TreeSitterParser(BaseParser):
    """
    Parser backed by tree-sitter + tree-sitter-language-pack.

    Uses direct AST node-type traversal (no deprecated query API).
    """

    @property
    def supported_languages(self) -> frozenset[str]:
        return frozenset(self._probe_available_languages())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, file_path: str, source: str, language: str) -> ParseResult:
        try:
            from tree_sitter_language_pack import get_parser as ts_get_parser
        except ImportError:
            return ParseResult(
                file_path=file_path,
                language=language,
                parse_errors=["tree-sitter-language-pack not installed"],
            )

        try:
            parser = ts_get_parser(language)
        except Exception as exc:
            return ParseResult(
                file_path=file_path,
                language=language,
                parse_errors=[f"No parser for language '{language}': {exc}"],
            )

        source_bytes = source.encode("utf-8", errors="replace")
        tree = parser.parse(source_bytes)
        root = tree.root_node

        symbols: list[Symbol] = []
        errors: list[str] = []

        if language in RICH_LANGUAGES:
            try:
                symbols, errors = self._extract_rich(file_path, source, language, root)
            except Exception as exc:
                logger.debug("Rich extraction failed for %s: %s", file_path, exc)
                errors.append(f"Rich extraction error: {exc}")
                symbols = [self._module_symbol(file_path, source, language)]
        else:
            symbols = [self._module_symbol(file_path, source, language)]

        return ParseResult(
            file_path=file_path,
            language=language,
            symbols=symbols,
            parse_errors=errors,
        )

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def _extract_rich(
        self, file_path: str, source: str, language: str, root: Any
    ) -> tuple[list[Symbol], list[str]]:
        dispatch: dict[str, Callable] = {
            "python":     self._parse_python,
            "javascript": self._parse_js,
            "typescript": self._parse_js,
            "tsx":        self._parse_js,
            "go":         self._parse_go,
            "java":       self._parse_java,
            "kotlin":     self._parse_kotlin,
            "rust":       self._parse_rust,
            "c":          self._parse_c,
            "cpp":        self._parse_c,
            "c_sharp":    self._parse_csharp,
            "ruby":       self._parse_ruby,
        }
        fn = dispatch.get(language)
        if fn is None:
            return [self._module_symbol(file_path, source, language)], []
        syms = fn(file_path, source, language, root)
        return syms, []

    # ------------------------------------------------------------------
    # Shared AST walker
    # ------------------------------------------------------------------

    @staticmethod
    def _walk(root: Any, target_types: set[str], max_depth: int = 10) -> Iterator[Any]:
        """
        Yield all descendant nodes whose type is in *target_types*.
        Stops descending at *max_depth* to bound recursion on huge files.
        """
        stack: list[tuple[Any, int]] = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            if node.type in target_types:
                yield node
            if depth < max_depth:
                # Push children in reverse so left-to-right order is preserved
                for child in reversed(node.children):
                    stack.append((child, depth + 1))

    # ------------------------------------------------------------------
    # Python
    # ------------------------------------------------------------------

    def _parse_python(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        symbols: list[Symbol] = []
        rel = Path(file_path).as_posix()

        for node in self._walk(root, _PY_FUNC_TYPES | _PY_CLASS_TYPES):
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = self.safe_decode(name_node.text)
            start = node.start_point[0] + 1
            end   = node.end_point[0] + 1

            if node.type in _PY_CLASS_TYPES:
                kind = SymbolKind.CLASS
                src  = self.extract_lines(source, start, min(start + 10, end))
                outer: str | None = None
            else:
                kind  = SymbolKind.METHOD if self._is_inside_class(node) else SymbolKind.FUNCTION
                src   = self.extract_lines(source, start, end)
                outer = self._outer_class_name(node)

            sym_id = self.make_symbol_id(file_path, *([outer] if outer else []), name)
            symbols.append(Symbol(
                id=sym_id, name=name, kind=kind, language=lang,
                file_path=rel, start_line=start, end_line=end,
                source=src, signature=self._first_line(src),
                docstring=self._extract_py_docstring(src),
                calls=self._extract_py_calls(node) if kind != SymbolKind.CLASS else [],
            ))

        for node in self._walk(root, _PY_IMPORT_TYPES, max_depth=3):
            src   = self.safe_decode(node.text)
            start = node.start_point[0] + 1
            sym_id = self.make_symbol_id(file_path, f"_import_{start}")
            symbols.append(Symbol(
                id=sym_id, name=src[:80], kind=SymbolKind.IMPORT,
                language=lang, file_path=rel,
                start_line=start, end_line=start, source=src,
                imports=self._parse_py_import_paths(src),
            ))

        return symbols

    # ------------------------------------------------------------------
    # JavaScript / TypeScript
    # ------------------------------------------------------------------

    def _parse_js(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        symbols: list[Symbol] = []
        rel = Path(file_path).as_posix()

        for node in self._walk(root, _JS_FUNC_TYPES | _JS_METHOD_TYPES | _JS_CLASS_TYPES):
            kind = (
                SymbolKind.CLASS  if node.type in _JS_CLASS_TYPES  else
                SymbolKind.METHOD if node.type in _JS_METHOD_TYPES else
                SymbolKind.FUNCTION
            )
            name_node = node.child_by_field_name("name")
            name = self.safe_decode(name_node.text) if name_node else "<anonymous>"
            start = node.start_point[0] + 1
            end   = node.end_point[0] + 1
            src   = self.extract_lines(source, start, min(start + 15, end) if kind == SymbolKind.CLASS else end)
            sym_id = self.make_symbol_id(file_path, name)
            symbols.append(Symbol(
                id=sym_id, name=name, kind=kind, language=lang,
                file_path=rel, start_line=start, end_line=end,
                source=src, signature=self._first_line(src),
            ))

        for node in self._walk(root, _JS_IMPORT_TYPES, max_depth=3):
            src   = self.safe_decode(node.text)
            start = node.start_point[0] + 1
            sym_id = self.make_symbol_id(file_path, f"_import_{start}")
            symbols.append(Symbol(
                id=sym_id, name=src[:80], kind=SymbolKind.IMPORT,
                language=lang, file_path=rel,
                start_line=start, end_line=start, source=src,
            ))

        return symbols

    # ------------------------------------------------------------------
    # Go
    # ------------------------------------------------------------------

    def _parse_go(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        symbols: list[Symbol] = []
        rel = Path(file_path).as_posix()

        for node in self._walk(root, _GO_FUNC_TYPES | _GO_METHOD_TYPES):
            kind = SymbolKind.METHOD if node.type in _GO_METHOD_TYPES else SymbolKind.FUNCTION
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name  = self.safe_decode(name_node.text)
            start = node.start_point[0] + 1
            end   = node.end_point[0] + 1
            src   = self.extract_lines(source, start, end)
            symbols.append(Symbol(
                id=self.make_symbol_id(file_path, name), name=name, kind=kind,
                language=lang, file_path=rel, start_line=start, end_line=end,
                source=src, signature=self._first_line(src),
            ))

        # Structs: type_spec nodes whose child type is struct_type
        for node in self._walk(root, _GO_STRUCT_TYPES):
            type_child = node.child_by_field_name("type")
            if not type_child or type_child.type != "struct_type":
                continue
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name  = self.safe_decode(name_node.text)
            start = node.start_point[0] + 1
            end   = node.end_point[0] + 1
            src   = self.extract_lines(source, start, min(start + 8, end))
            symbols.append(Symbol(
                id=self.make_symbol_id(file_path, name), name=name,
                kind=SymbolKind.CLASS, language=lang, file_path=rel,
                start_line=start, end_line=end, source=src,
            ))

        for node in self._walk(root, _GO_IMPORT_TYPES, max_depth=4):
            path_node = node.child_by_field_name("path")
            if not path_node:
                continue
            import_path = self.safe_decode(path_node.text).strip('"\'')
            start = node.start_point[0] + 1
            sym_id = self.make_symbol_id(file_path, f"_import_{start}")
            symbols.append(Symbol(
                id=sym_id, name=import_path, kind=SymbolKind.IMPORT,
                language=lang, file_path=rel, start_line=start, end_line=start,
                source=import_path, imports=[import_path],
            ))

        return symbols

    # ------------------------------------------------------------------
    # Java
    # ------------------------------------------------------------------

    def _parse_java(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        return self._generic_extract(
            file_path, source, lang, root,
            class_types=_JAVA_CLASS_TYPES,
            func_types=_JAVA_METHOD_TYPES,
            import_types=_JAVA_IMPORT_TYPES,
        )

    # ------------------------------------------------------------------
    # Kotlin
    # ------------------------------------------------------------------

    def _parse_kotlin(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        return self._generic_extract(
            file_path, source, lang, root,
            class_types=_KT_CLASS_TYPES,
            func_types=_KT_FUNC_TYPES,
            import_types=_KT_IMPORT_TYPES,
        )

    # ------------------------------------------------------------------
    # Rust
    # ------------------------------------------------------------------

    def _parse_rust(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        return self._generic_extract(
            file_path, source, lang, root,
            class_types=_RUST_STRUCT_TYPES,
            func_types=_RUST_FUNC_TYPES,
            import_types=_RUST_IMPORT_TYPES,
        )

    # ------------------------------------------------------------------
    # C / C++
    # ------------------------------------------------------------------

    def _parse_c(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        return self._generic_extract(
            file_path, source, lang, root,
            class_types=set(),
            func_types=_C_FUNC_TYPES,
            import_types=_C_IMPORT_TYPES,
        )

    # ------------------------------------------------------------------
    # C#
    # ------------------------------------------------------------------

    def _parse_csharp(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        return self._generic_extract(
            file_path, source, lang, root,
            class_types=_CS_CLASS_TYPES,
            func_types=_CS_METHOD_TYPES,
            import_types=_CS_IMPORT_TYPES,
        )

    # ------------------------------------------------------------------
    # Ruby
    # ------------------------------------------------------------------

    def _parse_ruby(self, file_path: str, source: str, lang: str, root: Any) -> list[Symbol]:
        symbols: list[Symbol] = []
        rel = Path(file_path).as_posix()

        for node in self._walk(root, _RUBY_CLASS_TYPES | _RUBY_FUNC_TYPES):
            kind = SymbolKind.CLASS if node.type in _RUBY_CLASS_TYPES else SymbolKind.FUNCTION
            # Ruby uses different field names
            name_node = (
                node.child_by_field_name("name")
                or next((c for c in node.children if c.type in ("constant", "identifier")), None)
            )
            if not name_node:
                continue
            name  = self.safe_decode(name_node.text)
            start = node.start_point[0] + 1
            end   = node.end_point[0] + 1
            src   = self.extract_lines(source, start, min(start + 8, end) if kind == SymbolKind.CLASS else end)
            symbols.append(Symbol(
                id=self.make_symbol_id(file_path, name), name=name, kind=kind,
                language=lang, file_path=rel, start_line=start, end_line=end,
                source=src, signature=self._first_line(src),
            ))

        # Ruby imports: call nodes where method is require/require_relative
        for node in self._walk(root, _RUBY_IMPORT_TYPES, max_depth=5):
            method_node = node.child_by_field_name("method")
            if not method_node:
                continue
            method_name = self.safe_decode(method_node.text)
            if method_name not in ("require", "require_relative", "include", "extend"):
                continue
            src   = self.safe_decode(node.text)
            start = node.start_point[0] + 1
            sym_id = self.make_symbol_id(file_path, f"_import_{start}")
            symbols.append(Symbol(
                id=sym_id, name=src[:80], kind=SymbolKind.IMPORT,
                language=lang, file_path=rel, start_line=start, end_line=start, source=src,
            ))

        return symbols

    # ------------------------------------------------------------------
    # Generic extractor (Java, Kotlin, Rust, C, C#)
    # ------------------------------------------------------------------

    def _generic_extract(
        self,
        file_path: str,
        source: str,
        lang: str,
        root: Any,
        class_types: set[str],
        func_types: set[str],
        import_types: set[str],
    ) -> list[Symbol]:
        symbols: list[Symbol] = []
        rel = Path(file_path).as_posix()

        for node in self._walk(root, class_types | func_types):
            kind = SymbolKind.CLASS if node.type in class_types else SymbolKind.FUNCTION
            name_node = node.child_by_field_name("name")
            if not name_node:
                # Try first identifier child
                name_node = next((c for c in node.children if c.type in ("identifier", "type_identifier", "simple_identifier")), None)
            if not name_node:
                continue
            name  = self.safe_decode(name_node.text)
            start = node.start_point[0] + 1
            end   = node.end_point[0] + 1
            cap   = min(start + 10, end) if kind == SymbolKind.CLASS else end
            src   = self.extract_lines(source, start, cap)
            symbols.append(Symbol(
                id=self.make_symbol_id(file_path, name), name=name, kind=kind,
                language=lang, file_path=rel, start_line=start, end_line=end,
                source=src, signature=self._first_line(src),
            ))

        for node in self._walk(root, import_types, max_depth=4):
            src   = self.safe_decode(node.text)
            start = node.start_point[0] + 1
            sym_id = self.make_symbol_id(file_path, f"_import_{start}")
            symbols.append(Symbol(
                id=sym_id, name=src[:80], kind=SymbolKind.IMPORT,
                language=lang, file_path=rel, start_line=start, end_line=start, source=src,
            ))

        return symbols

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _module_symbol(self, file_path: str, source: str, language: str) -> Symbol:
        rel = Path(file_path).as_posix()
        return Symbol(
            id=self.make_symbol_id(file_path),
            name=Path(file_path).stem,
            kind=SymbolKind.MODULE,
            language=language,
            file_path=rel,
            start_line=1,
            end_line=max(1, source.count("\n") + 1),
            source=source[:2000] if len(source) > 2000 else source,
        )

    @staticmethod
    def _first_line(source: str) -> str:
        return source.splitlines()[0].strip() if source else ""

    @staticmethod
    def _is_inside_class(node: Any) -> bool:
        current = node.parent
        while current is not None:
            if current.type in ("class_definition", "class_body"):
                return True
            current = current.parent
        return False

    @staticmethod
    def _outer_class_name(node: Any) -> str | None:
        current = node.parent
        while current is not None:
            if current.type == "class_definition":
                n = current.child_by_field_name("name")
                if n:
                    try:
                        return n.text.decode("utf-8")
                    except Exception:
                        return None
            current = current.parent
        return None

    @staticmethod
    def _extract_py_docstring(source: str) -> str:
        lines = source.strip().splitlines()
        in_doc = False
        doc_lines: list[str] = []
        for line in lines[1:]:
            stripped = line.strip()
            if not in_doc:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_doc = True
                    inner = stripped.lstrip("\"' ")
                    doc_lines.append(inner)
                    if (stripped.count('"""') >= 2 or stripped.count("'''") >= 2) and len(stripped) > 6:
                        break
                else:
                    break
            else:
                if '"""' in stripped or "'''" in stripped:
                    doc_lines.append(stripped.rstrip("\"' "))
                    break
                doc_lines.append(stripped)
        return " ".join(doc_lines).strip()

    @staticmethod
    def _extract_py_calls(func_node: Any) -> list[str]:
        calls: list[str] = []
        stack = list(func_node.children)
        visited: set[int] = set()
        while stack:
            node = stack.pop()
            nid = id(node)
            if nid in visited:
                continue
            visited.add(nid)
            if node.type == "call":
                fn_node = node.child_by_field_name("function")
                if fn_node:
                    try:
                        calls.append(fn_node.text.decode("utf-8").split("(")[0].strip())
                    except Exception:
                        pass
            stack.extend(node.children)
        return list(dict.fromkeys(calls))[:20]

    @staticmethod
    def _parse_py_import_paths(import_src: str) -> list[str]:
        paths: list[str] = []
        src = import_src.strip()
        if src.startswith("from "):
            parts = src.split()
            if len(parts) >= 2:
                paths.append(parts[1])
        elif src.startswith("import "):
            rest = src[7:]
            paths.extend(m.strip().split(" as ")[0] for m in rest.split(","))
        return [p for p in paths if p]

    @staticmethod
    def _probe_available_languages() -> list[str]:
        try:
            from tree_sitter_language_pack import get_parser
            KNOWN = [
                "python", "javascript", "typescript", "tsx", "go", "java",
                "kotlin", "rust", "c", "cpp", "c_sharp", "ruby", "swift",
                "php", "lua", "bash", "toml", "yaml", "json", "markdown",
                "sql", "dockerfile", "haskell", "elixir", "erlang",
                "clojure", "r", "julia", "dart", "zig", "scala", "groovy",
                "html", "css", "scss",
            ]
            return [lang for lang in KNOWN if _try_parser(lang)]
        except ImportError:
            return []


def _try_parser(lang: str) -> bool:
    try:
        from tree_sitter_language_pack import get_parser
        get_parser(lang)
        return True
    except Exception:
        return False
