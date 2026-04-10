"""
graph/symbol_graph.py — NetworkX-backed dependency graph for code symbols.

Nodes = Symbol IDs (strings)
Node attributes = serialised Symbol fields
Edges = directed relationships (calls, imports, defines, inherits, uses)

The graph is the in-memory index that makes cross-file context selection O(log n)
instead of O(n_files × file_size).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterator, Optional

import networkx as nx

from src.core.code_map.symbols import EdgeKind, Symbol

logger = logging.getLogger(__name__)


class SymbolGraph:
    """
    Thread-unsafe (lock managed by CodeMapper) directed graph of code symbols.

    Provides:
    - O(1) node lookup by symbol ID
    - O(1) reverse lookup: file path → all symbol IDs in that file
    - BFS/DFS traversal for context selection
    - Provenance: each node tracks which file it came from
    """

    def __init__(self) -> None:
        self._g: nx.DiGraph = nx.DiGraph()
        # file_path (posix) → set of symbol IDs
        self._file_index: dict[str, set[str]] = {}

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_symbol(self, sym: Symbol) -> None:
        """
        Add or update a symbol node.  If the node already exists, its
        attributes are merged (the new symbol wins for non-empty fields).
        """
        attrs = self._sym_to_attrs(sym)
        if self._g.has_node(sym.id):
            # Merge: keep existing attrs, overwrite with new non-empty values
            existing = dict(self._g.nodes[sym.id])
            for k, v in attrs.items():
                if v or not existing.get(k):
                    existing[k] = v
            self._g.nodes[sym.id].update(existing)
        else:
            self._g.add_node(sym.id, **attrs)

        # Update file index
        file_key = Path(sym.file_path).as_posix()
        self._file_index.setdefault(file_key, set()).add(sym.id)

        # Auto-wire edges from sym.calls and sym.imports
        for callee in sym.calls:
            self._g.add_edge(sym.id, callee, kind=EdgeKind.CALLS.value)
        for imported in sym.imports:
            self._g.add_edge(sym.id, imported, kind=EdgeKind.IMPORTS.value)

    def add_edge(self, from_id: str, to_id: str, kind: EdgeKind) -> None:
        """Add a directed edge between two symbol IDs."""
        if from_id and to_id:
            self._g.add_edge(from_id, to_id, kind=kind.value)

    def remove_symbol(self, symbol_id: str) -> None:
        """Remove a node and all its incident edges."""
        if self._g.has_node(symbol_id):
            # Remove from file index
            file_key = self._g.nodes[symbol_id].get("file_path", "")
            if file_key and file_key in self._file_index:
                self._file_index[file_key].discard(symbol_id)
            self._g.remove_node(symbol_id)

    def remove_file(self, file_path: str) -> int:
        """Remove all symbols belonging to *file_path*. Returns count removed."""
        key = Path(file_path).as_posix()
        ids = list(self._file_index.pop(key, set()))
        for sid in ids:
            if self._g.has_node(sid):
                self._g.remove_node(sid)
        return len(ids)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def has_node(self, symbol_id: str) -> bool:
        return self._g.has_node(symbol_id)

    def get_symbol(self, symbol_id: str) -> Optional[Symbol]:
        """Reconstruct a Symbol from a graph node's attributes, or None."""
        if not self._g.has_node(symbol_id):
            return None
        return self._attrs_to_sym(symbol_id, dict(self._g.nodes[symbol_id]))

    def nodes(self) -> Iterator[str]:
        """Yield all symbol IDs in the graph."""
        return iter(self._g.nodes)

    def symbols_in_file(self, file_path: str) -> list[Symbol]:
        """Return all symbols belonging to *file_path*."""
        key = Path(file_path).as_posix()
        ids = self._file_index.get(key, set())
        return [s for s in (self.get_symbol(sid) for sid in ids) if s is not None]

    def neighbours(self, symbol_id: str, edge_kind: Optional[EdgeKind] = None) -> list[str]:
        """
        Return direct neighbours (successors + predecessors) of *symbol_id*.

        If *edge_kind* is given, only edges of that type are followed.
        """
        if not self._g.has_node(symbol_id):
            return []
        result: set[str] = set()
        for u, v, data in self._g.edges(symbol_id, data=True):
            if edge_kind is None or data.get("kind") == edge_kind.value:
                result.add(v)
        for u, v, data in self._g.in_edges(symbol_id, data=True):
            if edge_kind is None or data.get("kind") == edge_kind.value:
                result.add(u)
        result.discard(symbol_id)
        return list(result)

    def bfs_subgraph(
        self,
        start_id: str,
        max_depth: int = 2,
        max_nodes: int = 30,
    ) -> list[str]:
        """
        Breadth-first expansion from *start_id* up to *max_depth* hops.

        Returns a list of symbol IDs in BFS order (anchor first).
        """
        if not self._g.has_node(start_id):
            return []

        visited: list[str] = []
        seen: set[str] = set()
        queue: list[tuple[str, int]] = [(start_id, 0)]

        while queue and len(visited) < max_nodes:
            node_id, depth = queue.pop(0)
            if node_id in seen:
                continue
            seen.add(node_id)
            visited.append(node_id)
            if depth < max_depth:
                for nb in self.neighbours(node_id):
                    if nb not in seen and self._g.has_node(nb):
                        queue.append((nb, depth + 1))

        return visited

    def all_symbols(self) -> list[Symbol]:
        """Return every symbol in the graph."""
        return [s for s in (self.get_symbol(nid) for nid in self._g.nodes) if s is not None]

    def search_by_name(self, name: str, case_sensitive: bool = False) -> list[Symbol]:
        """Return symbols whose name contains *name*."""
        cmp = name if case_sensitive else name.lower()
        results = []
        for sym in self.all_symbols():
            candidate = sym.name if case_sensitive else sym.name.lower()
            if cmp in candidate:
                results.append(sym)
        return results

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def node_count(self) -> int:
        return self._g.number_of_nodes()

    def edge_count(self) -> int:
        return self._g.number_of_edges()

    def file_count(self) -> int:
        return len(self._file_index)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sym_to_attrs(sym: Symbol) -> dict[str, Any]:
        return {
            "name":        sym.name,
            "kind":        sym.kind.value,
            "language":    sym.language,
            "file_path":   Path(sym.file_path).as_posix(),
            "start_line":  sym.start_line,
            "end_line":    sym.end_line,
            "source":      sym.source,
            "signature":   sym.signature,
            "docstring":   sym.docstring,
            "tags":        sym.tags,
        }

    @staticmethod
    def _attrs_to_sym(symbol_id: str, attrs: dict[str, Any]) -> Optional[Symbol]:
        from src.core.code_map.symbols import SymbolKind
        try:
            return Symbol(
                id=symbol_id,
                name=attrs.get("name", symbol_id.split("::")[-1]),
                kind=SymbolKind(attrs.get("kind", "unknown")),
                language=attrs.get("language", "unknown"),
                file_path=attrs.get("file_path", ""),
                start_line=attrs.get("start_line", 1),
                end_line=attrs.get("end_line", 1),
                source=attrs.get("source", ""),
                signature=attrs.get("signature", ""),
                docstring=attrs.get("docstring", ""),
                tags=attrs.get("tags", []),
            )
        except Exception as exc:
            logger.debug("Cannot reconstruct Symbol %s: %s", symbol_id, exc)
            return None
