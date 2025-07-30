# Use Python 3.13 slim image as base
FROM python:3.13-slim-bookworm as builder

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY uv.lock pyproject.toml ./

# Install dependencies into a virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable

# Copy the project source code
COPY . .

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

# Production stage
FROM python:3.13-slim-bookworm

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Copy the virtual environment from builder stage
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy the application code
COPY --from=builder --chown=app:app /app /app

# Set working directory and user
WORKDIR /app
USER app

# Add the virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create directories for data and config
RUN mkdir -p /app/data /app/config/schemas

# Set environment variables
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

# Default command - show help
CMD ["structured-output", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from structured_output_cookbook.config import Config; Config.from_env()" || exit 1

# Labels for better container management
LABEL name="structured-output-cookbook"
LABEL version="0.1.0"
LABEL description="LLM-powered structured output extraction with predefined and custom schemas"
LABEL maintainer="Saverio Mazza <saverio3107@gmail.com>" 