"""
graph/indexer.py — File walker that feeds the SymbolGraph.

The Indexer walks a directory tree, detects languages, delegates to the
appropriate parser, and upserts all extracted symbols into the SymbolGraph.
It also attempts to resolve cross-file call edges by matching raw call names
to known symbol IDs in the graph.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from src.core.code_map.graph.symbol_graph import SymbolGraph
from src.core.code_map.languages import detect_language, is_parseable
from src.core.code_map.symbols import EdgeKind, ParseResult

logger = logging.getLogger(__name__)

_DEFAULT_EXCLUDE_DIRS: set[str] = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".tox", "htmlcov", ".mypy_cache", ".pytest_cache",
    "coverage", ".eggs",
}


class Indexer:
    """
    Walks a file tree, parses each file, and populates a SymbolGraph.

    Usage
    -----
        graph = SymbolGraph()
        indexer = Indexer(graph)
        stats = indexer.index_directory("src/", patterns=["**/*.py"])
        print(stats)
    """

    def __init__(self, graph: SymbolGraph) -> None:
        self._graph = graph
        self._ts_parser = None
        self._fb_parser = None

    # ------------------------------------------------------------------
    # Parsers (lazy init)
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def index_file(self, file_path: str) -> ParseResult:
        """
        Parse *file_path* and upsert its symbols into the graph.

        Returns ParseResult (check .parse_errors for issues).
        """
        path = Path(file_path)
        if not path.exists():
            return ParseResult(
                file_path=str(path),
                language="unknown",
                parse_errors=[f"File not found: {path}"],
            )

        language = detect_language(str(path))
        if language is None:
            return ParseResult(
                file_path=str(path),
                language="unknown",
                parse_errors=[f"Unsupported: {path.suffix}"],
            )

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return ParseResult(
                file_path=str(path),
                language=language,
                parse_errors=[f"Read error: {exc}"],
            )

        return self._parse_and_ingest(str(path), source, language)

    def index_source(self, file_path: str, source: str) -> ParseResult:
        """
        Parse *source* as if it were the content of *file_path*.
        Useful for indexing in-memory buffers (e.g. unsaved editor content).
        """
        language = detect_language(file_path)
        if language is None:
            return ParseResult(
                file_path=file_path,
                language="unknown",
                parse_errors=[f"Cannot detect language for: {file_path}"],
            )
        return self._parse_and_ingest(file_path, source, language)

    def index_directory(
        self,
        root: str,
        patterns: Optional[list[str]] = None,
        exclude_dirs: Optional[set[str]] = None,
    ) -> dict:
        """
        Recursively index all parseable files under *root*.

        Returns a stats dict:
            {
              "files_indexed": int,
              "symbols_added": int,
              "files_failed": int,
              "errors": list[str],
            }
        """
        if patterns is None:
            patterns = ["**/*"]
        if exclude_dirs is None:
            exclude_dirs = _DEFAULT_EXCLUDE_DIRS

        root_path = Path(root)
        stats = {"files_indexed": 0, "symbols_added": 0, "files_failed": 0, "errors": []}

        for pattern in patterns:
            for file_path in sorted(root_path.glob(pattern)):
                if not file_path.is_file():
                    continue
                if any(ex in file_path.parts for ex in exclude_dirs):
                    continue
                if not is_parseable(str(file_path)):
                    continue

                result = self.index_file(str(file_path))
                if result.parse_errors:
                    stats["files_failed"] += 1
                    stats["errors"].extend(result.parse_errors[:3])
                else:
                    stats["files_indexed"] += 1
                    stats["symbols_added"] += len(result.symbols)

        # After all files are indexed, wire cross-file call edges
        self._resolve_cross_file_calls()
        logger.info("Indexed directory %s: %s", root, stats)
        return stats

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _parse_and_ingest(self, file_path: str, source: str, language: str) -> ParseResult:
        ts = self._get_ts_parser()
        if ts.can_parse(language):
            result = ts.parse(file_path, source, language)
        else:
            result = self._get_fb_parser().parse(file_path, source, language)

        # Remove stale nodes for this file before re-ingesting
        self._graph.remove_file(file_path)

        for sym in result.symbols:
            self._graph.add_symbol(sym)

        return result

    def _resolve_cross_file_calls(self) -> None:
        """
        Best-effort: for each CALLS edge whose target is a raw function name
        (not a full symbol ID), try to resolve it to a known symbol ID.
        """
        # Build name → [symbol_id] index for fast lookup
        name_index: dict[str, list[str]] = {}
        for sym_id in self._graph.nodes():
            sym = self._graph.get_symbol(sym_id)
            if sym:
                name_index.setdefault(sym.name, []).append(sym_id)

        # Walk all CALLS edges and try to resolve raw names
        g = self._graph._g  # access underlying DiGraph
        to_add: list[tuple[str, str]] = []
        for u, v, data in list(g.edges(data=True)):
            if data.get("kind") != EdgeKind.CALLS.value:
                continue
            if "::" in v or "/" in v:
                continue  # already a resolved ID
            candidates = name_index.get(v, [])
            if len(candidates) == 1:
                to_add.append((u, candidates[0]))

        for from_id, to_id in to_add:
            self._graph.add_edge(from_id, to_id, EdgeKind.CALLS)
