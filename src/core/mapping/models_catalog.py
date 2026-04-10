"""
models_catalog.py — Single source of truth for all known Bedrock models.

Pricing data sourced from the AWS Bedrock pricing page (April 2025).
Every entry is a ModelEntry instance validated at import time.
The MODELS list is consumed by ModelRegistry.load_defaults().
"""

from __future__ import annotations

from src.core.mapping.model_entry import ModelEntry

# ---------------------------------------------------------------------------
# Catalog definition
# ---------------------------------------------------------------------------
# fmt: off
MODELS: list[ModelEntry] = [

    # ── Anthropic Claude — Global Cross-Region ──────────────────────────────
    ModelEntry(
        alias="claude-sonnet-global",
        aws_id="global.anthropic.claude-sonnet-4-20250514-v1:0",
        provider="anthropic", family="claude", region_scope="global",
        supports_tools=True,
        input_cost_per_1k=0.003,   output_cost_per_1k=0.015,
        tags=["latest", "balanced", "tools"],
    ),
    ModelEntry(
        alias="claude-haiku-global",
        aws_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",
        provider="anthropic", family="claude", region_scope="global",
        supports_tools=True,
        input_cost_per_1k=0.0008,  output_cost_per_1k=0.0025,
        tags=["fast", "cheap", "tools"],
    ),
    ModelEntry(
        alias="claude-opus-global",
        aws_id="global.anthropic.claude-opus-4-5-20251101-v1:0",
        provider="anthropic", family="claude", region_scope="global",
        supports_tools=True,
        input_cost_per_1k=0.015,   output_cost_per_1k=0.075,
        tags=["powerful", "tools"],
    ),

    # ── Anthropic Claude — US Cross-Region ──────────────────────────────────
    ModelEntry(
        alias="claude-sonnet-us",
        aws_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        provider="anthropic", family="claude", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.003,   output_cost_per_1k=0.015,
        tags=["tools"],
    ),
    ModelEntry(
        alias="claude-haiku-us",
        aws_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        provider="anthropic", family="claude", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.0008,  output_cost_per_1k=0.0025,
        tags=["fast", "cheap", "tools"],
    ),
    ModelEntry(
        alias="claude-opus-us",
        aws_id="us.anthropic.claude-3-opus-20240229-v1:0",
        provider="anthropic", family="claude", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.015,   output_cost_per_1k=0.075,
        tags=["powerful", "tools"],
    ),
    ModelEntry(
        alias="claude-3-7-sonnet-us",
        aws_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        provider="anthropic", family="claude", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.003,   output_cost_per_1k=0.015,
        tags=["thinking", "tools"],
    ),

    # ── Anthropic Claude — EU Cross-Region ──────────────────────────────────
    ModelEntry(
        alias="claude-sonnet-eu",
        aws_id="eu.anthropic.claude-3-5-sonnet-20241022-v2:0",
        provider="anthropic", family="claude", region_scope="eu",
        supports_tools=True,
        input_cost_per_1k=0.003,   output_cost_per_1k=0.015,
        tags=["tools", "gdpr"],
    ),
    ModelEntry(
        alias="claude-haiku-eu",
        aws_id="eu.anthropic.claude-3-5-haiku-20241022-v1:0",
        provider="anthropic", family="claude", region_scope="eu",
        supports_tools=True,
        input_cost_per_1k=0.0008,  output_cost_per_1k=0.0025,
        tags=["fast", "cheap", "tools", "gdpr"],
    ),

    # ── Amazon Nova — Global Cross-Region ───────────────────────────────────
    ModelEntry(
        alias="nova-lite-global",
        aws_id="global.amazon.nova-2-lite-v1:0",
        provider="amazon", family="nova", region_scope="global",
        supports_tools=True,
        input_cost_per_1k=0.00006, output_cost_per_1k=0.00024,
        tags=["cheap", "fast", "tools"],
    ),

    # ── Amazon Nova — US Cross-Region ───────────────────────────────────────
    ModelEntry(
        alias="nova-pro-us",
        aws_id="us.amazon.nova-pro-v1:0",
        provider="amazon", family="nova", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.0008,  output_cost_per_1k=0.0032,
        tags=["tools"],
    ),
    ModelEntry(
        alias="nova-lite-us",
        aws_id="us.amazon.nova-lite-v1:0",
        provider="amazon", family="nova", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.00006, output_cost_per_1k=0.00024,
        tags=["cheap", "fast", "tools"],
    ),
    ModelEntry(
        alias="nova-micro-us",
        aws_id="us.amazon.nova-micro-v1:0",
        provider="amazon", family="nova", region_scope="us",
        supports_tools=False,
        input_cost_per_1k=0.000035, output_cost_per_1k=0.00014,
        tags=["ultra-cheap", "ultra-fast"],
    ),

    # ── Amazon Nova — Native ─────────────────────────────────────────────────
    ModelEntry(
        alias="nova-pro",
        aws_id="amazon.nova-pro-v1:0",
        provider="amazon", family="nova", region_scope="native",
        supports_tools=True,
        input_cost_per_1k=0.0008,  output_cost_per_1k=0.0032,
        tags=["tools"],
    ),
    ModelEntry(
        alias="nova-lite",
        aws_id="amazon.nova-lite-v1:0",
        provider="amazon", family="nova", region_scope="native",
        supports_tools=True,
        input_cost_per_1k=0.00006, output_cost_per_1k=0.00024,
        tags=["cheap", "fast", "tools", "default"],
    ),

    # ── Meta Llama ───────────────────────────────────────────────────────────
    ModelEntry(
        alias="llama-3-1-70b-us",
        aws_id="us.meta.llama3-1-70b-instruct-v1:0",
        provider="meta", family="llama", region_scope="us",
        supports_tools=True,
        input_cost_per_1k=0.00099, output_cost_per_1k=0.00099,
        tags=["open-source", "tools"],
    ),

    # ── Mistral ──────────────────────────────────────────────────────────────
    ModelEntry(
        alias="mistral-large",
        aws_id="mistral.mistral-large-2402-v1:0",
        provider="mistral", family="mistral", region_scope="native",
        supports_tools=True,
        input_cost_per_1k=0.004,   output_cost_per_1k=0.012,
        tags=["tools", "multilingual"],
    ),
]
# fmt: on

# ---------------------------------------------------------------------------
# Default model alias used when no model is explicitly selected
# ---------------------------------------------------------------------------
DEFAULT_MODEL_ALIAS: str = "nova-lite"
