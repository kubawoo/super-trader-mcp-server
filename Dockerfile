# Multi-stage build using uv for fast, reproducible builds
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy project source
COPY src ./src

# Install the project
RUN uv sync --frozen --no-dev


# Runtime stage
FROM python:3.13-slim AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --from=builder --chown=appuser:appuser /app/src /app/src

# Copy data files for index constituents
COPY --chown=appuser:appuser data /app/data

# Set working directory
WORKDIR /app

# Switch to non-root user
USER appuser

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Data directory for index CSV files
ENV INDEX_DATA_DIR=/app/data

# Expose the default port
EXPOSE 8000

# Set default port (can be overridden via FASTMCP_PORT)
ENV FASTMCP_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the server
ENTRYPOINT ["super-trader"]