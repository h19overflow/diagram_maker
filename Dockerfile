# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer (faster than pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create a non-root user for security (CKV_DOCKER_3 compliance)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy dependency files first for better Docker layer caching
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser requirements.txt ./

# Copy .env file if it exists (optional - can also pass env vars at runtime)
COPY --chown=appuser:appuser .env* ./

# Copy the entire project code (needed for uv pip install .)
COPY --chown=appuser:appuser . .

# Install Python dependencies using uv
# First install from pyproject.toml, then from requirements.txt
RUN uv pip install --system . && \
    uv pip install --system -r requirements.txt

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

