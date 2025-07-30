"""Cost tracking utilities for OpenAI API calls."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple

from .logger import get_logger


class TokenUsage(NamedTuple):
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CostInfo(NamedTuple):
    """Cost calculation information."""

    prompt_cost: float
    completion_cost: float
    total_cost: float
    currency: str = "USD"


# Current OpenAI pricing as of 2024 (per 1K tokens)
# Updated regularly - check https://openai.com/pricing
OPENAI_PRICING = {
    "gpt-4o": {
        "prompt": 0.0025,  # $2.50 per 1K tokens
        "completion": 0.01,  # $10.00 per 1K tokens
    },
    "gpt-4o-2024-08-06": {
        "prompt": 0.0025,
        "completion": 0.01,
    },
    "gpt-4o-mini": {
        "prompt": 0.00015,  # $0.150 per 1K tokens
        "completion": 0.0006,  # $0.600 per 1K tokens
    },
    "gpt-4o-mini-2024-07-18": {
        "prompt": 0.00015,
        "completion": 0.0006,
    },
    "gpt-4-turbo": {
        "prompt": 0.01,  # $10.00 per 1K tokens
        "completion": 0.03,  # $30.00 per 1K tokens
    },
    "gpt-4": {
        "prompt": 0.03,  # $30.00 per 1K tokens
        "completion": 0.06,  # $60.00 per 1K tokens
    },
    "gpt-3.5-turbo": {
        "prompt": 0.0005,  # $0.50 per 1K tokens
        "completion": 0.0015,  # $1.50 per 1K tokens
    },
}


class CostTracker:
    """Track and calculate costs for OpenAI API usage."""

    def __init__(self, pricing_data: dict[str, Any] | None = None):
        """Initialize cost tracker.

        Args:
            pricing_data: Custom pricing data, defaults to OPENAI_PRICING
        """
        self.pricing = pricing_data or OPENAI_PRICING
        self.logger = get_logger(__name__)
        self.session_costs: list[dict[str, Any]] = []

    def calculate_cost(self, model: str, usage: TokenUsage) -> CostInfo:
        """Calculate cost for a given model and token usage.

        Args:
            model: OpenAI model name
            usage: Token usage information

        Returns:
            Cost information
        """
        # Normalize model name for pricing lookup
        model_key = self._normalize_model_name(model)

        if model_key not in self.pricing:
            self.logger.warning(
                f"Unknown model for pricing: {model}, using gpt-4o-mini pricing",
            )
            model_key = "gpt-4o-mini"

        pricing = self.pricing[model_key]

        # Calculate costs (pricing is per 1K tokens)
        prompt_cost = (usage.prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (usage.completion_tokens / 1000) * pricing["completion"]
        total_cost = prompt_cost + completion_cost

        return CostInfo(
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_cost=total_cost,
        )

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name for pricing lookup."""
        # Handle different model name formats
        if model.startswith("gpt-4o-mini"):
            return "gpt-4o-mini"
        if model.startswith("gpt-4o"):
            return "gpt-4o"
        if model.startswith("gpt-4-turbo"):
            return "gpt-4-turbo"
        if model.startswith("gpt-4"):
            return "gpt-4"
        if model.startswith("gpt-3.5"):
            return "gpt-3.5-turbo"

        return model

    def track_request(
        self,
        model: str,
        usage: TokenUsage,
        extraction_type: str = "unknown",
    ) -> CostInfo:
        """Track a request and its cost.

        Args:
            model: OpenAI model used
            usage: Token usage information
            extraction_type: Type of extraction performed

        Returns:
            Cost information
        """
        cost_info = self.calculate_cost(model, usage)

        # Record for session tracking
        self.session_costs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "extraction_type": extraction_type,
                "usage": usage._asdict(),
                "cost": cost_info._asdict(),
            },
        )

        self.logger.info(
            f"API call: {model} | Tokens: {usage.total_tokens} | "
            f"Cost: ${cost_info.total_cost:.4f} | Type: {extraction_type}",
        )

        return cost_info

    def get_session_stats(self) -> dict[str, Any]:
        """Get statistics for the current session.

        Returns:
            Session statistics
        """
        if not self.session_costs:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "models_used": [],
                "extraction_types": [],
            }

        total_cost = sum(req["cost"]["total_cost"] for req in self.session_costs)
        total_tokens = sum(req["usage"]["total_tokens"] for req in self.session_costs)
        models_used = list(set(req["model"] for req in self.session_costs))
        extraction_types = list(
            set(req["extraction_type"] for req in self.session_costs),
        )

        return {
            "total_requests": len(self.session_costs),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "models_used": models_used,
            "extraction_types": extraction_types,
            "average_cost_per_request": total_cost / len(self.session_costs),
            "average_tokens_per_request": total_tokens / len(self.session_costs),
        }

    def export_session_data(self, filepath: str) -> None:
        """Export session data to a JSON file.

        Args:
            filepath: Path to save the session data
        """
        data = {
            "session_start": (
                self.session_costs[0]["timestamp"] if self.session_costs else None
            ),
            "session_end": (
                self.session_costs[-1]["timestamp"] if self.session_costs else None
            ),
            "stats": self.get_session_stats(),
            "requests": self.session_costs,
        }

        Path(filepath).write_text(json.dumps(data, indent=2))
        self.logger.info(f"Session data exported to {filepath}")

    def clear_session(self) -> None:
        """Clear session data."""
        self.session_costs.clear()
        self.logger.info("Session data cleared")

    def get_model_recommendations(
        self,
        usage_pattern: dict[str, Any],
    ) -> dict[str, Any]:
        """Get model recommendations based on usage patterns.

        Args:
            usage_pattern: Dictionary with average token usage info

        Returns:
            Model recommendations with cost comparisons
        """
        avg_tokens = usage_pattern.get("avg_total_tokens", 1000)
        avg_prompt_tokens = usage_pattern.get(
            "avg_prompt_tokens",
            int(avg_tokens * 0.8),
        )
        avg_completion_tokens = usage_pattern.get(
            "avg_completion_tokens",
            int(avg_tokens * 0.2),
        )

        usage = TokenUsage(
            prompt_tokens=avg_prompt_tokens,
            completion_tokens=avg_completion_tokens,
            total_tokens=avg_tokens,
        )

        recommendations = {}
        for model in ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4"]:
            if model in self.pricing:
                cost = self.calculate_cost(model, usage)
                recommendations[model] = {
                    "cost_per_request": cost.total_cost,
                    "cost_per_1k_requests": cost.total_cost * 1000,
                    "relative_cost": (
                        "baseline"
                        if model == "gpt-4o-mini"
                        else f"{cost.total_cost / self.calculate_cost('gpt-4o-mini', usage).total_cost:.1f}x"
                    ),
                }

        return recommendations
