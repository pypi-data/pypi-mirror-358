"""Main extractor class for structured output generation."""

import json
import time
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError
from pydantic import ValidationError

from .config import Config
from .schemas.base import BaseSchema, ExtractionResult
from .utils import (
    CostTracker,
    RateLimiter,
    SimpleCache,
    TokenUsage,
    YamlSchema,
    get_logger,
)


class StructuredExtractor:
    """Main extractor class using OpenAI's structured outputs."""

    def __init__(self, config: Config | None = None):
        """Initialize the extractor with configuration."""
        self.config = config or Config.from_env()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.logger = get_logger(__name__)

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(self.config.rate_limit_requests_per_minute)

        # Initialize cache if enabled
        self.cache = (
            SimpleCache(self.config.cache_ttl_seconds)
            if self.config.enable_caching
            else None
        )

        # Initialize cost tracker
        self.cost_tracker = CostTracker()

        # Log configuration (with masked API key)
        self.logger.info(f"Extractor initialized with config: {self.config.to_dict()}")

    def extract(
        self,
        text: str,
        schema: type[BaseSchema],
        system_prompt: str | None = None,
    ) -> ExtractionResult:
        """
        Extract structured data from text using a predefined Pydantic schema.

        Args:
            text: Input text to extract from
            schema: Pydantic schema class to use for extraction
            system_prompt: Optional custom system prompt

        Returns:
            ExtractionResult with success status and extracted data
        """
        # Validate input
        validation_error = self._validate_input(text)
        if validation_error:
            return ExtractionResult.error_result(validation_error)

        schema_name = schema.get_schema_name()
        self.logger.info(f"Starting extraction with schema: {schema_name}")

        # Check cache first
        if self.cache:
            cached_result = self.cache.get(
                text,
                schema_name,
                self.config.openai_model,
                self.config.temperature,
            )
            if cached_result:
                self.logger.info("Returning cached result")
                return ExtractionResult.success_result(
                    data=cached_result,
                    model_used=self.config.openai_model,
                    tokens_used=None,  # We don't store token usage in cache
                )

        # Use custom prompt or schema default
        prompt = system_prompt or schema.get_extraction_prompt()

        # Generate schema and ensure additionalProperties is false
        schema_dict = schema.model_json_schema()
        self._ensure_additional_properties_false(schema_dict)

        # Execute with retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                # Rate limiting
                self.rate_limiter.wait_if_needed()

                self.logger.debug(
                    f"Attempt {attempt + 1}/{self.config.max_retries + 1}",
                )

                response = self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text},
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name.lower().replace(" ", "_"),
                            "strict": True,
                            "schema": schema_dict,
                        },
                    },
                    timeout=self.config.timeout_seconds,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )

                # Parse the response
                content = response.choices[0].message.content
                if not content:
                    if attempt < self.config.max_retries:
                        self.logger.warning(
                            f"Empty response, retrying... (attempt {attempt + 1})",
                        )
                        continue
                    return ExtractionResult.error_result(
                        "Empty response from LLM after all retries",
                    )

                # Parse JSON and validate with schema
                try:
                    raw_data = json.loads(content)
                    validated_data = schema(**raw_data)

                    # Track cost
                    if response.usage:
                        usage = TokenUsage(
                            prompt_tokens=response.usage.prompt_tokens,
                            completion_tokens=response.usage.completion_tokens,
                            total_tokens=response.usage.total_tokens,
                        )
                        self.cost_tracker.track_request(
                            response.model,
                            usage,
                            schema_name,
                        )

                    # Cache the result
                    if self.cache:
                        self.cache.set(
                            text,
                            schema_name,
                            self.config.openai_model,
                            self.config.temperature,
                            validated_data.model_dump(),
                        )

                    self.logger.info("Extraction completed successfully")

                    return ExtractionResult.success_result(
                        data=validated_data.model_dump(),
                        model_used=response.model,
                        tokens_used=(
                            response.usage.total_tokens if response.usage else None
                        ),
                    )

                except (json.JSONDecodeError, ValidationError) as e:
                    if attempt < self.config.max_retries:
                        self.logger.warning(
                            f"Failed to parse/validate response, retrying... Error: {e}",
                        )
                        continue
                    self.logger.error(
                        f"Failed to parse/validate response after all retries: {e}",
                    )
                    return ExtractionResult.error_result(
                        f"Invalid response format: {e!s}",
                    )

            except RateLimitError as e:
                self.logger.warning(f"Rate limit hit, waiting before retry... {e}")
                time.sleep(min(2**attempt, 60))  # Exponential backoff, max 60s
                continue

            except APITimeoutError as e:
                if attempt < self.config.max_retries:
                    self.logger.warning(f"API timeout, retrying... {e}")
                    continue
                self.logger.error(f"API timeout after all retries: {e}")
                return ExtractionResult.error_result(f"API timeout: {e!s}")

            except APIError as e:
                # Check if it's a retryable error
                retryable = hasattr(e, "status_code") and getattr(
                    e,
                    "status_code",
                    0,
                ) in [500, 502, 503, 504]
                if attempt < self.config.max_retries and retryable:
                    self.logger.warning(
                        f"API error {getattr(e, 'status_code', 'unknown')}, retrying... {e}",
                    )
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                self.logger.error(f"API error: {e}")
                return ExtractionResult.error_result(f"API error: {e!s}")

            except Exception as e:
                if attempt < self.config.max_retries:
                    self.logger.warning(f"Unexpected error, retrying... {e}")
                    continue
                self.logger.error(f"Extraction failed after all retries: {e}")
                return ExtractionResult.error_result(str(e))

        return ExtractionResult.error_result("Max retries exceeded")

    def _validate_input(self, text: str) -> str | None:
        """Validate input text.

        Args:
            text: Input text to validate

        Returns:
            Error message if validation fails, None otherwise
        """
        if not text or not text.strip():
            return "Input text cannot be empty"

        if len(text) > self.config.max_input_length:
            return f"Input text too long: {len(text)} > {self.config.max_input_length} characters"

        # Basic text validation
        if len(text.strip()) < 10:
            return "Input text too short: minimum 10 characters required"

        return None

    def extract_with_yaml_schema(
        self,
        text: str,
        yaml_schema: YamlSchema,
    ) -> ExtractionResult:
        """
        Extract structured data from text using a YAML schema configuration.

        Args:
            text: Input text to extract from
            yaml_schema: YamlSchema object containing schema and prompt

        Returns:
            ExtractionResult with success status and extracted data
        """
        try:
            self.logger.info(
                f"Starting extraction with YAML schema: {yaml_schema.name}",
            )

            # Ensure schema has additionalProperties: false
            schema_dict = yaml_schema.schema.copy()
            self._ensure_additional_properties_false(schema_dict)

            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": yaml_schema.system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": yaml_schema.name.lower().replace(" ", "_"),
                        "strict": True,
                        "schema": schema_dict,
                    },
                },
                timeout=self.config.timeout_seconds,
            )

            content = response.choices[0].message.content
            if not content:
                return ExtractionResult.error_result("Empty response from LLM")

            try:
                data = json.loads(content)
                self.logger.info("YAML schema extraction completed successfully")

                return ExtractionResult.success_result(
                    data=data,
                    model_used=response.model,
                    tokens_used=response.usage.total_tokens if response.usage else None,
                )

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                return ExtractionResult.error_result(f"Invalid JSON response: {e!s}")

        except Exception as e:
            self.logger.error(f"YAML schema extraction failed: {e}")
            return ExtractionResult.error_result(str(e))

    def _ensure_additional_properties_false(self, schema_dict: dict[str, Any]) -> None:
        """Recursively ensure all objects have additionalProperties: false."""
        if isinstance(schema_dict, dict):
            if schema_dict.get("type") == "object":
                schema_dict["additionalProperties"] = False

            # Recursively process nested schemas
            for key, value in schema_dict.items():
                if key in ["properties", "items", "anyOf", "allOf", "oneOf"]:
                    if isinstance(value, dict):
                        self._ensure_additional_properties_false(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                self._ensure_additional_properties_false(item)
                elif isinstance(value, dict):
                    self._ensure_additional_properties_false(value)
