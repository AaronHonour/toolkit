#!/bin/bash
# Build Docker services in batches to avoid overwhelming Docker Desktop

set -e

echo "Building Unistax services in batches..."
echo "========================================="

# Batch 1: Infrastructure dependencies (small, fast)
echo ""
echo "[Batch 1/5] Building infrastructure services..."
docker compose build postgres redis loki prometheus jaeger

# Batch 2: First 5 apps
echo ""
echo "[Batch 2/5] Building apps 01-05..."
docker compose build app01 app02 app03 app04 app05

# Batch 3: Next 5 apps
echo ""
echo "[Batch 3/5] Building apps 06-10..."
docker compose build app06 app07 app08 app09 app10

# Batch 4: Next 5 apps
echo ""
echo "[Batch 4/5] Building apps 11-15..."
docker compose build app11 app12 app13 app14 app15

# Batch 5: Final apps + frontend
echo ""
echo "[Batch 5/5] Building apps 16-19 and frontend..."
docker compose build app16 app17 app18 app19 frontend

echo ""
echo "========================================="
echo "All services built successfully!"
echo ""
echo "To start services:"
echo "  docker compose up -d"
echo ""
echo "To run tests:"
echo "  docker compose exec app01 pytest -v"
