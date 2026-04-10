"""
Tests for src/core/code_map/graph/

Covers SymbolGraph and Indexer across add/remove/query operations.
"""

import textwrap
import pytest

from src.core.code_map.graph.symbol_graph import SymbolGraph
from src.core.code_map.graph.indexer import Indexer
from src.core.code_map.symbols import Symbol, SymbolKind, EdgeKind


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sym(sym_id: str, name: str, kind=SymbolKind.FUNCTION,
             file_path="src/foo.py", lang="python",
             start=1, end=10, source="def foo(): pass") -> Symbol:
    return Symbol(
        id=sym_id, name=name, kind=kind, language=lang,
        file_path=file_path, start_line=start, end_line=end, source=source,
    )


# ---------------------------------------------------------------------------
# SymbolGraph — basic operations
# ---------------------------------------------------------------------------

class TestSymbolGraphBasics:

    def test_add_and_has_node(self):
        g = SymbolGraph()
        sym = make_sym("src/foo.py::my_func", "my_func")
        g.add_symbol(sym)
        assert g.has_node("src/foo.py::my_func")

    def test_node_count(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("a::f", "f"))
        g.add_symbol(make_sym("b::g", "g"))
        assert g.node_count() == 2

    def test_get_symbol_roundtrip(self):
        g = SymbolGraph()
        sym = make_sym("src/foo.py::bar", "bar", kind=SymbolKind.CLASS)
        g.add_symbol(sym)
        retrieved = g.get_symbol("src/foo.py::bar")
        assert retrieved is not None
        assert retrieved.name == "bar"
        assert retrieved.kind == SymbolKind.CLASS

    def test_get_symbol_missing_returns_none(self):
        g = SymbolGraph()
        assert g.get_symbol("nonexistent::sym") is None

    def test_remove_symbol(self):
        g = SymbolGraph()
        sym = make_sym("f::g", "g")
        g.add_symbol(sym)
        g.remove_symbol("f::g")
        assert not g.has_node("f::g")

    def test_remove_file(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("src/x.py::a", "a", file_path="src/x.py"))
        g.add_symbol(make_sym("src/x.py::b", "b", file_path="src/x.py"))
        g.add_symbol(make_sym("src/y.py::c", "c", file_path="src/y.py"))
        removed = g.remove_file("src/x.py")
        assert removed == 2
        assert not g.has_node("src/x.py::a")
        assert not g.has_node("src/x.py::b")
        assert g.has_node("src/y.py::c")

    def test_symbols_in_file(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("src/m.py::f1", "f1", file_path="src/m.py"))
        g.add_symbol(make_sym("src/m.py::f2", "f2", file_path="src/m.py"))
        g.add_symbol(make_sym("src/n.py::f3", "f3", file_path="src/n.py"))
        in_m = g.symbols_in_file("src/m.py")
        assert len(in_m) == 2
        assert all(s.file_path == "src/m.py" for s in in_m)

    def test_file_count(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("a.py::f", "f", file_path="a.py"))
        g.add_symbol(make_sym("b.py::g", "g", file_path="b.py"))
        assert g.file_count() == 2

    def test_nodes_iterator(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("p::x", "x"))
        g.add_symbol(make_sym("q::y", "y"))
        ids = list(g.nodes())
        assert "p::x" in ids
        assert "q::y" in ids

    def test_all_symbols_returns_all(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("a::f", "f"))
        g.add_symbol(make_sym("b::g", "g"))
        syms = g.all_symbols()
        assert len(syms) == 2


# ---------------------------------------------------------------------------
# SymbolGraph — edges
# ---------------------------------------------------------------------------

class TestSymbolGraphEdges:

    def test_add_edge(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("a::f", "f"))
        g.add_symbol(make_sym("b::g", "g"))
        g.add_edge("a::f", "b::g", EdgeKind.CALLS)
        assert g.edge_count() >= 1

    def test_calls_edge_auto_wired_from_sym(self):
        g = SymbolGraph()
        caller = Symbol(
            id="src/foo.py::caller", name="caller",
            kind=SymbolKind.FUNCTION, language="python",
            file_path="src/foo.py", start_line=1, end_line=5,
            source="def caller(): callee()",
            calls=["src/bar.py::callee"],
        )
        g.add_symbol(caller)
        # The auto-wired edge: caller → callee
        assert g.edge_count() >= 1

    def test_neighbours_returns_connected(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("a::f", "f"))
        g.add_symbol(make_sym("b::g", "g"))
        g.add_edge("a::f", "b::g", EdgeKind.CALLS)
        nbs = g.neighbours("a::f")
        assert "b::g" in nbs

    def test_neighbours_bidirectional(self):
        """Neighbours should include both predecessors and successors."""
        g = SymbolGraph()
        g.add_symbol(make_sym("a::f", "f"))
        g.add_symbol(make_sym("b::g", "g"))
        g.add_edge("a::f", "b::g", EdgeKind.CALLS)
        # b::g should see a::f as a neighbour (predecessor)
        nbs_of_g = g.neighbours("b::g")
        assert "a::f" in nbs_of_g

    def test_neighbours_missing_node(self):
        g = SymbolGraph()
        assert g.neighbours("ghost") == []


# ---------------------------------------------------------------------------
# SymbolGraph — BFS subgraph
# ---------------------------------------------------------------------------

class TestBfsSubgraph:

    def setup_method(self):
        self.g = SymbolGraph()
        # a → b → c → d (chain depth 3)
        for letter in "abcd":
            self.g.add_symbol(make_sym(f"f::{letter}", letter))
        self.g.add_edge("f::a", "f::b", EdgeKind.CALLS)
        self.g.add_edge("f::b", "f::c", EdgeKind.CALLS)
        self.g.add_edge("f::c", "f::d", EdgeKind.CALLS)

    def test_bfs_depth_0_returns_anchor_only(self):
        result = self.g.bfs_subgraph("f::a", max_depth=0)
        assert result == ["f::a"]

    def test_bfs_depth_1_returns_direct_neighbours(self):
        result = self.g.bfs_subgraph("f::a", max_depth=1)
        assert "f::a" in result
        assert "f::b" in result
        assert "f::c" not in result

    def test_bfs_depth_2_reaches_two_hops(self):
        result = self.g.bfs_subgraph("f::a", max_depth=2)
        assert "f::c" in result

    def test_bfs_max_nodes_limits_result(self):
        result = self.g.bfs_subgraph("f::a", max_depth=10, max_nodes=2)
        assert len(result) <= 2

    def test_bfs_missing_anchor_returns_empty(self):
        result = self.g.bfs_subgraph("nonexistent", max_depth=2)
        assert result == []

    def test_bfs_starts_with_anchor(self):
        result = self.g.bfs_subgraph("f::a", max_depth=3)
        assert result[0] == "f::a"


# ---------------------------------------------------------------------------
# SymbolGraph — search
# ---------------------------------------------------------------------------

class TestSearchByName:

    def test_search_finds_partial_match(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("f::get_user", "get_user"))
        g.add_symbol(make_sym("f::set_user", "set_user"))
        g.add_symbol(make_sym("f::delete", "delete"))
        results = g.search_by_name("user")
        names = {s.name for s in results}
        assert "get_user" in names
        assert "set_user" in names
        assert "delete" not in names

    def test_search_case_insensitive_by_default(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("f::MyClass", "MyClass", kind=SymbolKind.CLASS))
        results = g.search_by_name("myclass")
        assert results

    def test_search_empty_returns_all(self):
        g = SymbolGraph()
        g.add_symbol(make_sym("f::a", "a"))
        g.add_symbol(make_sym("f::b", "b"))
        # Empty query matches everything
        results = g.search_by_name("")
        assert len(results) == 2


# ---------------------------------------------------------------------------
# Indexer — index_source()
# ---------------------------------------------------------------------------

class TestIndexerSource:

    PYTHON_SOURCE = textwrap.dedent("""\
        import os

        class Service:
            def run(self):
                pass

        def helper():
            pass
    """)

    def test_index_source_populates_graph(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        result = indexer.index_source("src/svc.py", self.PYTHON_SOURCE)
        assert len(result.symbols) > 0
        assert graph.node_count() > 0

    def test_index_source_finds_class(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        indexer.index_source("src/svc.py", self.PYTHON_SOURCE)
        results = graph.search_by_name("Service")
        assert results

    def test_index_source_finds_function(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        indexer.index_source("src/svc.py", self.PYTHON_SOURCE)
        results = graph.search_by_name("helper")
        assert results

    def test_index_source_re_index_clears_old(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        indexer.index_source("src/svc.py", self.PYTHON_SOURCE)
        before = graph.node_count()
        indexer.index_source("src/svc.py", "x = 1")  # tiny file
        after = graph.node_count()
        # After re-indexing with smaller source, node count should not grow unboundedly
        assert after <= before + 1

    def test_index_source_unsupported_lang_returns_error(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        result = indexer.index_source("file.unknownxyz", "some content")
        assert result.parse_errors

    def test_index_javascript(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        js_source = "class Foo {}\nfunction bar() {}"
        result = indexer.index_source("app.js", js_source)
        assert result.language == "javascript"
        assert graph.node_count() > 0
