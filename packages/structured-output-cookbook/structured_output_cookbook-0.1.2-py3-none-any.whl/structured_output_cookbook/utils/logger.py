"""Logging configuration using Loguru."""

import sys
from typing import Any

from loguru import logger

from ..config import Config


def setup_logger(config: Config) -> None:
    """Configure loguru logger based on config."""
    logger.remove()

    if config.log_format == "json":
        format_str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    else:
        format_str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {message}"

    logger.add(
        sys.stderr,
        format=format_str,
        level=config.log_level,
        serialize=config.log_format == "json",
    )


def setup_minimal_logger(level: str = "WARNING") -> None:
    """Configure a minimal logger format ideal for notebooks.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Default is WARNING to reduce noise in notebooks.
    """
    logger.remove()

    # Minimal format: just level and message
    format_str = "<level>{level}</level>: {message}"

    logger.add(sys.stderr, format=format_str, level=level.upper(), colorize=True)


def get_logger(name: str) -> Any:
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)
