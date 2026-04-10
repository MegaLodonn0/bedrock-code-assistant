"""
parser/fallback_parser.py — Pygments-based tokenizer fallback.

Used for any file whose language is not supported by tree-sitter-language-pack.
Extracts token-level symbols (function names, class names, imports) via
Pygments lexer analysis — no AST, but good enough to build a rough graph node.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from src.core.code_map.parser.base import BaseParser
from src.core.code_map.symbols import ParseResult, Symbol, SymbolKind

logger = logging.getLogger(__name__)


class FallbackParser(BaseParser):
    """
    Pygments-based parser.

    Produces coarse MODULE-level symbols and best-effort import detection.
    Intended as a last resort when tree-sitter has no grammar for the language.
    """

    @property
    def supported_languages(self) -> frozenset[str]:
        """
        Returns all languages that Pygments can lexify.
        In practice we use this parser only when tree-sitter has no grammar.
        """
        try:
            from pygments.lexers import get_all_lexers
            return frozenset(
                alias
                for _, aliases, _, _ in get_all_lexers()
                for alias in aliases
            )
        except Exception:
            return frozenset()

    def parse(self, file_path: str, source: str, language: str) -> ParseResult:
        errors: list[str] = []
        symbols: list[Symbol] = []

        try:
            symbols = self._tokenize(file_path, source, language)
        except Exception as exc:
            logger.debug("Fallback parse failed for %s: %s", file_path, exc)
            errors.append(f"Fallback parse error: {exc}")
            # Always produce at least a MODULE symbol
            symbols = [self._module_symbol(file_path, source, language)]

        return ParseResult(
            file_path=file_path,
            language=language,
            symbols=symbols,
            parse_errors=errors,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tokenize(self, file_path: str, source: str, language: str) -> list[Symbol]:
        from pygments.lexers import get_lexer_by_name
        from pygments.token import Token

        try:
            lexer = get_lexer_by_name(language)
        except Exception:
            return [self._module_symbol(file_path, source, language)]

        tokens = list(lexer.get_tokens(source))
        symbols: list[Symbol] = [self._module_symbol(file_path, source, language)]
        lines = source.splitlines()

        # Collect line-number info
        line = 1
        prev_type = None
        prev_value = ""
        for ttype, value in tokens:
            line += value.count("\n")
            # Heuristic: Name.Class token → CLASS symbol
            if ttype in Token.Name.Class:
                sym_id = self.make_symbol_id(file_path, value.strip())
                symbols.append(Symbol(
                    id=sym_id,
                    name=value.strip(),
                    kind=SymbolKind.CLASS,
                    language=language,
                    file_path=Path(file_path).as_posix(),
                    start_line=line,
                    end_line=line,
                    source=lines[line - 1] if line <= len(lines) else "",
                ))
            # Heuristic: Keyword "def"/"function"/"func" then Name → FUNCTION
            elif (ttype in Token.Keyword or str(ttype).startswith("Token.Keyword")) and value.strip() in (
                "def", "function", "func", "fn", "sub", "procedure", "method"
            ):
                prev_type = "funckey"
                prev_value = value
                continue
            elif prev_type == "funckey" and ttype in Token.Name:
                sym_id = self.make_symbol_id(file_path, value.strip())
                symbols.append(Symbol(
                    id=sym_id,
                    name=value.strip(),
                    kind=SymbolKind.FUNCTION,
                    language=language,
                    file_path=Path(file_path).as_posix(),
                    start_line=line,
                    end_line=line,
                    source=lines[line - 1] if line <= len(lines) else "",
                ))
            prev_type = None
            prev_value = ""

        return symbols

    def _module_symbol(self, file_path: str, source: str, language: str) -> Symbol:
        """Always produce at least a MODULE-level symbol as a graph node."""
        rel = Path(file_path).as_posix()
        line_count = source.count("\n") + 1
        return Symbol(
            id=self.make_symbol_id(file_path),
            name=Path(file_path).stem,
            kind=SymbolKind.MODULE,
            language=language,
            file_path=rel,
            start_line=1,
            end_line=line_count,
            source=source[:1000] if len(source) > 1000 else source,
        )
