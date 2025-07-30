"""Base schema definitions for structured output extraction."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel, ABC):
    """Abstract base class for all extraction schemas."""

    model_config = ConfigDict(
        extra="forbid",  # This generates additionalProperties: false
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    """Abstract base class for all extraction schemas."""

    @classmethod
    @abstractmethod
    def get_extraction_prompt(cls) -> str:
        """Return the prompt to use for extraction with this schema."""

    @classmethod
    def get_schema_name(cls) -> str:
        """Return a human-readable name for this schema."""
        return cls.__name__.replace("Schema", "")

    @classmethod
    def get_schema_description(cls) -> str:
        """Return a description of what this schema extracts."""
        return cls.__doc__ or f"Extract {cls.get_schema_name()} information"


class ExtractionResult(BaseModel):
    """Result wrapper for extraction operations."""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    model_used: str | None = None
    tokens_used: int | None = None

    @classmethod
    def success_result(
        cls,
        data: dict[str, Any],
        model_used: str | None = None,
        tokens_used: int | None = None,
    ) -> "ExtractionResult":
        """Create a successful extraction result."""
        return cls(
            success=True,
            data=data,
            model_used=model_used,
            tokens_used=tokens_used,
        )

    @classmethod
    def error_result(cls, error: str) -> "ExtractionResult":
        """Create an error extraction result."""
        return cls(success=False, error=error)
