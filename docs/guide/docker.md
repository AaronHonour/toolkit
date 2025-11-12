# Docker & Local Development Guide

Complete guide for running the Unistax with Docker for local development.

## Quick Start

```bash
# 1. Validate setup
./scripts/validate-docker-setup.sh

# 2. Start all services
make dev

# 3. View logs
make logs

# 4. Stop all services
make down
```

That's it! All 19 backend services, frontend, docs, and infrastructure will be running.

## Prerequisites

- **Docker Desktop**: Install from [docker.com](https://www.docker.com/products/docker-desktop/)
- **Docker Compose**: Included with Docker Desktop (or install separately)
- **Make**: Pre-installed on macOS/Linux, Windows users can use WSL or install manually

### Verify Prerequisites

```bash
docker --version       # Should be 20.10+
docker compose version # Should be 2.0+
make --version        # Any recent version
```

## Architecture Overview

### Multi-Stage Dockerfiles

All Dockerfiles use optimized multi-stage builds:

```
┌─────────────────────────────────────────────┐
│ Stage 1: Base                               │
│ - Python 3.11-slim or Node 20-alpine        │
│ - System dependencies                       │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Stage 2: Builder│    │ Stage 4: Dev    │
│ - Build deps    │    │ - Hot reload    │
│ - Compile       │    │ - Dev tools     │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Stage 3: Prod   │    │ Stage 5: Test   │
│ - Minimal       │    │ - Test runners  │
│ - ~50-200MB     │    │ - Coverage      │
└─────────────────┘    └─────────────────┘
```

**Benefits:**
- Production images: 60-70% smaller
- Faster builds with layer caching
- Separate dev/prod/test environments
- Security: Non-root users in all stages

### Docker Compose Services

```
Infrastructure (5 services)
├── postgres    - PostgreSQL 15        - Port 5432
├── redis       - Redis 7              - Port 6379
├── kafka       - Confluent Kafka 7.5  - Port 9092
├── zookeeper   - Zookeeper            - Port 2181
└── timescale   - TimescaleDB          - Port 5433

Backend (19 services)
├── app01 - E-Commerce Inventory       - Port 8001
├── app02 - Real-Time Analytics        - Port 8002
├── app03 - File Processing            - Port 8003
├── app04 - Microservices Gateway      - Port 8004
├── app05 - Data Export                - Port 8005
├── app06 - Kappa Architecture         - Port 8006
├── app07 - Distributed Tracing        - Port 8007
├── app08 - Multi-Tenant SaaS          - Port 8008
├── app09 - IoT Data Ingestion         - Port 8009
├── app10 - GraphQL Federation         - Port 8010
├── app11 - Webhook Manager            - Port 8011
├── app12 - Search & Autocomplete      - Port 8012
├── app13 - Rate Limiting              - Port 8013
├── app14 - Feature Flags              - Port 8014
├── app15 - Scheduled Jobs             - Port 8015
├── app16 - Notification Service       - Port 8016
├── app17 - Media Processing           - Port 8017
├── app18 - ML Model Serving           - Port 8018
└── app19 - Probabilistic Structures   - Port 8019

Frontend & Docs (2 services)
├── frontend - React/Vite Dev Server   - Port 3000
└── docs     - VitePress Site          - Port 5173
```

## Makefile Commands

### Development

```bash
# Start everything (recommended for first-time setup)
make dev

# Start only infrastructure (useful when developing specific services)
make dev-infra

# Stop all services
make down

# View live logs from all services
make logs

# Show running services status
make ps
```

### Installation

```bash
# Install backend dependencies locally
make install-backend

# Install frontend dependencies locally
make install-frontend
```

### Testing

```bash
# Run backend tests
make test-backend

# Run frontend tests
make test-frontend

# Run all tests
make test
```

### Code Quality

```bash
# Format code (Black, Prettier)
make format

# Run linters (Ruff, ESLint)
make lint

# Security scan (Bandit, Safety, npm audit)
make security
```

### Cleanup

```bash
# Clean build artifacts
make clean

# Remove Docker volumes (WARNING: deletes all data!)
docker compose down -v
```

## Service Details

### Backend Services

Each backend service runs in development mode with:
- **Hot Reload**: Code changes reflect immediately
- **Volume Mounts**: `./src` and `./examples` mounted for live editing
- **Health Checks**: Automatic health monitoring
- **Environment Variables**: Pre-configured database/cache URLs

**Example: App 01 (Inventory)**

```yaml
app01-inventory:
  build:
    context: .
    dockerfile: Dockerfile
    target: development
  ports:
    - "8001:8001"
  environment:
    DATABASE_URL: postgresql://toolkit:toolkit_dev@postgres:5432/toolkit
    REDIS_URL: redis://redis:6379/0
  volumes:
    - ./src:/app/src           # Live code reload
    - ./examples:/app/examples # Live examples reload
  depends_on:
    - postgres
    - redis
```

### Infrastructure Services

#### PostgreSQL
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U toolkit -d toolkit

# View databases
docker compose exec postgres psql -U toolkit -c "\l"

# Connection string
postgresql://toolkit:toolkit_dev@localhost:5432/toolkit
```

#### Redis
```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Check keys
docker compose exec redis redis-cli KEYS "*"

# Connection string
redis://localhost:6379/0
```

#### Kafka
```bash
# List topics
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Create topic
docker compose exec kafka kafka-topics --create --topic test --bootstrap-server localhost:9092

# Connection string
kafka:9092 (from containers)
localhost:9092 (from host)
```

#### TimescaleDB
```bash
# Connect to TimescaleDB
docker compose exec timescale psql -U toolkit -d timeseries

# Connection string
postgresql://toolkit:toolkit_dev@localhost:5433/timeseries
```

### Frontend

React 18 + TypeScript + Vite development server:

```bash
# Access frontend
http://localhost:3000

# View frontend logs
docker compose logs -f frontend

# Run frontend tests
docker compose exec frontend npm test

# Build production bundle
docker compose exec frontend npm run build
```

**Features:**
- Hot Module Replacement (HMR)
- TypeScript type checking
- ESLint + Prettier
- Vitest + Playwright testing
- Atomic Design System

### Documentation

VitePress documentation site with Mermaid diagrams:

```bash
# Access docs
http://localhost:5173

# View docs logs
docker compose logs -f docs

# Build static docs
docker compose exec docs npm run docs:build
```

**Content:**
- 19 pattern implementation guides
- OpenAPI specs for all services
- Architecture diagrams
- API references
- Deployment guides

## Development Workflows

### Workflow 1: Full Stack Development

Start everything and work across services:

```bash
# 1. Start all services
make dev

# 2. Wait for services to be healthy (~1-2 minutes)
docker compose ps

# 3. Access services
open http://localhost:3000  # Frontend
open http://localhost:5173  # Docs
open http://localhost:8001  # Backend API

# 4. Edit code - changes reflect immediately
# Backend: Edit src/ or examples/
# Frontend: Edit frontend/src/
# Docs: Edit docs/

# 5. View logs
make logs

# 6. Stop when done
make down
```

### Workflow 2: Backend-Only Development

Work on backend services without frontend overhead:

```bash
# 1. Start infrastructure only
make dev-infra

# 2. Start specific backend services
docker compose up -d app01-inventory app02-analytics

# 3. View logs for specific services
docker compose logs -f app01-inventory

# 4. Test API endpoints
curl http://localhost:8001/health

# 5. Stop specific services
docker compose stop app01-inventory
```

### Workflow 3: Frontend-Only Development

Work on frontend with API mocking:

```bash
# 1. Start infrastructure + minimal backend
make dev-infra
docker compose up -d app01-inventory

# 2. Start frontend
docker compose up -d frontend

# 3. View frontend logs
docker compose logs -f frontend

# 4. Access frontend
open http://localhost:3000
```

### Workflow 4: Documentation Writing

Work on documentation independently:

```bash
# 1. Start docs only
docker compose up -d docs

# 2. View docs
open http://localhost:5173

# 3. Edit docs/
# Changes reflect immediately with HMR

# 4. Build static site
docker compose exec docs npm run docs:build
```

## Troubleshooting

### Issue: Containers Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker compose logs

# Rebuild containers
docker compose build --no-cache

# Reset everything (WARNING: deletes data)
docker compose down -v
docker compose up -d
```

### Issue: Port Already in Use

```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Stop the process or change ports in docker-compose.yml
```

### Issue: Slow Performance

**On macOS:**
- Docker Desktop → Settings → Resources
- Increase CPUs to 4+
- Increase Memory to 8GB+
- Enable VirtioFS (faster file sharing)

**On Windows:**
- Use WSL 2 backend (much faster than Hyper-V)
- Store code in WSL filesystem, not Windows filesystem

**General:**
```bash
# Remove unused images/volumes
docker system prune -a

# Use named volumes for node_modules
# (already configured in docker-compose.yml)
```

### Issue: Database Connection Errors

```bash
# Wait for database to be ready
docker compose exec postgres pg_isready -U toolkit

# Check health status
docker compose ps

# View database logs
docker compose logs postgres

# Reset database
docker compose down -v postgres
docker compose up -d postgres
```

### Issue: Hot Reload Not Working

**Backend:**
```bash
# Check volume mounts
docker compose exec app01-inventory ls /app/src

# Verify uvicorn --reload is enabled
docker compose logs app01-inventory | grep reload
```

**Frontend:**
```bash
# Check volume mounts
docker compose exec frontend ls /app/src

# Verify Vite HMR
docker compose logs frontend | grep "hmr update"
```

### Issue: Build Failures

```bash
# Clear Docker build cache
docker builder prune -a

# Rebuild from scratch
docker compose build --no-cache --pull

# Check for disk space
docker system df
```

## Performance Optimization

### Build Speed

```bash
# Use BuildKit (faster builds)
export DOCKER_BUILDKIT=1

# Parallel builds
docker compose build --parallel

# Layer caching
# - Dependencies are cached separately from code
# - Change code without reinstalling dependencies
```

### Image Size

Current production image sizes:
- Backend: ~195 MB (Python 3.11-slim base)
- Frontend: ~48 MB (nginx:alpine)
- Docs: ~45 MB (nginx:alpine)

**Optimization techniques used:**
- Multi-stage builds
- Minimal base images (alpine, slim)
- .dockerignore to exclude unnecessary files
- apt-get clean to remove cache
- Virtual environments for Python

### Runtime Performance

```bash
# Resource limits (add to docker-compose.yml)
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## Security Best Practices

### ✅ Implemented

- [x] Non-root users in all containers (toolkit:1000)
- [x] Minimal base images (alpine, slim)
- [x] No secrets in Dockerfiles or docker-compose.yml
- [x] Health checks for all critical services
- [x] Network isolation (custom bridge network)
- [x] Volume permissions (chown toolkit:toolkit)

### 🔒 Production Recommendations

```bash
# Use secrets management
docker compose --env-file .env.production up

# Scan images for vulnerabilities
docker scout cves toolkit-backend

# Enable Docker Content Trust
export DOCKER_CONTENT_TRUST=1

# Use specific image tags (not :latest)
# Already done: postgres:15-alpine, redis:7-alpine

# Limit network exposure
# Expose only necessary ports in production
```

## Production Deployment

### Building Production Images

```bash
# Backend production image
docker compose build --target production app01-inventory

# Frontend production image
docker compose build --target production frontend

# Docs production image
docker compose build --target production docs

# Tag for registry
docker tag toolkit-backend:latest myregistry.com/toolkit-backend:v1.0.0

# Push to registry
docker push myregistry.com/toolkit-backend:v1.0.0
```

### Production docker-compose.yml

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app01-inventory:
    build:
      target: production  # Use production stage
    restart: always      # Auto-restart on failure
    env_file: .env.prod # Load secrets from file
    deploy:
      replicas: 3        # Scale horizontally
      resources:
        limits:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Run in production:
```bash
docker compose -f docker-compose.prod.yml up -d
```

## VS Code Dev Container

For the ultimate development experience, use the VS Code Dev Container:

```bash
# 1. Install VS Code Dev Containers extension
# 2. Open project in VS Code
# 3. F1 → "Dev Containers: Reopen in Container"
# 4. Wait for container to build
# 5. Start coding with full IDE support inside Docker!
```

**Benefits:**
- Complete development environment in Docker
- 25+ pre-installed extensions
- Automatic port forwarding
- Git credential forwarding
- Consistent environment across team

See `.devcontainer/README.md` for more details.

## Validation

Before deploying or sharing your setup, validate it:

```bash
./scripts/validate-docker-setup.sh
```

This checks:
- ✅ Required files exist
- ✅ Dockerfile syntax
- ✅ Security (non-root users)
- ✅ ESM module support
- ✅ Docker Compose services
- ✅ Build targets
- ✅ Health checks
- ✅ Makefile commands

## Additional Resources

- **Docker Compose Documentation**: https://docs.docker.com/compose/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Multi-stage Builds**: https://docs.docker.com/build/building/multi-stage/
- **Docker Security**: https://docs.docker.com/engine/security/

## Support

For issues with the Docker setup:
1. Run validation: `./scripts/validate-docker-setup.sh`
2. Check logs: `make logs`
3. Review troubleshooting section above
4. Open issue on GitHub with logs and error messages

---

**Phase 1.4: Docker & Local Development** ✓ Complete

Next: Phase 2.1 - Production Deployment Strategies
