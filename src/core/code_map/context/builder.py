"""
context/builder.py — Assembles selected symbols into a ContextBundle.

The ContextBundle is what actually gets serialised into the Bedrock prompt.
"""

from __future__ import annotations

from pathlib import Path

from src.core.code_map.symbols import ContextBundle, Symbol


class ContextBuilder:
    """Converts a list of ranked Symbol objects into a ContextBundle."""

    def build(
        self,
        query: str,
        anchor_id: str,
        symbols: list[Symbol],
        depth: int = 2,
    ) -> ContextBundle:
        """
        Build a ContextBundle from a pre-selected list of symbols.

        Parameters
        ----------
        query:
            Original user query (stored for traceability).
        anchor_id:
            Primary symbol ID the selection is centred on.
        symbols:
            Ordered list of symbols (anchor first).
        depth:
            BFS depth used during selection.
        """
        languages = sorted({sym.language for sym in symbols if sym.language})
        return ContextBundle(
            query=query,
            anchor_id=anchor_id,
            symbols=symbols,
            depth=depth,
            languages=languages,
        )

    def build_empty(self, query: str, reason: str = "") -> ContextBundle:
        """Return an empty ContextBundle (e.g. when file not found)."""
        return ContextBundle(
            query=query,
            anchor_id="",
            symbols=[],
            depth=0,
            languages=[],
        )
