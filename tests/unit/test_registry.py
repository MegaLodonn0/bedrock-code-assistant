"""
Unit tests for src/core/mapping/registry.py

Covers:
- register() happy path and duplicate errors
- resolve() by alias and by raw AWS ID
- resolve_safe() transparent pass-through
- reverse_lookup()
- supports_agent() from catalog + heuristic
- get_pricing() from catalog + default fallback
- fuzzy_search() ranking and limit
- suggest() hint generation
- to_dict() backwards compatibility
- merge_from_aws() unknown IDs
- load_defaults() — no duplicates, all entries valid
- Thread safety (basic)
- __contains__ operator
"""

import threading
import pytest

from src.core.mapping.exceptions import DuplicateAliasError, DuplicateAwsIdError, UnknownModelError
from src.core.mapping.model_entry import ModelEntry
from src.core.mapping.registry import ModelRegistry, get_registry, reset_registry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_entry(alias: str, aws_id: str, **kw) -> ModelEntry:
    defaults = dict(
        provider="testprovider",
        family="testfamily",
        region_scope="native",
        supports_tools=True,
        input_cost_per_1k=0.001,
        output_cost_per_1k=0.005,
    )
    defaults.update(kw)
    return ModelEntry(alias=alias, aws_id=aws_id, **defaults)


@pytest.fixture()
def reg():
    """Fresh, empty ModelRegistry for each test."""
    return ModelRegistry()


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the global singleton before and after each test."""
    reset_registry()
    yield
    reset_registry()


# ---------------------------------------------------------------------------
# register()
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_happy_path(self, reg):
        entry = make_entry("my-model", "us.test.v1:0")
        reg.register(entry)
        assert "my-model" in reg

    def test_register_duplicate_alias_raises(self, reg):
        entry = make_entry("my-model", "us.test.v1:0")
        reg.register(entry)
        with pytest.raises(DuplicateAliasError):
            reg.register(make_entry("my-model", "us.other.v1:0"))

    def test_register_duplicate_aws_id_different_alias_raises(self, reg):
        reg.register(make_entry("alias-a", "us.shared.v1:0"))
        with pytest.raises(DuplicateAwsIdError):
            reg.register(make_entry("alias-b", "us.shared.v1:0"))

    def test_register_overwrite_replaces_entry(self, reg):
        reg.register(make_entry("model", "us.old.v1:0"))
        reg.register(make_entry("model", "us.new.v1:0"), overwrite=True)
        assert reg.resolve("model") == "us.new.v1:0"

    def test_register_same_alias_same_id_overwrite(self, reg):
        """Overwriting with the same alias+id should succeed silently."""
        entry = make_entry("model", "us.test.v1:0")
        reg.register(entry)
        reg.register(entry, overwrite=True)
        assert reg.resolve("model") == "us.test.v1:0"


# ---------------------------------------------------------------------------
# resolve()
# ---------------------------------------------------------------------------

class TestResolve:
    def test_resolve_by_alias(self, reg):
        reg.register(make_entry("nova-lite", "amazon.nova-lite-v1:0"))
        assert reg.resolve("nova-lite") == "amazon.nova-lite-v1:0"

    def test_resolve_by_raw_aws_id(self, reg):
        reg.register(make_entry("nova-lite", "amazon.nova-lite-v1:0"))
        # raw AWS ID should pass through
        assert reg.resolve("amazon.nova-lite-v1:0") == "amazon.nova-lite-v1:0"

    def test_resolve_unknown_raises(self, reg):
        with pytest.raises(UnknownModelError):
            reg.resolve("nonexistent-model")

    def test_resolve_safe_returns_key_on_unknown(self, reg):
        result = reg.resolve_safe("some-raw-id")
        assert result == "some-raw-id"

    def test_resolve_safe_resolves_known_alias(self, reg):
        reg.register(make_entry("my-model", "us.test.v1:0"))
        assert reg.resolve_safe("my-model") == "us.test.v1:0"


# ---------------------------------------------------------------------------
# reverse_lookup()
# ---------------------------------------------------------------------------

class TestReverseLookup:
    def test_reverse_lookup_returns_alias(self, reg):
        reg.register(make_entry("my-alias", "us.test.v1:0"))
        assert reg.reverse_lookup("us.test.v1:0") == "my-alias"

    def test_reverse_lookup_unknown_returns_none(self, reg):
        assert reg.reverse_lookup("nonexistent.v1:0") is None


# ---------------------------------------------------------------------------
# supports_agent()
# ---------------------------------------------------------------------------

class TestSupportsAgent:
    def test_supports_tools_true_from_entry(self, reg):
        reg.register(make_entry("m", "id", supports_tools=True))
        assert reg.supports_agent("m") is True

    def test_supports_tools_false_from_entry(self, reg):
        reg.register(make_entry("m", "id", supports_tools=False))
        assert reg.supports_agent("m") is False

    def test_heuristic_claude_raw_id(self, reg):
        # Raw ID not in registry — heuristic kicks in
        assert reg.supports_agent("us.anthropic.claude-haiku-v1:0") is True

    def test_heuristic_nova_raw_id(self, reg):
        assert reg.supports_agent("amazon.nova-lite-v1:0") is True

    def test_heuristic_llama_raw_id(self, reg):
        assert reg.supports_agent("us.meta.llama3-1-70b-instruct-v1:0") is True


# ---------------------------------------------------------------------------
# get_pricing()
# ---------------------------------------------------------------------------

class TestGetPricing:
    def test_returns_catalog_pricing(self, reg):
        reg.register(make_entry("m", "id", input_cost_per_1k=0.003, output_cost_per_1k=0.015))
        in_c, out_c = reg.get_pricing("m")
        assert in_c == pytest.approx(0.003)
        assert out_c == pytest.approx(0.015)

    def test_returns_defaults_for_unknown(self, reg):
        in_c, out_c = reg.get_pricing("totally-unknown")
        assert in_c == 0.001
        assert out_c == 0.005

    def test_returns_pricing_by_raw_aws_id(self, reg):
        reg.register(make_entry("alias", "us.test.v1:0", input_cost_per_1k=0.002))
        in_c, _ = reg.get_pricing("us.test.v1:0")
        assert in_c == pytest.approx(0.002)


# ---------------------------------------------------------------------------
# fuzzy_search() and suggest()
# ---------------------------------------------------------------------------

class TestFuzzySearch:
    def setup_method(self):
        self.reg = ModelRegistry()
        self.reg.register(ModelEntry(
            alias="claude-sonnet-global",
            aws_id="global.anthropic.claude-sonnet-4-v1:0",
            provider="anthropic", family="claude", region_scope="global",
        ))
        self.reg.register(ModelEntry(
            alias="claude-haiku-global",
            aws_id="global.anthropic.claude-haiku-4-v1:0",
            provider="anthropic", family="claude", region_scope="global",
        ))
        self.reg.register(ModelEntry(
            alias="nova-lite",
            aws_id="amazon.nova-lite-v1:0",
            provider="amazon", family="nova", region_scope="native",
        ))

    def test_exact_alias_first(self):
        results = self.reg.fuzzy_search("claude-sonnet-global")
        assert results[0].alias == "claude-sonnet-global"

    def test_provider_returns_multiple(self):
        results = self.reg.fuzzy_search("anthropic")
        aliases = [e.alias for e in results]
        assert "claude-sonnet-global" in aliases
        assert "claude-haiku-global" in aliases

    def test_no_match_returns_empty(self):
        results = self.reg.fuzzy_search("zzznomatch")
        assert results == []

    def test_limit_is_respected(self):
        results = self.reg.fuzzy_search("claude", limit=1)
        assert len(results) <= 1

    def test_suggest_returns_aliases(self):
        hints = self.reg.suggest("claude", limit=2)
        assert len(hints) > 0
        assert any("claude" in h for h in hints)


# ---------------------------------------------------------------------------
# to_dict()
# ---------------------------------------------------------------------------

class TestToDict:
    def test_returns_plain_dict(self, reg):
        reg.register(make_entry("a", "us.a.v1:0"))
        reg.register(make_entry("b", "us.b.v1:0"))
        d = reg.to_dict()
        assert isinstance(d, dict)
        assert d["a"] == "us.a.v1:0"
        assert d["b"] == "us.b.v1:0"

    def test_modifying_returned_dict_does_not_affect_registry(self, reg):
        reg.register(make_entry("a", "us.a.v1:0"))
        d = reg.to_dict()
        d["injected"] = "us.injected.v1:0"
        assert "injected" not in reg


# ---------------------------------------------------------------------------
# merge_from_aws()
# ---------------------------------------------------------------------------

class TestMergeFromAws:
    def test_new_raw_ids_are_registered(self, reg):
        reg.merge_from_aws(["us.new.model-v1:0", "us.other.model-v1:0"])
        assert "us.new.model-v1:0" in reg
        assert "us.other.model-v1:0" in reg

    def test_already_registered_ids_are_skipped(self, reg):
        reg.register(make_entry("existing", "us.existing.v1:0"))
        # This should not raise even though the ID is already mapped
        reg.merge_from_aws(["us.existing.v1:0"])
        # Alias should remain the original catalog alias
        assert reg.reverse_lookup("us.existing.v1:0") == "existing"

    def test_empty_list_does_not_raise(self, reg):
        reg.merge_from_aws([])


# ---------------------------------------------------------------------------
# load_defaults()
# ---------------------------------------------------------------------------

class TestLoadDefaults:
    def test_load_defaults_populates_registry(self):
        reg = ModelRegistry()
        reg.load_defaults()
        assert len(reg) > 0

    def test_load_defaults_no_duplicates(self):
        """Calling load_defaults twice should not raise DuplicateAliasError."""
        reg = ModelRegistry()
        reg.load_defaults()
        reg.load_defaults()  # idempotent

    def test_nova_lite_has_single_alias(self):
        """The original bug: nova-lite was duplicated. Verify it appears once."""
        reg = ModelRegistry()
        reg.load_defaults()
        all_aliases = list(reg.to_dict().keys())
        assert all_aliases.count("nova-lite") == 1

    def test_all_catalog_entries_resolve(self):
        reg = ModelRegistry()
        reg.load_defaults()
        for alias, aws_id in reg.to_dict().items():
            resolved = reg.resolve(alias)
            assert resolved == aws_id

    def test_default_model_alias_is_registered(self):
        from src.core.mapping.models_catalog import DEFAULT_MODEL_ALIAS
        reg = ModelRegistry()
        reg.load_defaults()
        assert DEFAULT_MODEL_ALIAS in reg


# ---------------------------------------------------------------------------
# __contains__
# ---------------------------------------------------------------------------

class TestContains:
    def test_alias_in_registry(self, reg):
        reg.register(make_entry("m", "us.m.v1:0"))
        assert "m" in reg

    def test_aws_id_in_registry(self, reg):
        reg.register(make_entry("m", "us.m.v1:0"))
        assert "us.m.v1:0" in reg

    def test_missing_key_not_in_registry(self, reg):
        assert "ghost" not in reg


# ---------------------------------------------------------------------------
# grouped_by_provider()
# ---------------------------------------------------------------------------

class TestGroupedByProvider:
    def test_groups_by_capitalized_provider(self, reg):
        reg.register(make_entry("m1", "id1", provider="anthropic"))
        reg.register(make_entry("m2", "id2", provider="amazon"))
        groups = reg.grouped_by_provider()
        assert "Anthropic" in groups
        assert "Amazon" in groups


# ---------------------------------------------------------------------------
# Thread safety (smoke test)
# ---------------------------------------------------------------------------

class TestThreadSafety:
    def test_concurrent_register_does_not_corrupt(self):
        reg = ModelRegistry()
        errors = []

        def register_batch(start: int):
            for i in range(start, start + 20):
                try:
                    reg.register(make_entry(f"model-{i}", f"us.test{i}.v1:0"))
                except DuplicateAliasError:
                    pass
                except Exception as exc:
                    errors.append(exc)

        threads = [threading.Thread(target=register_batch, args=(i * 20,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

class TestSingleton:
    def test_get_registry_returns_same_instance(self):
        a = get_registry()
        b = get_registry()
        assert a is b

    def test_reset_registry_creates_fresh_instance(self):
        a = get_registry()
        reset_registry()
        b = get_registry()
        assert a is not b

    def test_singleton_is_pre_loaded(self):
        """get_registry() should return a pre-seeded registry."""
        reg = get_registry()
        assert len(reg) > 0
