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
RUN useradd -m -u 1000 toolkit && \
    mkdir -p /app && \
    chown -R toolkit:toolkit /app

# Copy virtual environment from builder
COPY --from=builder --chown=toolkit:toolkit /opt/venv /opt/venv

# Copy application code
WORKDIR /app
COPY --chown=toolkit:toolkit src/ ./src/
COPY --chown=toolkit:toolkit configs/ ./configs/
COPY --chown=toolkit:toolkit examples/ ./examples/

# Switch to non-root user
USER toolkit

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
RUN useradd -m -u 1000 toolkit && \
    mkdir -p /app && \
    chown -R toolkit:toolkit /app

WORKDIR /app

# Install dependencies (including dev)
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[dev,all]"

# Copy application code
COPY --chown=toolkit:toolkit . .

# Switch to non-root user
USER toolkit

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

USER toolkit

# Run tests by default
CMD ["pytest", "-v", "--cov=src/toolkit", "--cov-report=term", "--cov-report=html"]
