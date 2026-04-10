"""
ModelRegistry — bidirectional model mapping with Pydantic validation.

The registry is the single runtime source of truth for:
    alias  ↔  AWS model ID   (bidict — O(1) in both directions)
    alias  →  ModelEntry     (full metadata: provider, pricing, tool support)

Usage
-----
    from src.core.mapping.registry import get_registry

    reg = get_registry()
    aws_id  = reg.resolve("claude-sonnet-global")
    alias   = reg.reverse_lookup("global.anthropic.claude-sonnet-4-…")
    matches = reg.fuzzy_search("sonnet")
    cost_in, cost_out = reg.get_pricing("claude-sonnet-global")
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

from bidict import bidict, KeyDuplicationError, ValueDuplicationError

from src.core.mapping.exceptions import (
    DuplicateAliasError,
    DuplicateAwsIdError,
    UnknownModelError,
)
from src.core.mapping.model_entry import ModelEntry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Providers / families whose models support Bedrock Converse tool-use
# ---------------------------------------------------------------------------
_TOOL_CAPABLE_FAMILIES: frozenset[str] = frozenset(
    {"claude", "nova", "llama", "mistral", "command-r"}
)
_TOOL_CAPABLE_PROVIDERS: frozenset[str] = frozenset(
    {"anthropic", "amazon", "meta", "mistral", "cohere"}
)


# ---------------------------------------------------------------------------
# Default pricing fallback (used for raw AWS IDs without a loaded ModelEntry)
# ---------------------------------------------------------------------------
_DEFAULT_INPUT_COST: float = 0.001   # USD per 1K tokens
_DEFAULT_OUTPUT_COST: float = 0.005  # USD per 1K tokens


class ModelRegistry:
    """
    Thread-safe registry mapping model aliases to AWS model IDs and metadata.

    The internal bidict enforces:
        - Each alias maps to exactly one AWS ID
        - Each AWS ID maps to exactly one alias
        raising typed errors on violations instead of silently overwriting.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # bidict[alias, aws_id]
        self._mapping: bidict[str, str] = bidict()
        # alias → full ModelEntry (not all entries have one — raw AWS IDs don't)
        self._entries: dict[str, ModelEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, entry: ModelEntry, *, overwrite: bool = False) -> None:
        """
        Register a ModelEntry in the registry.

        Parameters
        ----------
        entry:
            Validated ModelEntry to add.
        overwrite:
            If True, silently replace an existing entry with the same alias.
            Default is False (raises DuplicateAliasError).

        Raises
        ------
        DuplicateAliasError
            If *alias* already exists and overwrite=False.
        DuplicateAwsIdError
            If *aws_id* already maps to a *different* alias (regardless of overwrite).
        """
        with self._lock:
            existing_alias_for_id = self._mapping.inverse.get(entry.aws_id)
            if existing_alias_for_id and existing_alias_for_id != entry.alias:
                raise DuplicateAwsIdError(entry.aws_id, existing_alias_for_id)

            if entry.alias in self._mapping:
                if not overwrite:
                    raise DuplicateAliasError(entry.alias)
                # Remove the old mapping before replacing
                del self._mapping[entry.alias]

            self._mapping[entry.alias] = entry.aws_id
            self._entries[entry.alias] = entry
            logger.debug("Registered model: %s → %s", entry.alias, entry.aws_id)

    def register_raw(self, alias: str, aws_id: str, *, overwrite: bool = False) -> None:
        """
        Register a raw alias→aws_id pair without full ModelEntry metadata.

        Used when AWS returns model IDs that are not in the catalog yet.
        A minimal ModelEntry is constructed from the ID itself.
        """
        provider, family = _infer_provider_family(aws_id)
        entry = ModelEntry(
            alias=alias,
            aws_id=aws_id,
            provider=provider,
            family=family,
            region_scope=_infer_region_scope(aws_id),
            supports_tools=_infer_tool_support(provider, family),
        )
        self.register(entry, overwrite=overwrite)

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self, key: str) -> str:
        """
        Resolve *key* to an AWS model ID.

        Accepts either an alias (e.g. 'claude-sonnet-global') or a raw AWS ID
        (returned as-is if it is already registered as an ID).

        Raises
        ------
        UnknownModelError
            If *key* is neither a known alias nor a registered AWS ID.
        """
        with self._lock:
            # 1. Exact alias match
            if key in self._mapping:
                return self._mapping[key]
            # 2. Already an AWS ID
            if key in self._mapping.inverse:
                return key
            raise UnknownModelError(key)

    def resolve_safe(self, key: str) -> str:
        """
        Like resolve() but returns *key* unchanged instead of raising when not found.
        Useful when the caller wants to pass raw IDs through transparently.
        """
        try:
            return self.resolve(key)
        except UnknownModelError:
            return key

    def reverse_lookup(self, aws_id: str) -> Optional[str]:
        """Return the alias for a given AWS ID, or None if not registered."""
        with self._lock:
            return self._mapping.inverse.get(aws_id)

    # ------------------------------------------------------------------
    # Metadata queries
    # ------------------------------------------------------------------

    def get_entry(self, alias: str) -> Optional[ModelEntry]:
        """Return the full ModelEntry for an alias, or None."""
        with self._lock:
            return self._entries.get(alias)

    def supports_agent(self, key: str) -> bool:
        """
        Return True if the model identified by *key* supports Bedrock Converse
        tool-use (required for /agent mode).

        Checks the ModelEntry first; falls back to heuristic analysis of the
        AWS ID string for raw IDs that are not in the catalog.
        """
        with self._lock:
            # Resolve alias if needed
            alias = self._mapping.inverse.get(key, key)
            entry = self._entries.get(alias)
            if entry is not None:
                return entry.supports_tools
            # Fallback heuristic for unregistered raw IDs
            lower_id = key.lower()
            return any(
                hint in lower_id
                for hint in _TOOL_CAPABLE_FAMILIES | {"llama3-1", "llama3-2", "llama3-3"}
            )

    def get_pricing(self, key: str) -> tuple[float, float]:
        """
        Return (input_cost_per_1k, output_cost_per_1k) for *key*.

        Falls back to the global defaults if the model is not in the catalog.
        """
        with self._lock:
            alias = self._mapping.inverse.get(key, key)
            entry = self._entries.get(alias)
            if entry is not None:
                return entry.input_cost_per_1k, entry.output_cost_per_1k
            return _DEFAULT_INPUT_COST, _DEFAULT_OUTPUT_COST

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def fuzzy_search(self, query: str, limit: int = 10) -> list[ModelEntry]:
        """
        Search across alias, aws_id, provider, and family.

        Returns a list of ModelEntry objects sorted by match quality
        (highest first), limited to *limit* results.
        """
        with self._lock:
            scored = [
                (entry.matches(query), entry)
                for entry in self._entries.values()
                if entry.matches(query) > 0
            ]
            scored.sort(key=lambda t: t[0], reverse=True)
            return [entry for _, entry in scored[:limit]]

    def suggest(self, bad_key: str, limit: int = 3) -> list[str]:
        """
        Return a list of alias suggestions for an unknown *bad_key*.
        Used to build "did you mean?" messages.
        """
        matches = self.fuzzy_search(bad_key, limit=limit)
        return [e.alias for e in matches]

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def load_defaults(self) -> None:
        """
        Seed the registry from the built-in models catalog.

        Called once at application startup. Idempotent — safe to call
        multiple times (existing entries are skipped, not replaced).
        """
        from src.core.mapping.models_catalog import MODELS

        loaded = 0
        for entry in MODELS:
            try:
                self.register(entry)
                loaded += 1
            except (DuplicateAliasError, DuplicateAwsIdError) as exc:
                logger.warning("Skipping catalog entry: %s", exc)
        logger.info("ModelRegistry: loaded %d models from catalog.", loaded)

    def merge_from_aws(self, raw_ids: list[str]) -> None:
        """
        Register AWS model IDs that were returned by the Bedrock API but are
        not yet in the catalog. They receive auto-generated aliases equal to
        their raw ID (so they are still resolvable).

        Already-registered IDs are silently ignored.
        """
        with self._lock:
            new_count = 0
            for raw_id in raw_ids:
                if raw_id in self._mapping.inverse:
                    continue  # already mapped via catalog
                try:
                    # Use the raw ID as both alias and value — a unique pass-through mapping
                    self.register_raw(raw_id, raw_id)
                    new_count += 1
                except (DuplicateAliasError, DuplicateAwsIdError):
                    pass
            if new_count:
                logger.debug("Merged %d new raw AWS model IDs into registry.", new_count)

    # ------------------------------------------------------------------
    # Backwards-compatible export
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        """
        Return a plain alias → aws_id dict.

        Keeps compatibility with code that previously iterated
        settings.bedrock_models directly.
        """
        with self._lock:
            return dict(self._mapping)

    def grouped_by_provider(self) -> dict[str, list[dict[str, str]]]:
        """
        Return entries grouped by provider, each item containing 'id' and 'name'.
        Compatible with the format expected by BedrockHardened.get_all_grouped_models().
        """
        with self._lock:
            groups: dict[str, list[dict[str, str]]] = {}
            for entry in self._entries.values():
                provider_key = entry.provider.capitalize()
                groups.setdefault(provider_key, [])
                groups[provider_key].append(
                    {"id": entry.aws_id, "name": entry.alias}
                )
            return groups

    def __len__(self) -> int:
        with self._lock:
            return len(self._mapping)

    def __contains__(self, key: str) -> bool:
        """Support 'alias in registry' and 'aws_id in registry' checks."""
        with self._lock:
            return key in self._mapping or key in self._mapping.inverse


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _infer_provider_family(aws_id: str) -> tuple[str, str]:
    """
    Infer (provider, family) from a raw AWS model ID string.
    Examples:
        'global.anthropic.claude-sonnet-…' → ('anthropic', 'claude')
        'us.amazon.nova-pro-v1:0'           → ('amazon', 'nova')
        'us.meta.llama3-1-…'                → ('meta', 'llama')
    """
    lower = aws_id.lower()
    provider = "unknown"
    family = "unknown"

    provider_hints = {
        "anthropic": "anthropic",
        "amazon": "amazon",
        "meta": "meta",
        "mistral": "mistral",
        "cohere": "cohere",
        "deepseek": "deepseek",
        "twelvelabs": "twelvelabs",
    }
    family_hints = {
        "claude": "claude",
        "nova": "nova",
        "llama": "llama",
        "mistral": "mistral",
        "command": "command-r",
        "deepseek": "deepseek",
    }

    for hint, name in provider_hints.items():
        if hint in lower:
            provider = name
            break
    for hint, name in family_hints.items():
        if hint in lower:
            family = name
            break

    return provider, family


def _infer_region_scope(aws_id: str) -> str:
    """Infer region_scope from AWS ID prefix."""
    lower = aws_id.lower()
    if lower.startswith("global."):
        return "global"
    if lower.startswith("us."):
        return "us"
    if lower.startswith("eu."):
        return "eu"
    return "native"


def _infer_tool_support(provider: str, family: str) -> bool:
    """Infer tool support from provider and family."""
    return (
        provider in _TOOL_CAPABLE_PROVIDERS
        or family in _TOOL_CAPABLE_FAMILIES
    )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_registry: Optional[ModelRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> ModelRegistry:
    """
    Return the process-global ModelRegistry, creating and seeding it on
    first call (thread-safe).
    """
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = ModelRegistry()
                _registry.load_defaults()
    return _registry


def reset_registry() -> None:
    """
    Reset the singleton (for use in tests only).
    Never call this in production code.
    """
    global _registry
    with _registry_lock:
        _registry = None
