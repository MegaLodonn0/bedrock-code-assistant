"""
languages.py — file-extension ↔ language mapping and parser factory.

Centralises all language detection logic so that parsers, the graph indexer,
and the context builder can all call one consistent API:

    lang = detect_language("src/app.tsx")  # → "typescript"
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Extension → language name
# ---------------------------------------------------------------------------

#: Maps lowercase file extensions (without leading dot) to tree-sitter language names.
_EXT_TO_LANG: dict[str, str] = {
    # Python
    "py": "python",
    "pyw": "python",
    "pyi": "python",
    # JavaScript
    "js": "javascript",
    "mjs": "javascript",
    "cjs": "javascript",
    # TypeScript
    "ts": "typescript",
    "tsx": "tsx",
    "mts": "typescript",
    # Web
    "html": "html",
    "htm": "html",
    "css": "css",
    "scss": "scss",
    # JVM
    "java": "java",
    "kt": "kotlin",
    "kts": "kotlin",
    "scala": "scala",
    "groovy": "groovy",
    # Go
    "go": "go",
    # Rust
    "rs": "rust",
    # C / C++
    "c": "c",
    "h": "c",
    "cpp": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp",
    "hxx": "cpp",
    # C#
    "cs": "c_sharp",
    # Ruby
    "rb": "ruby",
    # Swift
    "swift": "swift",
    # PHP
    "php": "php",
    # Lua
    "lua": "lua",
    # Bash / Shell
    "sh": "bash",
    "bash": "bash",
    "zsh": "bash",
    # TOML / YAML / JSON
    "toml": "toml",
    "yaml": "yaml",
    "yml": "yaml",
    "json": "json",
    # Markdown
    "md": "markdown",
    "mdx": "markdown",
    # SQL
    "sql": "sql",
    # Dockerfile
    "dockerfile": "dockerfile",
    # Haskell
    "hs": "haskell",
    # Elixir
    "ex": "elixir",
    "exs": "elixir",
    # Erlang
    "erl": "erlang",
    # Clojure
    "clj": "clojure",
    "cljs": "clojure",
    # R
    "r": "r",
    # Julia
    "jl": "julia",
    # Dart
    "dart": "dart",
    # Zig
    "zig": "zig",
}

# ---------------------------------------------------------------------------
# Languages for which tree-sitter queries extract rich structured symbols.
# Others get import-only extraction via tree-sitter + fallback tokenisation.
# ---------------------------------------------------------------------------

#: Languages with full structured query support (functions, classes, imports).
RICH_LANGUAGES: frozenset[str] = frozenset(
    {
        "python",
        "javascript",
        "typescript",
        "tsx",
        "go",
        "java",
        "kotlin",
        "rust",
        "c",
        "cpp",
        "c_sharp",
        "ruby",
    }
)

#: Languages that are config / data formats — we index them for imports only.
DATA_LANGUAGES: frozenset[str] = frozenset(
    {"json", "toml", "yaml", "markdown", "sql", "dockerfile"}
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_language(file_path: str | Path) -> str | None:
    """
    Return the tree-sitter language name for *file_path*, or ``None`` if the
    extension is not recognised.

    Special cases:
    - ``Dockerfile`` (no extension) → ``'dockerfile'``
    - ``Makefile`` → ``'makefile'``
    """
    path = Path(file_path)
    name_lower = path.name.lower()

    # Exact filename matches first
    _FILENAME_MAP: dict[str, str] = {
        "dockerfile": "dockerfile",
        "makefile": "makefile",
        "gemfile": "ruby",
        "rakefile": "ruby",
        "vagrantfile": "ruby",
        "procfile": "bash",
    }
    if name_lower in _FILENAME_MAP:
        return _FILENAME_MAP[name_lower]

    # Extension lookup
    suffix = path.suffix.lstrip(".").lower()
    if suffix:
        lang = _EXT_TO_LANG.get(suffix)
        if lang:
            return lang

    return None


def is_rich_language(lang: str) -> bool:
    """Return True if *lang* has full function/class symbol extraction."""
    return lang in RICH_LANGUAGES


def is_parseable(file_path: str | Path) -> bool:
    """Return True if we have any parser support for this file."""
    return detect_language(file_path) is not None


def get_all_supported_extensions() -> list[str]:
    """Return sorted list of all supported file extensions (with leading dot)."""
    return sorted(f".{ext}" for ext in _EXT_TO_LANG)


def get_language_display_name(lang: str) -> str:
    """Return a human-readable display name for a language identifier."""
    _DISPLAY: dict[str, str] = {
        "c_sharp": "C#",
        "cpp": "C++",
        "bash": "Bash/Shell",
        "tsx": "TypeScript JSX",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
    }
    return _DISPLAY.get(lang, lang.capitalize())
