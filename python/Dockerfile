# Multi-stage Dockerfile for Backend Toolkit
# Optimized for size, security, and build speed

# =============================================================================
# Stage 1: Base Python Image
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Stage 2: Dependencies Builder
# =============================================================================
FROM base as builder

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[all]"

# =============================================================================
# Stage 3: Production Runtime
# =============================================================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 unistax && \
    mkdir -p /app /app/backends && \
    chown -R unistax:unistax /app

# Copy virtual environment from builder
COPY --from=builder --chown=unistax:unistax /opt/venv /opt/venv

# Copy application code
WORKDIR /app
COPY --chown=unistax:unistax src/ ./src/

# Switch to non-root user
USER unistax

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (override in docker-compose)
CMD ["python", "-m", "uvicorn", "examples.01_ecommerce_inventory.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage 4: Development Runtime
# =============================================================================
FROM base as development

# Install development dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 unistax && \
    mkdir -p /app /app/backends && \
    chown -R unistax:unistax /app

WORKDIR /app

# Install dependencies (including dev)
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[dev,all]"

# Examples will be mounted as volumes at runtime
# No need to copy them into the image

# Switch to non-root user
USER unistax

# Default command for development (hot reload)
CMD ["python", "-m", "uvicorn", "examples.01_ecommerce_inventory.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Stage 5: Testing Runtime
# =============================================================================
FROM development as testing

USER root

# Install additional testing tools
RUN pip install --no-cache-dir \
    pytest-xdist \
    pytest-timeout

USER unistax

# Run tests by default
CMD ["pytest", "-v", "--cov=src/toolkit", "--cov-report=term", "--cov-report=html"]
