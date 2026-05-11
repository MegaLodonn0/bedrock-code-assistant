"""
Agent Tool System
=================
Defines the tools available to the agentic AI.
Each tool is a callable with metadata (name, description, parameters, approval requirement).
The ToolRegistry manages discovery and execution of all tools.
"""

import os
import re
import glob as glob_module
import asyncio
import logging
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────

@dataclass
class ToolResult:
    """Result of a single tool invocation."""
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0


@dataclass
class ToolDefinition:
    """Metadata + callable for a single tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    requires_approval: bool = False
    execute: Optional[Callable[..., Awaitable[ToolResult]]] = None


# ─────────────────────────────────────────────────────────────────
# Built-in tool implementations
# ─────────────────────────────────────────────────────────────────

# Files with more lines than this threshold return an OUTLINE instead
# of full content when start_line/end_line are not specified.
OUTLINE_THRESHOLD = 150


def _build_outline(path: str, lines: list) -> str:
    """
    Return a structural outline of a file with line numbers.
    Python files are parsed with ast for accurate signatures.
    Other file types fall back to regex heuristics.
    """
    total = len(lines)
    header = (
        f"[OUTLINE: {path} — {total} lines]\n"
        f"File is too large to return in full. "
        f"Use read_file(path, start_line=N, end_line=M) to read a specific section, "
        f"or read_symbol(symbol, path) for a named function/class (Python only).\n\n"
    )

    entries: list = []  # list of (lineno, kind, label)

    if path.endswith(".py"):
        try:
            import ast as _ast
            source = "\n".join(lines)
            tree = _ast.parse(source)
            for node in _ast.walk(tree):
                if isinstance(node, _ast.ClassDef):
                    entries.append((node.lineno, "class", f"class {node.name}:"))
                elif isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                    prefix = "async def" if isinstance(node, _ast.AsyncFunctionDef) else "def"
                    args = []
                    for a in node.args.args:
                        args.append(a.arg)
                    sig = f"{prefix} {node.name}({', '.join(args)})"
                    entries.append((node.lineno, "  fn", sig))
        except SyntaxError:
            pass  # fall through to regex below

    if not entries:
        _patterns = [
            (re.compile(r'^\s*(class|interface|struct)\s+(\w+)'), "class"),
            (re.compile(r'^\s*(async\s+)?def\s+(\w+)'),           "  fn"),
            (re.compile(r'^\s*(async\s+)?function\s+(\w+)'),      "  fn"),
            (re.compile(r'^\s*(export\s+)?(default\s+)?(const|let|var)\s+(\w+)\s*=\s*(async\s+)?[({]'), "  fn"),
        ]
        for i, line in enumerate(lines, 1):
            for pat, kind in _patterns:
                if pat.match(line):
                    entries.append((i, kind, line.strip()[:80]))
                    break

    entries.sort(key=lambda x: x[0])
    body = "\n".join(f"  L{lineno:<5} {kind}  {label}" for lineno, kind, label in entries)
    return header + (body if body else "(no recognizable structure found)")


async def tool_read_file(
    path: str,
    start_line: int = None,
    end_line: int = None,
) -> ToolResult:
    """
    Read file contents.
    - With start_line/end_line: returns only that range (1-indexed, inclusive).
    - Without range on a file > OUTLINE_THRESHOLD lines: returns an OUTLINE.
    - Without range on a small file: returns full content.
    """
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return ToolResult("read_file", False, "", f"File not found: {path}",
                              (time.time() - start) * 1000)
        if not os.path.isfile(abs_path):
            return ToolResult("read_file", False, "", f"Not a file: {path}",
                              (time.time() - start) * 1000)

        # Safety: reject binary / huge files
        size = os.path.getsize(abs_path)
        if size > 512_000:  # 500 KB hard cap
            return ToolResult(
                "read_file", False, "",
                f"File too large ({size:,} bytes). Use search_code to locate relevant sections first.",
                (time.time() - start) * 1000,
            )

        def _read():
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        content = await asyncio.to_thread(_read)
        lines = content.splitlines()
        total_lines = len(lines)

        # ── Line-range mode ───────────────────────────────────────
        if start_line is not None or end_line is not None:
            s = max(0, (start_line or 1) - 1)            # convert to 0-indexed
            e = min(total_lines, end_line or total_lines)  # inclusive end
            selected = lines[s:e]
            out = "\n".join(selected)
            return ToolResult(
                "read_file", True,
                f"[Lines {s + 1}–{e} of {total_lines} | {path}]\n{out}",
                execution_time_ms=(time.time() - start) * 1000,
            )

        # ── Large file: return outline instead of full content ────
        if total_lines > OUTLINE_THRESHOLD:
            outline = _build_outline(path, lines)
            return ToolResult(
                "read_file", True, outline,
                execution_time_ms=(time.time() - start) * 1000,
            )

        # ── Small file: return full content ───────────────────────
        return ToolResult("read_file", True, content,
                          execution_time_ms=(time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("read_file", False, "", str(e),
                          (time.time() - start) * 1000)


async def tool_list_dir(path: str = ".", max_depth: int = 2) -> ToolResult:
    """List directory contents up to *max_depth* levels deep."""
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        if not os.path.isdir(abs_path):
            return ToolResult("list_dir", False, "", f"Not a directory: {path}",
                              (time.time() - start) * 1000)

        lines: List[str] = []
        item_count = 0
        max_items = 500  # safety cap

        def _walk(dir_path: str, depth: int, prefix: str):
            nonlocal item_count
            if depth > max_depth or item_count >= max_items:
                return
            try:
                entries = sorted(os.listdir(dir_path))
            except PermissionError:
                lines.append(f"{prefix}[permission denied]")
                return

            # Filter out noisy dirs
            skip = {".git", "__pycache__", ".pytest_cache", "node_modules",
                    ".venv", "venv", "htmlcov", ".coverage", ".mypy_cache"}

            for entry in entries:
                if entry in skip:
                    continue
                full = os.path.join(dir_path, entry)
                is_dir = os.path.isdir(full)
                marker = "📁 " if is_dir else "📄 "
                size_info = ""
                if not is_dir:
                    try:
                        sz = os.path.getsize(full)
                        size_info = f"  ({sz:,} B)"
                    except OSError:
                        pass
                lines.append(f"{prefix}{marker}{entry}{size_info}")
                item_count += 1
                if is_dir and depth < max_depth:
                    _walk(full, depth + 1, prefix + "  ")

        await asyncio.to_thread(_walk, abs_path, 0, "")

        output = "\n".join(lines) if lines else "(empty directory)"
        if item_count >= max_items:
            output += f"\n\n⚠️ Truncated at {max_items} items."
        return ToolResult("list_dir", True, output,
                          execution_time_ms=(time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("list_dir", False, "", str(e),
                          (time.time() - start) * 1000)


async def tool_glob_files(pattern: str, root: str = ".") -> ToolResult:
    """Find files matching a glob pattern (e.g., '**/*.py')."""
    start = time.time()
    try:
        abs_root = os.path.abspath(root)
        matches = sorted(glob_module.glob(
            os.path.join(abs_root, pattern), recursive=True
        ))
        # Limit to 200 results
        truncated = len(matches) > 200
        matches = matches[:200]

        rel_paths = [os.path.relpath(m, abs_root) for m in matches]
        output = "\n".join(rel_paths) if rel_paths else "(no matches)"
        if truncated:
            output += "\n\n⚠️ Truncated to 200 results."
        return ToolResult("glob_files", True, output,
                          execution_time_ms=(time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("glob_files", False, "", str(e),
                          (time.time() - start) * 1000)


# Context lines shown around each search match (before + after)
_SEARCH_CONTEXT = 2


async def tool_search_code(query: str, path: str = ".", max_results: int = 20) -> ToolResult:
    """
    Search for a text pattern across source files (case-insensitive).
    Returns each match with surrounding context lines so you can often
    avoid a follow-up read_file call entirely.
    """
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        results: List[str] = []

        skip_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules",
                     "venv", ".venv", "htmlcov"}
        text_exts = {".py", ".js", ".ts", ".json", ".md", ".txt", ".toml",
                     ".yaml", ".yml", ".cfg", ".ini", ".html", ".css",
                     ".sh", ".bat", ".env"}

        pattern = re.compile(re.escape(query), re.IGNORECASE)

        def _search():
            for root_dir, dirs, files in os.walk(abs_path):
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                for fname in files:
                    if len(results) >= max_results:
                        return
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in text_exts:
                        continue
                    fpath = os.path.join(root_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                            all_lines = f.readlines()
                        for line_no, line in enumerate(all_lines, 1):
                            if len(results) >= max_results:
                                return
                            if pattern.search(line):
                                rel = os.path.relpath(fpath, abs_path)
                                # Gather context lines around the match
                                ctx_start = max(0, line_no - 1 - _SEARCH_CONTEXT)
                                ctx_end   = min(len(all_lines), line_no + _SEARCH_CONTEXT)
                                ctx_lines = []
                                for ci in range(ctx_start, ctx_end):
                                    marker = "►" if ci == line_no - 1 else " "
                                    ctx_lines.append(
                                        f"  {ci + 1:4}│{marker} {all_lines[ci].rstrip()}"
                                    )
                                block = f"{rel}:{line_no}\n" + "\n".join(ctx_lines)
                                results.append(block)
                    except (OSError, UnicodeDecodeError):
                        continue

        await asyncio.to_thread(_search)

        output = "\n\n".join(results) if results else f"No matches for '{query}'"
        if len(results) >= max_results:
            output += f"\n\n⚠️ Truncated at {max_results} results."
        return ToolResult("search_code", True, output,
                          execution_time_ms=(time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("search_code", False, "", str(e),
                          (time.time() - start) * 1000)


async def tool_tree_view(path: str = ".", max_depth: int = 3) -> ToolResult:
    """Display a tree-style view of the project directory."""
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        if not os.path.isdir(abs_path):
            return ToolResult("tree_view", False, "", f"Not a directory: {path}",
                              (time.time() - start) * 1000)

        lines: List[str] = [os.path.basename(abs_path) + "/"]
        item_count = 0
        max_items = 300

        skip = {".git", "__pycache__", ".pytest_cache", "node_modules",
                "venv", ".venv", "htmlcov", ".mypy_cache"}

        def _tree(dir_path: str, prefix: str, depth: int):
            nonlocal item_count
            if depth > max_depth or item_count >= max_items:
                return
            try:
                entries = sorted(os.listdir(dir_path))
            except PermissionError:
                return
            entries = [e for e in entries if e not in skip]
            for i, entry in enumerate(entries):
                if item_count >= max_items:
                    return
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                full = os.path.join(dir_path, entry)
                is_dir = os.path.isdir(full)
                lines.append(f"{prefix}{connector}{entry}{'/' if is_dir else ''}")
                item_count += 1
                if is_dir and depth < max_depth:
                    ext_prefix = prefix + ("    " if is_last else "│   ")
                    _tree(full, ext_prefix, depth + 1)

        await asyncio.to_thread(_tree, abs_path, "", 0)
        output = "\n".join(lines)
        if item_count >= max_items:
            output += f"\n\n⚠️ Truncated at {max_items} items."
        return ToolResult("tree_view", True, output,
                          execution_time_ms=(time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("tree_view", False, "", str(e),
                          (time.time() - start) * 1000)


async def tool_read_symbol(symbol: str, path: str) -> ToolResult:
    """
    Extract a named function or class from a Python file using AST.
    Supports 'ClassName.method_name' and 'function_name' formats.
    More efficient than read_file with line ranges — no line numbers needed.
    """
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return ToolResult("read_symbol", False, "", f"File not found: {path}",
                              (time.time() - start) * 1000)
        if not path.endswith(".py"):
            return ToolResult(
                "read_symbol", False, "",
                "read_symbol only supports Python (.py) files. Use read_file with start_line/end_line for other types.",
                (time.time() - start) * 1000,
            )

        def _extract():
            import ast as _ast
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            lines = source.splitlines()
            tree = _ast.parse(source)

            parts = symbol.strip().split(".")
            target_class  = parts[0] if len(parts) > 1 else None
            target_symbol = parts[-1]

            found = None

            if target_class:
                # Look for ClassName.method_name
                for node in _ast.walk(tree):
                    if isinstance(node, _ast.ClassDef) and node.name == target_class:
                        for child in node.body:
                            if isinstance(child, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                                if child.name == target_symbol:
                                    found = child
                                    break
                        break
            else:
                # Top-level function or class
                for node in _ast.walk(tree):
                    if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                        if node.name == target_symbol:
                            found = node
                            break

            if found is None:
                return None, None, None

            sl = found.lineno
            el = getattr(found, "end_lineno", None)
            if el is None:
                # Python < 3.8 fallback: read until next same-indent block
                el = sl
                base_indent = len(lines[sl - 1]) - len(lines[sl - 1].lstrip())
                for i in range(sl, len(lines)):
                    stripped = lines[i].lstrip()
                    if stripped and i > sl - 1:
                        indent = len(lines[i]) - len(stripped)
                        if indent <= base_indent and not lines[i].strip().startswith("#"):
                            break
                    el = i + 1

            return lines[sl - 1:el], sl, el

        selected, sl, el = await asyncio.to_thread(_extract)

        if selected is None:
            return ToolResult(
                "read_symbol", False, "",
                f"Symbol '{symbol}' not found in {path}. "
                f"Try read_file(path) first to see the file outline.",
                (time.time() - start) * 1000,
            )

        out = "\n".join(selected)
        return ToolResult(
            "read_symbol", True,
            f"[{symbol} — Lines {sl}–{el} of {path}]\n\n{out}",
            execution_time_ms=(time.time() - start) * 1000,
        )
    except SyntaxError as e:
        return ToolResult("read_symbol", False, "", f"Syntax error parsing {path}: {e}",
                          (time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("read_symbol", False, "", str(e),
                          (time.time() - start) * 1000)


# ─────────────────────────────────────────────────────────────────
# Tool Registry
# ─────────────────────────────────────────────────────────────────

class ToolRegistry:
    """Central registry for all agent tools."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_builtins()

    def _register_builtins(self):
        """Register the built-in read-only tools."""
        self.register(ToolDefinition(
            name="read_file",
            description=(
                "Read the contents of a file. "
                f"Files over {OUTLINE_THRESHOLD} lines return an [OUTLINE] with line numbers instead of full content — "
                "you MUST then call read_file again with start_line and end_line, or use read_symbol. "
                "Use start_line/end_line to read a specific section directly. "
                "For Python symbols, prefer read_symbol over line ranges."
            ),
            parameters={
                "path":       {"type": "string",  "description": "Path to the file (relative or absolute)"},
                "start_line": {"type": "integer", "description": "First line to read, 1-indexed inclusive. Optional.", "default": None},
                "end_line":   {"type": "integer", "description": "Last line to read, 1-indexed inclusive. Optional.",  "default": None},
            },
            requires_approval=False,
            execute=lambda **kw: tool_read_file(**kw),
        ))
        self.register(ToolDefinition(
            name="read_symbol",
            description=(
                "Extract a named function or class from a Python file by symbol name. "
                "More efficient than read_file with line ranges — no line numbers needed. "
                "Supports 'ClassName.method_name' and bare 'function_name'. "
                "Python files only."
            ),
            parameters={
                "symbol": {"type": "string", "description": "Symbol to extract, e.g. 'Executor.ask_ai' or 'tool_read_file'"},
                "path":   {"type": "string", "description": "Path to the Python file"},
            },
            requires_approval=False,
            execute=lambda **kw: tool_read_symbol(**kw),
        ))
        self.register(ToolDefinition(
            name="list_dir",
            description="List the contents of a directory (files and subdirectories), up to a configurable depth.",
            parameters={
                "path": {"type": "string", "description": "Directory path. Default: current directory", "default": "."},
                "max_depth": {"type": "integer", "description": "How many levels deep to list. Default: 2", "default": 2},
            },
            requires_approval=False,
            execute=lambda **kw: tool_list_dir(**kw),
        ))
        self.register(ToolDefinition(
            name="glob_files",
            description="Find files matching a glob pattern, e.g. '**/*.py' to find all Python files.",
            parameters={
                "pattern": {"type": "string", "description": "Glob pattern, e.g. '**/*.py'"},
                "root": {"type": "string", "description": "Root directory for the search. Default: '.'", "default": "."},
            },
            requires_approval=False,
            execute=lambda **kw: tool_glob_files(**kw),
        ))
        self.register(ToolDefinition(
            name="search_code",
            description=(
                "Search for a text pattern across source files (case-insensitive). "
                "Returns each match with surrounding context lines — often enough to answer "
                "without a follow-up read_file call. ALWAYS use this before read_file "
                "to locate the relevant section."
            ),
            parameters={
                "query": {"type": "string", "description": "Text or identifier to search for"},
                "path":  {"type": "string", "description": "Directory to search in. Default: '.'", "default": "."},
            },
            requires_approval=False,
            execute=lambda **kw: tool_search_code(**kw),
        ))
        self.register(ToolDefinition(
            name="tree_view",
            description="Display a tree-style view of the project directory structure.",
            parameters={
                "path": {"type": "string", "description": "Root directory. Default: '.'", "default": "."},
                "max_depth": {"type": "integer", "description": "Max depth. Default: 3", "default": 3},
            },
            requires_approval=False,
            execute=lambda **kw: tool_tree_view(**kw),
        ))

    def register(self, tool: ToolDefinition):
        """Register a new tool."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for the AI system prompt."""
        lines = []
        for tool in self._tools.values():
            params_desc = ", ".join(
                f"{k}: {v.get('type', 'string')}"
                for k, v in tool.parameters.items()
            )
            approval = " ⚠️ REQUIRES USER APPROVAL" if tool.requires_approval else ""
            lines.append(f"- {tool.name}({params_desc}): {tool.description}{approval}")
        return "\n".join(lines)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas in Bedrock ToolConfiguration format."""
        schemas = []
        for tool in self._tools.values():
            properties = {}
            required = []
            for param_name, param_info in tool.parameters.items():
                properties[param_name] = {
                    "type": param_info.get("type", "string"),
                    "description": param_info.get("description", ""),
                }
                if "default" not in param_info:
                    required.append(param_name)

            schemas.append({
                "toolSpec": {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": properties,
                            "required": required,
                        }
                    }
                }
            })
        return schemas

    async def execute_tool(self, name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name with the given parameters."""
        tool = self.get(name)
        if tool is None:
            return ToolResult(name, False, "", f"Unknown tool: {name}")
        if tool.execute is None:
            return ToolResult(name, False, "", f"Tool {name} has no execute function")
        try:
            return await tool.execute(**params)
        except TypeError as e:
            return ToolResult(name, False, "", f"Invalid parameters for {name}: {e}")
        except Exception as e:
            return ToolResult(name, False, "", f"Tool {name} failed: {e}")
