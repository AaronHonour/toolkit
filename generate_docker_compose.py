#!/usr/bin/env python3
"""Generate docker-compose.yml for the new directory structure."""

backends = [
    ("01", "01_high_performance_rest_api", "E-Commerce Inventory"),
    ("02", "02_realtime_analytics_dashboard", "Analytics Dashboard"),
    ("03", "03_file_processing_service", "File Processing Service"),
    ("04", "04_microservices_gateway", "Microservices Gateway"),
    ("05", "05_data_export_service", "Data Export Service"),
    ("06", "06_kappa_architecture", "Kappa Architecture"),
    ("07", "07_event_sourcing", "Event Sourcing"),
    ("08", "08_timeseries_db", "Timeseries DB"),
    ("09", "09_distributed_cache", "Distributed Cache"),
    ("10", "10_message_queue", "Message Queue Manager"),
    ("11", "11_rate_limiter", "Rate Limiter"),
    ("12", "12_lambda_architecture", "Lambda Architecture"),
    ("13", "13_cdc_pipeline", "CDC Pipeline"),
    ("14", "14_recommendation_engine", "Recommendation Engine"),
    ("15", "15_fulltext_search", "Fulltext Search"),
    ("16", "16_feature_store", "Feature Store"),
    ("17", "17_realtime_olap", "Realtime OLAP"),
    ("18", "18_distributed_tracing", "Distributed Tracing"),
    ("19", "19_probabilistic_structures", "Probabilistic Structures"),
]

header = """version: '3.8'

# =============================================================================
# Unistax - Full Stack Docker Compose
# All 19 backend services + frontend + infrastructure
# =============================================================================

networks:
  unistax-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:

services:
"""

backend_template = """  # App {num}: {name}
  app{num}:
    build:
      context: ../python
      dockerfile: Dockerfile
      target: development
    container_name: unistax-app{num}
    working_dir: /app/backends/{dirname}
    command: python -m uvicorn src.main:app --host 0.0.0.0 --port 80{num} --reload
    ports:
      - "80{num}:80{num}"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://unistax:unistax_dev@postgres:5432/unistax
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backends/{dirname}:/app/backends/{dirname}
      - ../python/src:/app/src
    networks:
      - unistax-network
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
"""

frontend_section = """
  # Frontend
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
      target: development
    container_name: unistax-frontend
    working_dir: /app/frontend
    ports:
      - "3000-3019:3000-3019"
    environment:
      - NODE_ENV=development
    volumes:
      - ../frontend:/app/frontend
      - ./frontends:/app/frontends
    networks:
      - unistax-network
    restart: unless-stopped
"""

infra_section = """
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: unistax-postgres
    environment:
      POSTGRES_USER: unistax
      POSTGRES_PASSWORD: unistax_dev
      POSTGRES_DB: unistax
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - unistax-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U unistax"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: unistax-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - unistax-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
"""

def main():
    """Generate docker-compose.yml."""
    with open('examples/docker-compose.yml', 'w') as f:
        f.write(header)

        # Write infrastructure
        f.write(infra_section)

        # Write backend services
        f.write("\n  # Backend Services\n")
        for num, dirname, name in backends:
            service = backend_template.format(num=num, dirname=dirname, name=name)
            f.write(service)

        # Write frontend
        f.write(frontend_section)

    print("docker-compose.yml generated successfully!")

if __name__ == '__main__':
    main()
