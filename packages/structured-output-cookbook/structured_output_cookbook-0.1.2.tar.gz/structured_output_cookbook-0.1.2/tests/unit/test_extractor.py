"""Test cases for extractor module."""

import json
from unittest.mock import Mock, patch

import pytest
from openai import APITimeoutError, RateLimitError

from structured_output_cookbook.config import Config
from structured_output_cookbook.extractor import StructuredExtractor
from structured_output_cookbook.templates.recipe import RecipeSchema


class TestStructuredExtractor:
    """Test cases for StructuredExtractor class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            openai_api_key="sk-test123456789",
            openai_model="gpt-4o-mini",
            max_retries=2,
            enable_caching=False,  # Disable for testing
        )

    @pytest.fixture
    def extractor(self, config):
        """Create test extractor."""
        with patch("structured_output_cookbook.extractor.OpenAI"):
            return StructuredExtractor(config)

    def test_init_with_config(self, config):
        """Test extractor initialization with configuration."""
        with patch("structured_output_cookbook.extractor.OpenAI") as mock_openai:
            extractor = StructuredExtractor(config)

            assert extractor.config == config
            mock_openai.assert_called_once_with(api_key=config.openai_api_key)
            assert extractor.rate_limiter is not None
            assert extractor.cost_tracker is not None

    def test_init_without_config(self):
        """Test extractor initialization without configuration."""
        with patch("structured_output_cookbook.extractor.Config") as mock_config:
            with patch("structured_output_cookbook.extractor.OpenAI"):
                mock_config.from_env.return_value = Mock()
                extractor = StructuredExtractor()

                mock_config.from_env.assert_called_once()

    def test_validate_input_empty_text(self, extractor):
        """Test input validation with empty text."""
        error = extractor._validate_input("")
        assert error == "Input text cannot be empty"

        error = extractor._validate_input("   ")
        assert error == "Input text cannot be empty"

    def test_validate_input_too_short(self, extractor):
        """Test input validation with text too short."""
        error = extractor._validate_input("short")
        assert "too short" in error

    def test_validate_input_too_long(self, extractor):
        """Test input validation with text too long."""
        long_text = "a" * (extractor.config.max_input_length + 1)
        error = extractor._validate_input(long_text)
        assert "too long" in error

    def test_validate_input_valid(self, extractor):
        """Test input validation with valid text."""
        valid_text = "This is a valid text for extraction testing purposes."
        error = extractor._validate_input(valid_text)
        assert error is None

    @patch("structured_output_cookbook.extractor.time.sleep")
    def test_extract_with_retry_on_rate_limit(self, mock_sleep, extractor):
        """Test extraction with retry on rate limit error."""
        # Complete mock response with all required fields
        complete_recipe = {
            "name": "Test Recipe",
            "description": "A delicious test recipe",
            "cuisine": "Italian",
            "difficulty": "easy",
            "prep_time": "15 minutes",
            "cook_time": "30 minutes",
            "total_time": "45 minutes",
            "servings": 4,
            "ingredients": [
                {"name": "flour", "quantity": "2", "unit": "cups", "notes": None},
            ],
            "instructions": ["Mix ingredients", "Cook until done"],
            "tags": ["vegetarian", "easy"],
            "nutrition": {"calories": 200},
        }

        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(complete_recipe)
        mock_response.model = "gpt-4o-mini"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 80
        mock_response.usage.completion_tokens = 20

        # First call raises RateLimitError, second succeeds
        rate_limit_error = RateLimitError(
            message="Rate limit exceeded",
            response=Mock(),
            body={},
        )
        extractor.client.chat.completions.create.side_effect = [
            rate_limit_error,
            mock_response,
        ]

        # Mock rate limiter to not actually wait
        extractor.rate_limiter.wait_if_needed = Mock()

        text = "This is a test recipe text for extraction."
        result = extractor.extract(text, RecipeSchema)

        assert result.success
        assert "name" in result.data
        mock_sleep.assert_called()  # Should have slept for retry
        assert extractor.client.chat.completions.create.call_count == 2

    def test_extract_success(self, extractor):
        """Test successful extraction."""
        # Complete mock response with all required fields
        complete_recipe = {
            "name": "Test Recipe",
            "description": "A delicious test recipe",
            "cuisine": "Italian",
            "difficulty": "easy",
            "prep_time": "15 minutes",
            "cook_time": "30 minutes",
            "total_time": "45 minutes",
            "servings": 4,
            "ingredients": [
                {"name": "flour", "quantity": "2", "unit": "cups", "notes": None},
            ],
            "instructions": ["Mix ingredients", "Cook until done"],
            "tags": ["vegetarian", "easy"],
            "nutrition": {"calories": 200},
        }

        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(complete_recipe)
        mock_response.model = "gpt-4o-mini"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 80
        mock_response.usage.completion_tokens = 20

        extractor.client.chat.completions.create.return_value = mock_response
        extractor.rate_limiter.wait_if_needed = Mock()

        text = "This is a test recipe text for extraction."
        result = extractor.extract(text, RecipeSchema)

        assert result.success
        assert result.data is not None
        assert "name" in result.data
        assert result.model_used == "gpt-4o-mini"
        assert result.tokens_used == 100

    def test_extract_empty_response(self, extractor):
        """Test extraction with empty response."""
        # Mock empty response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None

        extractor.client.chat.completions.create.return_value = mock_response
        extractor.rate_limiter.wait_if_needed = Mock()

        text = "This is a test recipe text for extraction."
        result = extractor.extract(text, RecipeSchema)

        assert not result.success
        assert "Empty response" in result.error

    def test_extract_invalid_json(self, extractor):
        """Test extraction with invalid JSON response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"invalid": json}'  # Invalid JSON

        extractor.client.chat.completions.create.return_value = mock_response
        extractor.rate_limiter.wait_if_needed = Mock()

        text = "This is a test recipe text for extraction."
        result = extractor.extract(text, RecipeSchema)

        assert not result.success
        assert "Invalid response format" in result.error

    def test_extract_with_caching(self, config):
        """Test extraction with caching enabled."""
        config.enable_caching = True

        with patch("structured_output_cookbook.extractor.OpenAI"):
            extractor = StructuredExtractor(config)

            # Mock cache hit with complete data
            cached_data = {
                "name": "Cached Recipe",
                "description": "A cached recipe",
                "cuisine": None,
                "difficulty": None,
                "prep_time": None,
                "cook_time": None,
                "total_time": None,
                "servings": None,
                "ingredients": [],
                "instructions": [],
                "tags": [],
                "nutrition": None,
            }
            if extractor.cache:
                extractor.cache.get = Mock(return_value=cached_data)

            text = "This is a test recipe text for extraction."
            result = extractor.extract(text, RecipeSchema)

            assert result.success
            assert result.data == cached_data
            assert result.tokens_used is None  # No tokens used for cached result

    def test_extract_max_retries_exceeded(self, extractor):
        """Test extraction when max retries is exceeded."""
        # Mock API error that causes retries
        timeout_error = APITimeoutError(request=Mock())
        extractor.client.chat.completions.create.side_effect = timeout_error
        extractor.rate_limiter.wait_if_needed = Mock()

        text = "This is a test recipe text for extraction."
        result = extractor.extract(text, RecipeSchema)

        assert not result.success
        assert "API timeout" in result.error
        # Should have tried max_retries + 1 times
        assert (
            extractor.client.chat.completions.create.call_count
            == extractor.config.max_retries + 1
        )

    def test_extract_input_validation_failure(self, extractor):
        """Test extraction with input validation failure."""
        result = extractor.extract("", RecipeSchema)

        assert not result.success
        assert "cannot be empty" in result.error

        # Should not have called the API
        extractor.client.chat.completions.create.assert_not_called()

    def test_ensure_additional_properties_false(self, extractor):
        """Test that _ensure_additional_properties_false works correctly."""
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "nested": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                },
            },
        }

        extractor._ensure_additional_properties_false(schema_dict)

        assert schema_dict["additionalProperties"] is False
        assert schema_dict["properties"]["nested"]["additionalProperties"] is False
