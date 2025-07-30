"""Configuration management for the application."""

import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()


class Config(BaseModel):
    """Application configuration."""

    openai_api_key: str = Field(..., min_length=1)
    openai_model: str = "gpt-4o-mini"
    max_retries: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    log_level: str = "INFO"
    log_format: str = "json"
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=1, le=100000)
    max_input_length: int = Field(default=100000, ge=1)
    enable_caching: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600, ge=60)
    rate_limit_requests_per_minute: int = Field(default=60, ge=1)

    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v.startswith(("sk-", "sk-proj-")):
            raise ValueError("OpenAI API key must start with 'sk-' or 'sk-proj-'")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        if v not in {"json", "text"}:
            raise ValueError("Log format must be 'json' or 'text'")
        return v

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return cls(
            openai_api_key=api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            temperature=float(os.getenv("TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("MAX_TOKENS", "4000")),
            max_input_length=int(os.getenv("MAX_INPUT_LENGTH", "100000")),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
            rate_limit_requests_per_minute=int(os.getenv("RATE_LIMIT_RPM", "60")),
        )

    def get_masked_api_key(self) -> str:
        """Get masked API key for logging."""
        return f"{self.openai_api_key[:8]}...{self.openai_api_key[-4:]}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, masking sensitive data."""
        data = self.model_dump()
        data["openai_api_key"] = self.get_masked_api_key()
        return data
