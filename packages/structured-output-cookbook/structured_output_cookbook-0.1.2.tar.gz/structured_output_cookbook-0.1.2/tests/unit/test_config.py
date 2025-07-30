"""Test cases for configuration module."""

import pytest
from pydantic import ValidationError

from structured_output_cookbook.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_from_env_with_valid_api_key(self, monkeypatch):
        """Test configuration loading with valid environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123456789")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        monkeypatch.setenv("TEMPERATURE", "0.2")
        monkeypatch.setenv("MAX_TOKENS", "2000")

        config = Config.from_env()

        assert config.openai_api_key == "sk-test123456789"
        assert config.openai_model == "gpt-4o-mini"
        assert config.temperature == 0.2
        assert config.max_tokens == 2000

    def test_from_env_missing_api_key(self, monkeypatch):
        """Test configuration loading without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(
            ValueError,
            match="OPENAI_API_KEY environment variable is required",
        ):
            Config.from_env()

    def test_from_env_defaults(self, monkeypatch):
        """Test configuration loading with default values."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123456789")
        # Clear other env vars to test defaults
        for var in ["OPENAI_MODEL", "TEMPERATURE", "MAX_TOKENS", "LOG_LEVEL"]:
            monkeypatch.delenv(var, raising=False)

        config = Config.from_env()

        assert config.openai_model == "gpt-4o-mini"
        assert config.temperature == 0.1
        assert config.max_tokens == 4000
        assert config.log_level == "INFO"
        assert config.max_retries == 3
        assert config.enable_caching is True

    def test_invalid_api_key_format(self):
        """Test validation of API key format."""
        with pytest.raises(ValidationError, match="OpenAI API key must start with"):
            Config(openai_api_key="invalid-key")

    def test_valid_api_key_formats(self):
        """Test validation of valid API key formats."""
        # Test sk- prefix
        config1 = Config(openai_api_key="sk-test123456789")
        assert config1.openai_api_key == "sk-test123456789"

        # Test sk-proj- prefix
        config2 = Config(openai_api_key="sk-proj-test123456789")
        assert config2.openai_api_key == "sk-proj-test123456789"

    def test_temperature_validation(self):
        """Test temperature parameter validation."""
        # Valid temperatures
        config1 = Config(openai_api_key="sk-test", temperature=0.0)
        assert config1.temperature == 0.0

        config2 = Config(openai_api_key="sk-test", temperature=2.0)
        assert config2.temperature == 2.0

        # Invalid temperatures
        with pytest.raises(ValidationError):
            Config(openai_api_key="sk-test", temperature=-0.1)

        with pytest.raises(ValidationError):
            Config(openai_api_key="sk-test", temperature=2.1)

    def test_max_retries_validation(self):
        """Test max retries validation."""
        # Valid values
        config1 = Config(openai_api_key="sk-test", max_retries=0)
        assert config1.max_retries == 0

        config2 = Config(openai_api_key="sk-test", max_retries=10)
        assert config2.max_retries == 10

        # Invalid values
        with pytest.raises(ValidationError):
            Config(openai_api_key="sk-test", max_retries=-1)

        with pytest.raises(ValidationError):
            Config(openai_api_key="sk-test", max_retries=11)

    def test_log_level_validation(self):
        """Test log level validation."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            config = Config(openai_api_key="sk-test", log_level=level)
            assert config.log_level == level

        # Test case insensitive
        config = Config(openai_api_key="sk-test", log_level="debug")
        assert config.log_level == "DEBUG"

        # Invalid level
        with pytest.raises(ValidationError):
            Config(openai_api_key="sk-test", log_level="INVALID")

    def test_log_format_validation(self):
        """Test log format validation."""
        # Valid formats
        config1 = Config(openai_api_key="sk-test", log_format="json")
        assert config1.log_format == "json"

        config2 = Config(openai_api_key="sk-test", log_format="text")
        assert config2.log_format == "text"

        # Invalid format
        with pytest.raises(ValidationError):
            Config(openai_api_key="sk-test", log_format="invalid")

    def test_get_masked_api_key(self):
        """Test API key masking for logging."""
        config = Config(openai_api_key="sk-test123456789abcdef")
        masked = config.get_masked_api_key()

        assert masked.startswith("sk-test1")
        assert masked.endswith("cdef")
        assert "..." in masked
        assert len(masked) < len(config.openai_api_key)

    def test_to_dict_masks_api_key(self):
        """Test that to_dict masks the API key."""
        config = Config(openai_api_key="sk-test123456789abcdef")
        config_dict = config.to_dict()

        assert "openai_api_key" in config_dict
        assert config_dict["openai_api_key"] != config.openai_api_key
        assert config_dict["openai_api_key"].startswith("sk-test1")
        assert "..." in config_dict["openai_api_key"]
