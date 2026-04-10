"""
parser/base.py — Abstract base class for all code parsers.

Every language-specific parser must implement ``parse()``.  The rest of the
pipeline (indexer, graph builder) works exclusively against ``BaseParser``
so new languages can be added without touching existing code.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from src.core.code_map.symbols import ParseResult, Symbol

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract parser.  Subclasses implement ``parse()`` for one or more
    programming languages.
    """

    @property
    @abstractmethod
    def supported_languages(self) -> frozenset[str]:
        """Set of language names this parser handles."""

    @abstractmethod
    def parse(self, file_path: str, source: str, language: str) -> ParseResult:
        """
        Parse *source* (the content of *file_path*) and return a ``ParseResult``.

        Parameters
        ----------
        file_path:
            Path of the file (used for symbol IDs and error messages).
        source:
            Full UTF-8 source text of the file.
        language:
            Language identifier (e.g. 'python', 'javascript').

        Returns
        -------
        ParseResult
            Always returns a result object; parse errors are stored in
            ``ParseResult.parse_errors`` rather than raised.
        """

    def can_parse(self, language: str) -> bool:
        """Return True if this parser handles *language*."""
        return language in self.supported_languages

    # ------------------------------------------------------------------
    # Helpers available to subclasses
    # ------------------------------------------------------------------

    @staticmethod
    def make_symbol_id(file_path: str, *name_parts: str) -> str:
        """
        Build a stable, unique symbol ID.

        Examples
        --------
        make_symbol_id("src/foo.py", "MyClass", "my_method")
        → "src/foo.py::MyClass::my_method"

        make_symbol_id("src/foo.py", "top_level_fn")
        → "src/foo.py::top_level_fn"
        """
        parts = [str(Path(file_path).as_posix())] + [p for p in name_parts if p]
        return "::".join(parts)

    @staticmethod
    def safe_decode(source_bytes: bytes) -> str:
        """Decode bytes to str, replacing errors rather than raising."""
        try:
            return source_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return source_bytes.decode("utf-8", errors="replace")

    @staticmethod
    def extract_lines(source: str, start_line: int, end_line: int) -> str:
        """
        Return the slice ``source[start_line:end_line]`` (1-indexed, inclusive).
        """
        lines = source.splitlines()
        sl = max(0, start_line - 1)
        el = min(len(lines), end_line)
        return "\n".join(lines[sl:el])
