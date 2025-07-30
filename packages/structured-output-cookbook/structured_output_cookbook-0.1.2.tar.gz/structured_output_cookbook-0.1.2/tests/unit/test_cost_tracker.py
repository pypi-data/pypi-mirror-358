"""Test cases for cost tracker module."""

import pytest

from structured_output_cookbook.utils.cost_tracker import (
    CostInfo,
    CostTracker,
    TokenUsage,
)


class TestCostTracker:
    """Test cases for CostTracker class."""

    @pytest.fixture
    def cost_tracker(self):
        """Create test cost tracker."""
        return CostTracker()

    def test_calculate_cost_gpt4o_mini(self, cost_tracker):
        """Test cost calculation for gpt-4o-mini."""
        usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = cost_tracker.calculate_cost("gpt-4o-mini", usage)

        # gpt-4o-mini: $0.150 per 1K prompt tokens, $0.600 per 1K completion tokens
        expected_prompt_cost = (1000 / 1000) * 0.00015
        expected_completion_cost = (500 / 1000) * 0.0006
        expected_total = expected_prompt_cost + expected_completion_cost

        assert cost.prompt_cost == expected_prompt_cost
        assert cost.completion_cost == expected_completion_cost
        assert cost.total_cost == expected_total
        assert cost.currency == "USD"

    def test_calculate_cost_gpt4o(self, cost_tracker):
        """Test cost calculation for gpt-4o."""
        usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = cost_tracker.calculate_cost("gpt-4o", usage)

        # gpt-4o: $2.50 per 1K prompt tokens, $10.00 per 1K completion tokens
        expected_prompt_cost = (1000 / 1000) * 0.0025
        expected_completion_cost = (500 / 1000) * 0.01
        expected_total = expected_prompt_cost + expected_completion_cost

        assert cost.prompt_cost == expected_prompt_cost
        assert cost.completion_cost == expected_completion_cost
        assert cost.total_cost == expected_total

    def test_normalize_model_name(self, cost_tracker):
        """Test model name normalization."""
        assert (
            cost_tracker._normalize_model_name("gpt-4o-mini-2024-07-18")
            == "gpt-4o-mini"
        )
        assert cost_tracker._normalize_model_name("gpt-4o-2024-08-06") == "gpt-4o"
        assert (
            cost_tracker._normalize_model_name("gpt-4-turbo-preview") == "gpt-4-turbo"
        )
        assert cost_tracker._normalize_model_name("gpt-4-0613") == "gpt-4"
        assert (
            cost_tracker._normalize_model_name("gpt-3.5-turbo-0613") == "gpt-3.5-turbo"
        )

    def test_unknown_model_fallback(self, cost_tracker):
        """Test fallback to gpt-4o-mini pricing for unknown models."""
        usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = cost_tracker.calculate_cost("unknown-model", usage)

        # Should fallback to gpt-4o-mini pricing
        expected_cost = cost_tracker.calculate_cost("gpt-4o-mini", usage)
        assert cost.total_cost == expected_cost.total_cost

    def test_track_request(self, cost_tracker):
        """Test request tracking."""
        usage = TokenUsage(prompt_tokens=800, completion_tokens=200, total_tokens=1000)
        cost_info = cost_tracker.track_request("gpt-4o-mini", usage, "recipe")

        assert isinstance(cost_info, CostInfo)
        assert len(cost_tracker.session_costs) == 1

        request_data = cost_tracker.session_costs[0]
        assert request_data["model"] == "gpt-4o-mini"
        assert request_data["extraction_type"] == "recipe"
        assert request_data["usage"]["total_tokens"] == 1000
        assert "timestamp" in request_data

    def test_get_session_stats_empty(self, cost_tracker):
        """Test session statistics with no requests."""
        stats = cost_tracker.get_session_stats()

        assert stats["total_requests"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost"] == 0.0
        assert stats["models_used"] == []
        assert stats["extraction_types"] == []

    def test_get_session_stats_with_requests(self, cost_tracker):
        """Test session statistics with requests."""
        usage1 = TokenUsage(prompt_tokens=800, completion_tokens=200, total_tokens=1000)
        usage2 = TokenUsage(prompt_tokens=600, completion_tokens=150, total_tokens=750)

        cost_tracker.track_request("gpt-4o-mini", usage1, "recipe")
        cost_tracker.track_request("gpt-4o", usage2, "job")

        stats = cost_tracker.get_session_stats()

        assert stats["total_requests"] == 2
        assert stats["total_tokens"] == 1750
        assert stats["total_cost"] > 0
        assert "gpt-4o-mini" in stats["models_used"]
        assert "gpt-4o" in stats["models_used"]
        assert "recipe" in stats["extraction_types"]
        assert "job" in stats["extraction_types"]
        assert stats["average_tokens_per_request"] == 875

    def test_clear_session(self, cost_tracker):
        """Test clearing session data."""
        usage = TokenUsage(prompt_tokens=800, completion_tokens=200, total_tokens=1000)
        cost_tracker.track_request("gpt-4o-mini", usage, "test")

        assert len(cost_tracker.session_costs) == 1

        cost_tracker.clear_session()

        assert len(cost_tracker.session_costs) == 0
        stats = cost_tracker.get_session_stats()
        assert stats["total_requests"] == 0

    def test_get_model_recommendations(self, cost_tracker):
        """Test model recommendations."""
        usage_pattern = {
            "avg_total_tokens": 1000,
            "avg_prompt_tokens": 800,
            "avg_completion_tokens": 200,
        }

        recommendations = cost_tracker.get_model_recommendations(usage_pattern)

        assert "gpt-4o-mini" in recommendations
        assert "gpt-4o" in recommendations
        assert "gpt-4" in recommendations

        # gpt-4o-mini should be baseline
        assert recommendations["gpt-4o-mini"]["relative_cost"] == "baseline"

        # Other models should have relative cost multipliers
        assert "x" in recommendations["gpt-4o"]["relative_cost"]

        # More expensive models should have higher costs
        assert (
            recommendations["gpt-4"]["cost_per_request"]
            > recommendations["gpt-4o"]["cost_per_request"]
            > recommendations["gpt-4o-mini"]["cost_per_request"]
        )

    def test_export_session_data(self, cost_tracker, tmp_path):
        """Test exporting session data."""
        usage = TokenUsage(prompt_tokens=800, completion_tokens=200, total_tokens=1000)
        cost_tracker.track_request("gpt-4o-mini", usage, "test")

        export_file = tmp_path / "session_data.json"
        cost_tracker.export_session_data(str(export_file))

        assert export_file.exists()

        import json

        with open(export_file) as f:
            data = json.load(f)

        assert "session_start" in data
        assert "session_end" in data
        assert "stats" in data
        assert "requests" in data
        assert len(data["requests"]) == 1
