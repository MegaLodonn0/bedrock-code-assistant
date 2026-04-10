"""
Unit tests for src/core/mapping/model_entry.py

Covers:
- Valid ModelEntry construction
- Field validators (whitespace stripping, blank rejection, lowercase normalisation)
- region_scope validation
- cost field constraints (non-negative)
- matches() scoring
- Immutability (frozen model)
"""

import pytest
from pydantic import ValidationError

from src.core.mapping.model_entry import ModelEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def valid_entry(**overrides) -> ModelEntry:
    defaults = dict(
        alias="test-model",
        aws_id="us.test.model-v1:0",
        provider="testprovider",
        family="testfamily",
        region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.001,
        output_cost_per_1k=0.005,
    )
    defaults.update(overrides)
    return ModelEntry(**defaults)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestModelEntryConstruction:
    def test_minimal_valid_entry(self):
        entry = valid_entry()
        assert entry.alias == "test-model"
        assert entry.aws_id == "us.test.model-v1:0"
        assert entry.provider == "testprovider"
        assert entry.family == "testfamily"

    def test_tags_default_to_empty_list(self):
        entry = valid_entry()
        assert entry.tags == []

    def test_supports_tools_default_true(self):
        entry = valid_entry()
        assert entry.supports_tools is True

    def test_region_scope_default_native(self):
        entry = ModelEntry(
            alias="x",
            aws_id="x.test.v1:0",
            provider="p",
            family="f",
        )
        assert entry.region_scope == "native"

    def test_cost_defaults(self):
        entry = ModelEntry(
            alias="x",
            aws_id="x.test.v1:0",
            provider="p",
            family="f",
        )
        assert entry.input_cost_per_1k == 0.001
        assert entry.output_cost_per_1k == 0.005

    def test_tags_are_stored(self):
        entry = valid_entry(tags=["fast", "cheap"])
        assert "fast" in entry.tags
        assert "cheap" in entry.tags


# ---------------------------------------------------------------------------
# Validator: alias and aws_id stripping
# ---------------------------------------------------------------------------

class TestAliasAwsIdValidator:
    def test_whitespace_is_stripped_from_alias(self):
        entry = valid_entry(alias="  trimmed  ")
        assert entry.alias == "trimmed"

    def test_whitespace_is_stripped_from_aws_id(self):
        entry = valid_entry(aws_id="  us.test.v1:0  ")
        assert entry.aws_id == "us.test.v1:0"

    def test_blank_alias_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(alias="   ")

    def test_blank_aws_id_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(aws_id="")

    def test_non_string_alias_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(alias=123)


# ---------------------------------------------------------------------------
# Validator: provider and family normalisation
# ---------------------------------------------------------------------------

class TestProviderFamilyValidator:
    def test_provider_is_lowercased(self):
        entry = valid_entry(provider="Anthropic")
        assert entry.provider == "anthropic"

    def test_family_is_lowercased(self):
        entry = valid_entry(family="CLAUDE")
        assert entry.family == "claude"

    def test_blank_provider_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(provider="")

    def test_blank_family_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(family="  ")


# ---------------------------------------------------------------------------
# Validator: region_scope
# ---------------------------------------------------------------------------

class TestRegionScopeValidator:
    @pytest.mark.parametrize("scope", ["global", "us", "eu", "native"])
    def test_valid_scopes_accepted(self, scope):
        entry = valid_entry(region_scope=scope)
        assert entry.region_scope == scope

    def test_invalid_scope_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(region_scope="apac")

    def test_scope_is_lowercased(self):
        entry = valid_entry(region_scope="US")
        assert entry.region_scope == "us"


# ---------------------------------------------------------------------------
# Validator: cost fields
# ---------------------------------------------------------------------------

class TestCostFieldValidator:
    def test_zero_cost_is_allowed(self):
        entry = valid_entry(input_cost_per_1k=0.0, output_cost_per_1k=0.0)
        assert entry.input_cost_per_1k == 0.0

    def test_negative_input_cost_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(input_cost_per_1k=-0.001)

    def test_negative_output_cost_raises(self):
        with pytest.raises(ValidationError):
            valid_entry(output_cost_per_1k=-1.0)


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------

class TestModelEntryImmutability:
    def test_cannot_mutate_alias(self):
        entry = valid_entry()
        with pytest.raises(Exception):
            entry.alias = "hacked"


# ---------------------------------------------------------------------------
# matches() scoring
# ---------------------------------------------------------------------------

class TestMatchesScoring:
    def setup_method(self):
        self.entry = ModelEntry(
            alias="claude-sonnet-global",
            aws_id="global.anthropic.claude-sonnet-4-20250514-v1:0",
            provider="anthropic",
            family="claude",
            region_scope="global",
            input_cost_per_1k=0.003,
            output_cost_per_1k=0.015,
        )

    def test_exact_alias_scores_4(self):
        assert self.entry.matches("claude-sonnet-global") == 4

    def test_exact_aws_id_scores_3(self):
        assert self.entry.matches("global.anthropic.claude-sonnet-4-20250514-v1:0") == 3

    def test_prefix_match_scores_2(self):
        assert self.entry.matches("claude-sonnet") == 2

    def test_substring_match_scores_1(self):
        assert self.entry.matches("anthropic") == 1

    def test_no_match_scores_0(self):
        assert self.entry.matches("nova-lite") == 0

    def test_case_insensitive_matching(self):
        assert self.entry.matches("CLAUDE-SONNET-GLOBAL") == 4

    def test_blank_query_scores_0(self):
        assert self.entry.matches("") == 0
