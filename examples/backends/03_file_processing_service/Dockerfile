# File Processing Service Dockerfile

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

# Create directory for file uploads
RUN mkdir -p /app/uploads /app/outputs

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8004/health')"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "4"]
