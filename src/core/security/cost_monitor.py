"""
CostMonitor — tracks token consumption and estimated USD cost.

Pricing is no longer hardcoded here. Instead, the caller is expected to
pass the per-1K token rates obtained from the ModelRegistry so that costs
stay accurate as the catalog evolves without touching this class.
"""


class CostMonitor:
    """Accumulate token usage and compute a running cost estimate."""

    def __init__(self) -> None:
        self.total_cost: float = 0.0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0

    def update(
        self,
        input_tokens: float,
        output_tokens: float,
        input_cost_per_1k: float = 0.001,
        output_cost_per_1k: float = 0.005,
    ) -> float:
        """
        Record a single API call's token usage and return the incremental cost.

        Parameters
        ----------
        input_tokens:
            Number of input (prompt) tokens consumed.
        output_tokens:
            Number of output (completion) tokens generated.
        input_cost_per_1k:
            Cost in USD per 1,000 input tokens (default: global fallback).
        output_cost_per_1k:
            Cost in USD per 1,000 output tokens (default: global fallback).

        Returns
        -------
        float
            The cost of this call in USD.
        """
        cost = (input_tokens / 1000.0 * input_cost_per_1k) + (
            output_tokens / 1000.0 * output_cost_per_1k
        )
        self.total_cost += cost
        self.total_input_tokens += int(input_tokens)
        self.total_output_tokens += int(output_tokens)
        return cost

    def get_summary(self) -> str:
        """Return a one-line human-readable cost summary."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return (
            f"[COST] Input: {self.total_input_tokens:,} tokens | "
            f"Output: {self.total_output_tokens:,} tokens | "
            f"Total: {total_tokens:,} tokens | "
            f"Est. cost: ${self.total_cost:.6f}"
        )
