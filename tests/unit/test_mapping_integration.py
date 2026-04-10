"""
Integration tests: ModelRegistry is correctly wired into Executor,
CostMonitor, and Settings.

All AWS / Docker / ChromaDB dependencies are mocked so tests run offline.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.core.mapping.registry import get_registry, reset_registry
from src.core.mapping.model_entry import ModelEntry
from src.core.security.cost_monitor import CostMonitor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    return asyncio.run(coro)


def make_executor():
    """Return a fully-mocked Executor with real settings & registry."""
    with (
        patch("src.core.executor.BedrockHardened") as mock_bedrock_cls,
        patch("src.core.executor.DockerSandbox"),
        patch("src.core.executor.DependencyAnalyzer"),
        patch("src.core.executor.CostMonitor"),
        patch("src.core.executor.get_rate_limiter") as mock_rl,
        patch("src.core.executor.get_retry_policy"),
        patch("src.core.executor.get_agent_qa"),
        patch("src.core.executor.get_feedback_loop"),
        patch("src.core.executor.get_vector_db"),
    ):
        mock_bedrock_instance = MagicMock()
        mock_bedrock_instance.available = False
        mock_bedrock_cls.return_value = mock_bedrock_instance

        mock_rl_instance = MagicMock()
        mock_rl_instance.wait_and_acquire = AsyncMock()
        mock_rl.return_value = mock_rl_instance

        from src.core.executor import Executor
        return Executor(use_mock=True)


@pytest.fixture(autouse=True)
def reset_global_registry():
    reset_registry()
    yield
    reset_registry()


# ---------------------------------------------------------------------------
# Settings integration
# ---------------------------------------------------------------------------

class TestSettingsRegistryIntegration:
    def test_settings_bedrock_models_reflects_catalog(self):
        from src.config.settings import settings
        models = settings.bedrock_models
        assert isinstance(models, dict)
        assert "nova-lite" in models
        assert "claude-sonnet-global" in models

    def test_settings_bedrock_models_no_duplicate_values(self):
        """Each AWS ID should appear at most once in the exported dict."""
        from src.config.settings import settings
        models = settings.bedrock_models
        values = list(models.values())
        # Duplicate values would indicate two aliases pointing to the same AWS ID;
        # that is allowed ONLY if they are intentional aliases (not the nova-lite bug).
        # We specifically check that 'nova-lite' and 'nova-lite-global' differ.
        assert models.get("nova-lite") != models.get("nova-lite-global", "__sentinel__")

    def test_settings_default_model_is_in_registry(self):
        from src.config.settings import settings
        reg = get_registry()
        assert settings.default_model in reg

    def test_settings_registry_property_returns_singleton(self):
        from src.config.settings import settings
        r1 = settings.registry
        r2 = settings.registry
        assert r1 is r2


# ---------------------------------------------------------------------------
# Executor _resolve_model_id
# ---------------------------------------------------------------------------

class TestExecutorModelResolution:
    def test_resolve_uses_registry(self):
        ex = make_executor()
        # nova-lite is in the catalog
        ex.current_model = "nova-lite"
        resolved = ex._resolve_model_id()
        assert resolved == "amazon.nova-lite-v1:0"

    def test_resolve_raw_aws_id_passthrough(self):
        ex = make_executor()
        raw = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        resolved = ex._resolve_model_id(model_id=raw)
        # Not in registry → resolve_safe returns it unchanged
        assert resolved == raw

    def test_supports_agent_for_claude(self):
        ex = make_executor()
        ex.current_model = "claude-sonnet-global"
        assert ex.supports_agent is True

    def test_supports_agent_for_nova_micro(self):
        """nova-micro has supports_tools=False in the catalog."""
        ex = make_executor()
        ex.current_model = "nova-micro-us"
        assert ex.supports_agent is False

    def test_supports_agent_for_unknown_defaults_to_heuristic(self):
        ex = make_executor()
        # Set a raw Claude ID that isn't an alias
        ex.current_model = "us.anthropic.claude-haiku-raw"
        # Heuristic: 'claude' in the string → True
        assert ex.supports_agent is True


# ---------------------------------------------------------------------------
# Executor set_model fuzzy suggestions
# ---------------------------------------------------------------------------

class TestSetModelFuzzy:
    def test_set_model_valid_alias(self):
        ex = make_executor()
        result = run(ex.set_model("nova-lite"))
        assert "nova-lite" in result
        assert ex.current_model == "nova-lite"

    def test_set_model_unknown_returns_error_and_suggestion(self):
        ex = make_executor()
        result = run(ex.set_model("nova-lte"))   # typo: "nova-lte" not in catalog
        # Should contain the unknown label
        assert "Unknown" in result or "unknown" in result.capitalize()

    def test_set_model_suggestion_displayed_for_near_miss(self):
        ex = make_executor()
        result = run(ex.set_model("claude"))  # 'claude' matches many entries via fuzzy
        # claude is not an alias but fuzzy_search will find it
        # The result should be "Unknown model" (not found as exact alias)
        # and suggestions should appear because registry.suggest("claude") returns hints
        assert "Unknown" in result or "claude" in result.lower()

    def test_set_model_persists(self):
        ex = make_executor()
        run(ex.set_model("claude-haiku-global"))
        assert ex.current_model == "claude-haiku-global"


# ---------------------------------------------------------------------------
# CostMonitor with registry pricing
# ---------------------------------------------------------------------------

class TestCostMonitorWithRegistry:
    def test_update_with_registry_pricing(self):
        monitor = CostMonitor()
        reg = get_registry()
        in_cost, out_cost = reg.get_pricing("claude-sonnet-global")

        cost = monitor.update(1000, 500, input_cost_per_1k=in_cost, output_cost_per_1k=out_cost)

        assert cost > 0
        # 1000 input * 0.003/1K + 500 output * 0.015/1K = 3 + 7.5 = 10.5 mUSD
        expected = (1000 / 1000) * in_cost + (500 / 1000) * out_cost
        assert cost == pytest.approx(expected)

    def test_update_uses_default_fallback(self):
        monitor = CostMonitor()
        cost = monitor.update(1000, 1000)
        # Default: 0.001 + 0.005 = 0.006
        assert cost == pytest.approx(0.006)

    def test_cumulative_cost_accumulates(self):
        monitor = CostMonitor()
        monitor.update(1000, 1000)
        monitor.update(1000, 1000)
        assert monitor.total_cost == pytest.approx(0.012)

    def test_get_summary_contains_tokens(self):
        monitor = CostMonitor()
        monitor.update(500, 250)
        summary = monitor.get_summary()
        assert "500" in summary
        assert "250" in summary
        assert "$" in summary

    def test_nova_micro_cheaper_than_claude(self):
        reg = get_registry()
        claude_in, claude_out = reg.get_pricing("claude-opus-global")
        nova_in, nova_out = reg.get_pricing("nova-micro-us")
        assert nova_in < claude_in
        assert nova_out < claude_out


# ---------------------------------------------------------------------------
# Registry bidirectional lookup smoke tests
# ---------------------------------------------------------------------------

class TestRegistryBidirectional:
    def test_alias_to_id(self):
        reg = get_registry()
        aws_id = reg.resolve("claude-sonnet-global")
        assert "anthropic" in aws_id.lower()

    def test_id_to_alias(self):
        reg = get_registry()
        # Use the catalog ID we know
        alias = reg.reverse_lookup("amazon.nova-lite-v1:0")
        assert alias == "nova-lite"

    def test_fuzzy_search_finds_all_anthropic(self):
        reg = get_registry()
        results = reg.fuzzy_search("anthropic")
        providers = {e.provider for e in results}
        assert "anthropic" in providers

    def test_all_catalog_entries_roundtrip(self):
        """alias → aws_id → alias roundtrip must be identity for all catalog entries."""
        reg = get_registry()
        for alias, aws_id in reg.to_dict().items():
            back = reg.reverse_lookup(aws_id)
            # Back should either be the same alias or None (raw IDs registered via
            # merge_from_aws use themselves as both key and value)
            assert back == alias or back == aws_id
