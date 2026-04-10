"""
context/selector.py — BFS-based context selection engine.

Given an anchor symbol ID and a natural-language query, selects the minimum
set of graph nodes that are:
  1. Reachable from the anchor within *depth* hops
  2. Scored by relevance to the query (keyword overlap)
  3. Within the *token_budget*

This is the core of the token-reduction machinery: instead of sending 5,000
raw file tokens to Bedrock, we send 200–800 tokens of the most relevant symbols.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from src.core.code_map.graph.symbol_graph import SymbolGraph
from src.core.code_map.symbols import Symbol

logger = logging.getLogger(__name__)


@dataclass
class _ScoredSymbol:
    symbol: Symbol
    score: float = 0.0
    depth: int = 0


class ContextSelector:
    """
    Selects the most relevant subset of symbols for a given query.

    Algorithm:
    1. BFS from *anchor_id* up to *depth* hops in the SymbolGraph
    2. Score each reachable symbol by keyword overlap with *query*
    3. Always include the anchor (even if score is 0)
    4. Sort by (depth ASC, score DESC)
    5. Greedily add symbols until *token_budget* is exhausted
    """

    def __init__(self, graph: SymbolGraph) -> None:
        self._graph = graph

    def select(
        self,
        anchor_id: str,
        query: str,
        depth: int = 2,
        token_budget: int = 2000,
    ) -> list[Symbol]:
        """
        Return an ordered list of symbols for the prompt context.

        The anchor is always first. Remaining symbols are ordered by
        relevance score (descending) then BFS depth (ascending).
        """
        if not self._graph.has_node(anchor_id):
            # If anchor doesn't exist, try a fuzzy name search instead
            return self._fallback_search(query, token_budget)

        bfs_ids = self._graph.bfs_subgraph(anchor_id, max_depth=depth, max_nodes=50)
        if not bfs_ids:
            return []

        query_tokens = self._tokenise_query(query)
        scored: list[_ScoredSymbol] = []

        for i, sym_id in enumerate(bfs_ids):
            sym = self._graph.get_symbol(sym_id)
            if sym is None:
                continue
            depth_val = 0 if sym_id == anchor_id else (1 if i <= 3 else 2)
            score = self._score(sym, query_tokens, is_anchor=(sym_id == anchor_id))
            scored.append(_ScoredSymbol(symbol=sym, score=score, depth=depth_val))

        # Sort: anchor first, then by depth asc, score desc
        scored.sort(key=lambda s: (0 if s.depth == 0 else 1, s.depth, -s.score))

        # Greedily fill token budget
        selected: list[Symbol] = []
        used_tokens = 0
        for item in scored:
            est = item.symbol.token_estimate()
            if used_tokens + est > token_budget and selected:
                break  # budget exhausted (always include at least anchor)
            selected.append(item.symbol)
            used_tokens += est

        return selected

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score(self, sym: Symbol, query_tokens: set[str], is_anchor: bool) -> float:
        """
        Score a symbol 0–1 by relevance to the query tokens.

        Signals (weighted):
        - Anchor bonus                  (+10)
        - Name contains query token     (+3 each)
        - Docstring contains token      (+1 each)
        - Source contains token         (+0.5 each)
        - Tags contain token            (+2 each)
        """
        if not query_tokens:
            return 1.0 if is_anchor else 0.0

        score = 10.0 if is_anchor else 0.0

        name_lower = sym.name.lower()
        doc_lower  = sym.docstring.lower()
        src_lower  = sym.source.lower()[:500]  # cap for performance
        tag_lower  = " ".join(sym.tags).lower()
        sig_lower  = sym.signature.lower()

        for token in query_tokens:
            if token in name_lower or token in sig_lower:
                score += 3.0
            if token in doc_lower:
                score += 1.0
            if token in src_lower:
                score += 0.5
            if token in tag_lower:
                score += 2.0

        # Normalise to avoid extreme values
        return min(score, 20.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenise_query(query: str) -> set[str]:
        """Extract meaningful lowercase tokens from the query string."""
        tokens = re.findall(r"[a-z][a-z0-9_]*", query.lower())
        # Filter stop words
        _STOP = {
            "the", "a", "an", "is", "are", "was", "be", "to", "of", "and",
            "in", "for", "on", "with", "this", "that", "how", "does", "do",
            "what", "why", "where", "when", "which", "it", "its",
        }
        return {t for t in tokens if len(t) > 2 and t not in _STOP}

    def _fallback_search(self, query: str, token_budget: int) -> list[Symbol]:
        """When anchor is not in graph, do a keyword search across all symbols."""
        query_tokens = self._tokenise_query(query)
        if not query_tokens:
            return []
        results = []
        for token in query_tokens:
            results.extend(self._graph.search_by_name(token))
        # Deduplicate and cap
        seen: set[str] = set()
        unique: list[Symbol] = []
        used = 0
        for sym in results:
            if sym.id not in seen:
                seen.add(sym.id)
                est = sym.token_estimate()
                if used + est > token_budget and unique:
                    break
                unique.append(sym)
                used += est
        return unique
