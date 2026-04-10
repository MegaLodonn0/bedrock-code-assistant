"""
code_mapper.py — Top-level orchestrator for the Code Map System.

This module wires together the parsers, symbol graph, and context engine
into a single high-level API consumed by the executor and agent tools.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional

from src.core.code_map.languages import detect_language, is_parseable
from src.core.code_map.symbols import ContextBundle, ParseResult, Symbol

logger = logging.getLogger(__name__)


class CodeMapper:
    """
    Process-global code mapping orchestrator.

    Responsibilities:
    - Parse source files via TreeSitterParser (+ FallbackParser)
    - Maintain a SymbolGraph of all indexed symbols
    - Serve minimum-viable ContextBundles for Bedrock API calls
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._indexed_files: set[str] = set()

        # Lazy-initialised components (to keep import time fast)
        self._ts_parser = None
        self._fb_parser = None
        self._graph = None

    # ------------------------------------------------------------------
    # Parser access
    # ------------------------------------------------------------------

    def _get_ts_parser(self):
        if self._ts_parser is None:
            from src.core.code_map.parser.treesitter_parser import TreeSitterParser
            self._ts_parser = TreeSitterParser()
        return self._ts_parser

    def _get_fb_parser(self):
        if self._fb_parser is None:
            from src.core.code_map.parser.fallback_parser import FallbackParser
            self._fb_parser = FallbackParser()
        return self._fb_parser

    def _get_graph(self):
        if self._graph is None:
            from src.core.code_map.graph.symbol_graph import SymbolGraph
            self._graph = SymbolGraph()
        return self._graph

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def index_file(self, file_path: str) -> ParseResult:
        """
        Parse *file_path* and upsert its symbols into the graph.

        Returns the ParseResult (check `.parse_errors` for issues).
        """
        path = Path(file_path)
        if not path.exists():
            return ParseResult(
                file_path=str(path),
                language="unknown",
                parse_errors=[f"File not found: {path}"],
            )

        language = detect_language(file_path)
        if language is None:
            return ParseResult(
                file_path=str(path),
                language="unknown",
                parse_errors=[f"Unsupported file type: {path.suffix}"],
            )

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return ParseResult(
                file_path=str(path),
                language=language,
                parse_errors=[f"Cannot read file: {exc}"],
            )

        ts = self._get_ts_parser()
        if ts.can_parse(language):
            result = ts.parse(str(path), source, language)
        else:
            result = self._get_fb_parser().parse(str(path), source, language)

        graph = self._get_graph()
        with self._lock:
            for sym in result.symbols:
                graph.add_symbol(sym)
            self._indexed_files.add(str(path))

        logger.debug("Indexed %s: %d symbols", path.name, len(result.symbols))
        return result

    def index_directory(
        self,
        root: str,
        patterns: Optional[list[str]] = None,
        exclude_dirs: Optional[set[str]] = None,
    ) -> int:
        """
        Recursively index all parseable files under *root*.

        Returns the total number of symbols indexed.
        """
        if patterns is None:
            patterns = ["**/*"]
        if exclude_dirs is None:
            exclude_dirs = {
                ".git", "__pycache__", "node_modules", ".venv", "venv",
                "dist", "build", ".tox", "htmlcov",
            }

        root_path = Path(root)
        total_symbols = 0

        for pattern in patterns:
            for file_path in root_path.glob(pattern):
                if not file_path.is_file():
                    continue
                if any(ex in file_path.parts for ex in exclude_dirs):
                    continue
                if not is_parseable(str(file_path)):
                    continue
                result = self.index_file(str(file_path))
                total_symbols += len(result.symbols)

        logger.info("Indexed directory %s: %d total symbols", root, total_symbols)
        return total_symbols

    def get_context(
        self,
        file: str,
        query: str,
        symbol: Optional[str] = None,
        depth: int = 2,
        token_budget: int = 2000,
    ) -> ContextBundle:
        """
        Return a ContextBundle for *file* / *symbol* relevant to *query*.

        If the file has not been indexed yet, it is indexed on demand.
        """
        # Auto-index if not seen before
        file_str = str(Path(file).as_posix())
        if file_str not in self._indexed_files and str(Path(file)) not in self._indexed_files:
            self.index_file(file)

        graph = self._get_graph()
        from src.core.code_map.context.selector import ContextSelector
        from src.core.code_map.context.builder import ContextBuilder

        selector = ContextSelector(graph)
        builder = ContextBuilder()

        anchor_id = self._resolve_anchor(file, symbol, graph)
        selected = selector.select(
            anchor_id=anchor_id,
            query=query,
            depth=depth,
            token_budget=token_budget,
        )
        return builder.build(
            query=query,
            anchor_id=anchor_id,
            symbols=selected,
            depth=depth,
        )

    def invalidate(self, file_path: str) -> None:
        """Remove a file's symbols from the graph (call after file changes)."""
        graph = self._get_graph()
        with self._lock:
            graph.remove_file(file_path)
            self._indexed_files.discard(file_path)
            self._indexed_files.discard(str(Path(file_path)))

    def stats(self) -> dict:
        """Return graph statistics for monitoring / display."""
        graph = self._get_graph()
        return {
            "indexed_files": len(self._indexed_files),
            "total_symbols": graph.node_count(),
            "total_edges": graph.edge_count(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_anchor(self, file: str, symbol: Optional[str], graph) -> str:
        """
        Determine the anchor symbol ID for context selection.

        Priority:
        1. Caller provided a symbol name → find best-matching node in graph
        2. Fall back to the MODULE node for the file
        """
        from src.core.code_map.parser.base import BaseParser

        file_posix = Path(file).as_posix()

        if symbol:
            # Check exact ID first
            exact = f"{file_posix}::{symbol}"
            if graph.has_node(exact):
                return exact
            # Fuzzy: any node whose id ends with ::{symbol}
            for node_id in graph.nodes():
                if node_id.endswith(f"::{symbol}") and file_posix in node_id:
                    return node_id

        # Default: MODULE-level node = just the file path
        module_id = BaseParser.make_symbol_id(file_posix)
        if graph.has_node(module_id):
            return module_id

        # Last resort: first node whose id starts with the file path
        for node_id in graph.nodes():
            if node_id.startswith(file_posix):
                return node_id

        return module_id  # return it even if not in graph; selector handles missing gracefully


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_mapper: Optional[CodeMapper] = None
_mapper_lock = threading.Lock()


def get_code_mapper() -> CodeMapper:
    """Return the process-global CodeMapper (thread-safe lazy init)."""
    global _mapper
    if _mapper is None:
        with _mapper_lock:
            if _mapper is None:
                _mapper = CodeMapper()
    return _mapper


def reset_code_mapper() -> None:
    """Reset the singleton — for use in tests only."""
    global _mapper
    with _mapper_lock:
        _mapper = None
