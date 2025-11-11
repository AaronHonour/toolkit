# Real-Time Analytics Dashboard Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy toolkit (parent directory)
COPY ../../ /toolkit

# Install toolkit
RUN pip install --no-cache-dir /toolkit

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
