# Build stage - install dependencies with build tools
FROM --platform=linux/amd64 python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt ./

# Copy project code (needed for uv pip install .)
COPY . .

# Install Python dependencies using uv
# Filter out Windows-only packages (like pywin32) for Linux container
RUN uv pip install --system . && \
    grep -v "^pywin32" requirements.txt | uv pip install --system -r /dev/stdin && \
    # Clean up Python cache and unnecessary files to reduce image size
    find /usr/local/lib/python3.12/site-packages -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.12/site-packages -type f -name "*.pyc" -delete && \
    find /usr/local/lib/python3.12/site-packages -type f -name "*.pyo" -delete

# Runtime stage - minimal image with only runtime dependencies
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Install only runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

# Create a non-root user for security (CKV_DOCKER_3 compliance)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Copy .env file if it exists (optional - can also pass env vars at runtime)
COPY --chown=appuser:appuser .env* ./

# Switch to non-root user
USER appuser

# Expose the port (default is 8001 based on api_config.py)
EXPOSE 8001

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check using the FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/api/v1/health || exit 1

# Run the FastAPI application using uvicorn
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8001"]

