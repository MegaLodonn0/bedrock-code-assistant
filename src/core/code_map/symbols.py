"""
symbols.py — Pydantic v2 schemas for the Code Map System.

All data that flows through the pipeline is validated against these models
so that malformed parse results are caught early rather than silently causing
wrong context bundles to be sent to Bedrock.
"""

from __future__ import annotations

import hashlib
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, computed_field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SymbolKind(str, Enum):
    """Coarse-grained category of a code symbol."""
    FUNCTION  = "function"
    METHOD    = "method"
    CLASS     = "class"
    MODULE    = "module"
    IMPORT    = "import"
    VARIABLE  = "variable"
    CONSTANT  = "constant"
    UNKNOWN   = "unknown"


class EdgeKind(str, Enum):
    """Type of relationship between two symbols in the graph."""
    CALLS     = "calls"      # symbol A calls / invokes symbol B
    IMPORTS   = "imports"    # file A imports file/module B
    DEFINES   = "defines"    # class A defines method B
    INHERITS  = "inherits"   # class A inherits from class B
    USES      = "uses"       # symbol A uses identifier B


# ---------------------------------------------------------------------------
# Symbol
# ---------------------------------------------------------------------------


class Symbol(BaseModel):
    """
    Represents a single named entity extracted from a source file.

    The ``id`` field is the primary key used in the dependency graph.
    Its format:  ``<relative_file_path>::<outer_class>::<name>``
    (outer_class is omitted for top-level symbols).
    """

    model_config = {"frozen": True}

    id: str
    """Unique identifier: 'src/foo.py::MyClass::my_method'."""

    name: str
    """Short identifier name as it appears in the source."""

    kind: SymbolKind = SymbolKind.UNKNOWN

    language: str
    """Lowercase language name: 'python', 'javascript', 'go', …"""

    file_path: str
    """Absolute or project-relative path of the containing file."""

    start_line: int = Field(ge=1, description="1-indexed start line (inclusive).")
    end_line: int   = Field(ge=1, description="1-indexed end line (inclusive).")

    source: str = ""
    """Actual source lines of this symbol (may be truncated for very large bodies)."""

    signature: str = ""
    """Function/class signature without the body, e.g. 'def foo(x: int) -> str'."""

    docstring: str = ""
    """Docstring or leading comment if present."""

    calls: list[str] = Field(default_factory=list)
    """IDs (or raw names) of symbols this symbol directly calls / invokes."""

    imports: list[str] = Field(default_factory=list)
    """Module paths or file paths that this symbol (or its file) imports."""

    tags: list[str] = Field(default_factory=list)
    """Optional labels, e.g. ['public', 'async', 'exported']."""

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("language", mode="before")
    @classmethod
    def normalise_language(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("source", mode="before")
    @classmethod
    def truncate_large_source(cls, v: str) -> str:
        """Cap source at 200 lines to keep graph memory bounded."""
        lines = v.splitlines()
        if len(lines) > 200:
            lines = lines[:200] + [f"… ({len(lines) - 200} more lines)"]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @computed_field  # type: ignore[prop-decorator]
    @property
    def line_count(self) -> int:
        return max(0, self.end_line - self.start_line + 1)

    def token_estimate(self) -> int:
        """Rough estimate of tokens this symbol would consume in a prompt."""
        text = f"{self.signature}\n{self.docstring}\n{self.source}"
        return max(1, len(text) // 4)

    def display_header(self) -> str:
        return (
            f"[{self.kind.value.upper()}: {self.id} | {self.language} "
            f"| lines {self.start_line}–{self.end_line}]"
        )


# ---------------------------------------------------------------------------
# ParseResult — output of a single file parse
# ---------------------------------------------------------------------------


class ParseResult(BaseModel):
    """The set of symbols extracted from one file."""

    file_path: str
    language: str
    symbols: list[Symbol] = Field(default_factory=list)
    parse_errors: list[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def file_hash(self) -> str:
        """SHA-256 digest of the file path (not content) for cache keying."""
        return hashlib.sha256(self.file_path.encode()).hexdigest()[:16]

    @property
    def success(self) -> bool:
        return not self.parse_errors


# ---------------------------------------------------------------------------
# ContextBundle — output of the context selection engine
# ---------------------------------------------------------------------------


class ContextBundle(BaseModel):
    """
    A minimal, structured collection of symbols assembled for a specific query.

    This is what gets serialised into the Bedrock prompt instead of raw file
    content.  It contains only the symbols that are directly relevant to the
    user's question, reducing token usage by 80–95%.
    """

    query: str
    """The original user query that drove context selection."""

    anchor_id: str
    """Primary symbol ID the query is centred on."""

    symbols: list[Symbol] = Field(default_factory=list)
    """Selected symbols, ordered by relevance (most relevant first)."""

    depth: int = 2
    """BFS depth used when expanding the dependency graph."""

    languages: list[str] = Field(default_factory=list)
    """Distinct languages present in this bundle."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_tokens_estimate(self) -> int:
        return sum(s.token_estimate() for s in self.symbols)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def symbol_count(self) -> int:
        return len(self.symbols)

    def to_prompt(self) -> str:
        """
        Serialise the bundle into a compact, structured string suitable for
        injection into a Bedrock prompt.

        Format:
            [CONTEXT: file::Symbol | lang | lines N–M]
            <signature>
            <docstring>
            <source>

            [USES: ...]
            ...
        """
        if not self.symbols:
            return "(no relevant code context found)"

        parts: list[str] = []
        anchor_done = False

        for sym in self.symbols:
            header = sym.display_header()
            body_parts: list[str] = []

            if sym.signature:
                body_parts.append(sym.signature)
            if sym.docstring:
                body_parts.append(f'    """{sym.docstring}"""')
            if sym.source and sym.source != sym.signature:
                body_parts.append(sym.source)

            body = "\n".join(body_parts) if body_parts else "(body not available)"
            label = "ANCHOR" if not anchor_done else "CONTEXT"
            anchor_done = True
            parts.append(f"[{label}: {sym.id} | {sym.language} | lines {sym.start_line}–{sym.end_line}]\n{body}")

        header_line = (
            f"# Code Context for: {self.query}\n"
            f"# Symbols: {self.symbol_count} | "
            f"Est. tokens: {self.total_tokens_estimate} | "
            f"Languages: {', '.join(self.languages)}\n"
        )
        return header_line + "\n\n".join(parts)

    def summary(self) -> str:
        """One-line summary for logging."""
        return (
            f"ContextBundle({self.symbol_count} symbols, "
            f"~{self.total_tokens_estimate} tokens, "
            f"depth={self.depth})"
        )
