"""
ModelEntry — Pydantic v2 schema for a single Bedrock model.

Every entry in the ModelRegistry is validated against this schema so that
malformed data (missing fields, wrong types, whitespace in IDs) is caught
at registration time rather than silently causing runtime failures.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Reusable annotated types
# ---------------------------------------------------------------------------

NonEmptyStr = Annotated[str, Field(min_length=1)]


# ---------------------------------------------------------------------------
# ModelEntry
# ---------------------------------------------------------------------------

class ModelEntry(BaseModel):
    """Represents a single Bedrock model with its routing and billing metadata."""

    model_config = {"frozen": True}  # immutable after creation

    alias: NonEmptyStr
    """Human-readable key used inside the application (e.g. 'claude-sonnet-global')."""

    aws_id: NonEmptyStr
    """Full AWS model or inference-profile ID (e.g. 'global.anthropic.claude-sonnet-4-…')."""

    provider: NonEmptyStr
    """Model provider in lowercase (e.g. 'anthropic', 'amazon', 'meta', 'mistral')."""

    family: NonEmptyStr
    """Model family in lowercase (e.g. 'claude', 'nova', 'llama', 'mistral')."""

    region_scope: str = "native"
    """
    Routing scope:
        'global'  — global cross-region inference profile
        'us'      — US cross-region inference profile
        'eu'      — EU cross-region inference profile
        'native'  — single-region native model ID
    """

    supports_tools: bool = True
    """
    Whether the model supports Bedrock Converse tool-use (required for /agent mode).
    Claude, Nova, Llama 3.1+, Mistral Large, and Cohere Command-R all support tools.
    """

    input_cost_per_1k: float = Field(default=0.001, ge=0.0)
    """Cost in USD per 1,000 input tokens."""

    output_cost_per_1k: float = Field(default=0.005, ge=0.0)
    """Cost in USD per 1,000 output tokens."""

    tags: list[str] = Field(default_factory=list)
    """Optional labels for filtering (e.g. ['fast', 'cheap', 'vision'])."""

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("alias", "aws_id", mode="before")
    @classmethod
    def strip_and_lower_ids(cls, value: str) -> str:
        """Strip surrounding whitespace; reject empty strings after stripping."""
        if not isinstance(value, str):
            raise ValueError("Must be a string.")
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value must not be blank after stripping whitespace.")
        return stripped

    @field_validator("provider", "family", mode="before")
    @classmethod
    def lowercase_identifiers(cls, value: str) -> str:
        """Normalise provider and family to lowercase for consistent comparisons."""
        if not isinstance(value, str):
            raise ValueError("Must be a string.")
        result = value.strip().lower()
        if not result:
            raise ValueError("Value must not be blank.")
        return result

    @field_validator("region_scope")
    @classmethod
    def validate_region_scope(cls, value: str) -> str:
        allowed = {"global", "us", "eu", "native"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(f"region_scope must be one of {allowed}, got '{value}'.")
        return normalised

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def matches(self, query: str) -> int:
        """
        Return a match-quality score (higher is better) for a free-text query.

        Scoring:
            4 — exact alias match
            3 — exact aws_id match
            2 — alias or aws_id *starts with* query
            1 — query is a substring of alias, aws_id, provider, or family
            0 — no match or blank query
        """
        q = query.strip().lower()
        if not q:
            return 0
        if self.alias.lower() == q:
            return 4
        if self.aws_id.lower() == q:
            return 3
        if self.alias.lower().startswith(q) or self.aws_id.lower().startswith(q):
            return 2
        haystack = f"{self.alias} {self.aws_id} {self.provider} {self.family}".lower()
        if q in haystack:
            return 1
        return 0
