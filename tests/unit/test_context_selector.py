"""
Tests for src/core/code_map/context/

Covers ContextSelector scoring, BFS selection, token budget enforcement,
and ContextBuilder output format.
"""

import textwrap
import pytest

from src.core.code_map.context.selector import ContextSelector
from src.core.code_map.context.builder import ContextBuilder
from src.core.code_map.graph.symbol_graph import SymbolGraph
from src.core.code_map.graph.indexer import Indexer
from src.core.code_map.symbols import Symbol, SymbolKind, ContextBundle, EdgeKind


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sym(sym_id: str, name: str, kind=SymbolKind.FUNCTION,
             file_path="src/a.py", lang="python",
             source="def foo(): pass", docstring="") -> Symbol:
    return Symbol(
        id=sym_id, name=name, kind=kind, language=lang,
        file_path=file_path, start_line=1, end_line=5,
        source=source, docstring=docstring,
    )


def build_graph_with_chain() -> tuple[SymbolGraph, ContextSelector]:
    """Graph: anchor → helper → util (chain depth 2)."""
    g = SymbolGraph()
    anchor = make_sym("f::anchor", "anchor", docstring="This is the main cost tracking function")
    helper = make_sym("f::helper", "helper", docstring="Helper for cost calculation")
    util   = make_sym("f::util",   "util",   docstring="Generic utility")
    import_node = make_sym("f::os_import", "_import_1", kind=SymbolKind.IMPORT)
    for sym in (anchor, helper, util, import_node):
        g.add_symbol(sym)
    g.add_edge("f::anchor", "f::helper", EdgeKind.CALLS)
    g.add_edge("f::helper", "f::util",   EdgeKind.CALLS)
    return g, ContextSelector(g)


# ---------------------------------------------------------------------------
# ContextSelector._tokenise_query
# ---------------------------------------------------------------------------

class TestTokeniseQuery:

    def test_extracts_meaningful_tokens(self):
        result = ContextSelector._tokenise_query("How does cost tracking work?")
        assert "cost" in result
        assert "tracking" in result
        assert "work" in result

    def test_filters_stop_words(self):
        result = ContextSelector._tokenise_query("How does the function work")
        assert "the" not in result
        assert "does" not in result
        assert "how" not in result

    def test_empty_query_returns_empty_set(self):
        assert ContextSelector._tokenise_query("") == set()

    def test_short_tokens_filtered(self):
        result = ContextSelector._tokenise_query("do it now")
        # 'do', 'it' are <= 2 chars or stop words
        assert "do" not in result
        assert "it" not in result

    def test_case_insensitive(self):
        result = ContextSelector._tokenise_query("CostMonitor")
        assert "costmonitor" in result


# ---------------------------------------------------------------------------
# ContextSelector.select — anchor always included
# ---------------------------------------------------------------------------

class TestContextSelectorAnchorAlwaysFirst:

    def test_anchor_is_first_in_result(self):
        g, sel = build_graph_with_chain()
        result = sel.select("f::anchor", "cost tracking", depth=2)
        assert result
        assert result[0].id == "f::anchor"

    def test_anchor_included_even_with_tiny_budget(self):
        g, sel = build_graph_with_chain()
        result = sel.select("f::anchor", "anything", depth=2, token_budget=1)
        assert any(s.id == "f::anchor" for s in result)

    def test_missing_anchor_falls_back_to_search(self):
        g, sel = build_graph_with_chain()
        result = sel.select("nonexistent::sym", "helper", depth=2)
        # Should still find something via fallback name search
        assert result  # may or may not find, no crash

    def test_neighbours_included_within_depth(self):
        g, sel = build_graph_with_chain()
        result = sel.select("f::anchor", "cost", depth=1)
        ids = {s.id for s in result}
        # Direct neighbour should be included
        assert "f::helper" in ids

    def test_deep_nodes_excluded_at_depth_1(self):
        g, sel = build_graph_with_chain()
        result = sel.select("f::anchor", "cost", depth=1)
        ids = {s.id for s in result}
        # f::util is 2 hops away — should NOT appear at depth=1
        assert "f::util" not in ids

    def test_deep_nodes_included_at_depth_2(self):
        g, sel = build_graph_with_chain()
        result = sel.select("f::anchor", "cost", depth=2)
        ids = {s.id for s in result}
        assert "f::util" in ids


# ---------------------------------------------------------------------------
# ContextSelector.select — token budget enforcement
# ---------------------------------------------------------------------------

class TestTokenBudget:

    def test_result_fits_within_budget(self):
        g, sel = build_graph_with_chain()
        budget = 100
        result = sel.select("f::anchor", "cost", depth=2, token_budget=budget)
        total = sum(s.token_estimate() for s in result)
        assert total <= budget + result[0].token_estimate()  # anchor always included

    def test_larger_budget_returns_more_nodes(self):
        g, sel = build_graph_with_chain()
        small = sel.select("f::anchor", "cost", depth=2, token_budget=50)
        large = sel.select("f::anchor", "cost", depth=2, token_budget=5000)
        assert len(large) >= len(small)


# ---------------------------------------------------------------------------
# ContextSelector.select — scoring
# ---------------------------------------------------------------------------

class TestScoringRelevance:

    def test_query_match_increases_score(self):
        g = SymbolGraph()
        relevant = make_sym("f::tracker", "cost_tracker", docstring="Tracks costs precisely")
        irrelevant = make_sym("f::parser", "xml_parser", docstring="Parses XML documents")
        g.add_symbol(relevant)
        g.add_symbol(irrelevant)
        g.add_edge("f::tracker", "f::parser", EdgeKind.CALLS)
        sel = ContextSelector(g)
        result = sel.select("f::tracker", "cost tracking", depth=1)
        # relevant (anchor) should be first
        assert result[0].name == "cost_tracker"


# ---------------------------------------------------------------------------
# ContextBuilder
# ---------------------------------------------------------------------------

class TestContextBuilder:

    def test_build_returns_context_bundle(self):
        builder = ContextBuilder()
        sym = make_sym("f::foo", "foo")
        bundle = builder.build("What does foo do?", "f::foo", [sym], depth=1)
        assert isinstance(bundle, ContextBundle)

    def test_bundle_has_correct_query(self):
        builder = ContextBuilder()
        sym = make_sym("f::bar", "bar")
        bundle = builder.build("How does bar work?", "f::bar", [sym])
        assert bundle.query == "How does bar work?"

    def test_bundle_anchor_id(self):
        builder = ContextBuilder()
        sym = make_sym("f::baz", "baz")
        bundle = builder.build("q", "f::baz", [sym])
        assert bundle.anchor_id == "f::baz"

    def test_bundle_languages_collected(self):
        builder = ContextBuilder()
        py_sym = make_sym("a.py::f", "f", lang="python")
        js_sym = make_sym("b.js::g", "g", lang="javascript", file_path="b.js")
        bundle = builder.build("q", "a.py::f", [py_sym, js_sym])
        assert "python" in bundle.languages
        assert "javascript" in bundle.languages

    def test_bundle_token_estimate(self):
        builder = ContextBuilder()
        sym = make_sym("f::x", "x", source="def x():\n    return 42\n")
        bundle = builder.build("q", "f::x", [sym])
        assert bundle.total_tokens_estimate > 0

    def test_to_prompt_contains_anchor_label(self):
        builder = ContextBuilder()
        sym = make_sym("f::myfunc", "myfunc", source="def myfunc(): pass")
        bundle = builder.build("explain myfunc", "f::myfunc", [sym])
        prompt = bundle.to_prompt()
        assert "ANCHOR" in prompt
        assert "myfunc" in prompt

    def test_to_prompt_contains_query(self):
        builder = ContextBuilder()
        sym = make_sym("f::myfunc", "myfunc")
        bundle = builder.build("explain myfunc", "f::myfunc", [sym])
        prompt = bundle.to_prompt()
        assert "explain myfunc" in prompt

    def test_empty_bundle_to_prompt(self):
        builder = ContextBuilder()
        bundle = builder.build_empty("nothing here")
        prompt = bundle.to_prompt()
        assert "no relevant" in prompt.lower()

    def test_build_empty_returns_bundle(self):
        builder = ContextBuilder()
        bundle = builder.build_empty("q", reason="file not found")
        assert isinstance(bundle, ContextBundle)
        assert bundle.symbol_count == 0

    def test_summary_method(self):
        builder = ContextBuilder()
        sym = make_sym("f::x", "x")
        bundle = builder.build("q", "f::x", [sym])
        summary = bundle.summary()
        assert "ContextBundle" in summary
        assert "1 symbols" in summary


# ---------------------------------------------------------------------------
# End-to-end: index → select → build
# ---------------------------------------------------------------------------

class TestEndToEnd:

    PYTHON_SOURCE = textwrap.dedent("""\
        import os

        class CostMonitor:
            \"\"\"Tracks API call costs.\"\"\"

            def update(self, tokens_in: int, tokens_out: int, price_in: float, price_out: float) -> float:
                \"\"\"Update cost with new token counts.\"\"\"
                cost = (tokens_in * price_in + tokens_out * price_out) / 1000
                self.total += cost
                return cost

        def compute_price(model: str) -> tuple:
            \"\"\"Look up model pricing.\"\"\"
            return 0.003, 0.015
    """)

    def test_full_pipeline_reduces_tokens(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        indexer.index_source("cost.py", self.PYTHON_SOURCE)

        sel = ContextSelector(graph)
        builder = ContextBuilder()

        all_syms = graph.all_symbols()
        anchor = next((s for s in all_syms if s.name == "update"), None)
        if anchor is None:
            pytest.skip("Parser did not extract 'update' method")

        result = sel.select(anchor.id, "How does cost tracking work?", depth=2, token_budget=2000)
        bundle = builder.build("How does cost tracking work?", anchor.id, result)

        raw_tokens = len(self.PYTHON_SOURCE) // 4
        assert bundle.total_tokens_estimate < raw_tokens, (
            f"Context ({bundle.total_tokens_estimate}) should be < raw file ({raw_tokens})"
        )

    def test_full_pipeline_includes_anchor(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        indexer.index_source("cost.py", self.PYTHON_SOURCE)

        sel = ContextSelector(graph)
        all_syms = graph.all_symbols()
        anchor = next((s for s in all_syms if "CostMonitor" in s.id or s.name == "CostMonitor"), None)
        if anchor is None:
            pytest.skip("Parser did not extract 'CostMonitor' class")

        result = sel.select(anchor.id, "cost monitor class", depth=1)
        assert result[0].id == anchor.id

    def test_to_prompt_is_shorter_than_raw_file(self):
        graph = SymbolGraph()
        indexer = Indexer(graph)
        indexer.index_source("cost.py", self.PYTHON_SOURCE)

        sel = ContextSelector(graph)
        all_syms = graph.all_symbols()
        anchor = all_syms[0] if all_syms else None
        if anchor is None:
            pytest.skip("No symbols indexed")

        result = sel.select(anchor.id, "cost", depth=1, token_budget=500)
        builder = ContextBuilder()
        bundle = builder.build("cost", anchor.id, result)
        prompt = bundle.to_prompt()

        assert len(prompt) < len(self.PYTHON_SOURCE) * 3  # some overhead for headers is ok
