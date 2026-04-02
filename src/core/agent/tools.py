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

async def tool_read_file(path: str) -> ToolResult:
    """Read and return the contents of a file."""
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
        if size > 512_000:  # 500 KB
            return ToolResult(
                "read_file", False, "",
                f"File too large ({size:,} bytes). Max 500 KB.",
                (time.time() - start) * 1000,
            )

        def _read():
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        content = await asyncio.to_thread(_read)
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


async def tool_search_code(query: str, path: str = ".", max_results: int = 50) -> ToolResult:
    """Search for a text pattern across files under *path* (case-insensitive)."""
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        results: List[str] = []

        skip_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules",
                     "venv", ".venv", "htmlcov", "data"}
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
                            for line_no, line in enumerate(f, 1):
                                if pattern.search(line):
                                    rel = os.path.relpath(fpath, abs_path)
                                    snippet = line.strip()[:120]
                                    results.append(f"{rel}:{line_no}: {snippet}")
                                    if len(results) >= max_results:
                                        return
                    except (OSError, UnicodeDecodeError):
                        continue

        await asyncio.to_thread(_search)

        output = "\n".join(results) if results else f"No matches for '{query}'"
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
            description="Read the contents of a file. Returns the full text of the file.",
            parameters={
                "path": {"type": "string", "description": "Path to the file to read (relative or absolute)"}
            },
            requires_approval=False,
            execute=lambda **kw: tool_read_file(**kw),
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
            description="Search for a text pattern across source files (case-insensitive). Returns matching lines with file:line format.",
            parameters={
                "query": {"type": "string", "description": "Text to search for"},
                "path": {"type": "string", "description": "Directory to search in. Default: '.'", "default": "."},
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
