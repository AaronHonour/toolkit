# Docker Deployment Guide

**Last Updated:** 2025-11-10
**Branch:** claude/frontend-review-011CUzoFMaRApxtqZzrpdNb3

This guide explains how to deploy the frontend applications using Docker after the Tailwind CSS styling fix.

---

## Quick Start

### For Development Environment

```bash
# Navigate to project root
cd /home/user/toolkit

# Rebuild the frontend Docker image (REQUIRED after dependency changes)
docker-compose build frontend

# Start the frontend service
docker-compose up frontend

# Or start all services including frontend
docker-compose up
```

### For Production Environment

```bash
# Build production image
docker build -t toolkit-frontend:production \
  --target production \
  -f frontend/Dockerfile \
  ./frontend

# Run production container
docker run -d \
  --name toolkit-frontend-prod \
  -p 8080:8080 \
  toolkit-frontend:production
```

---

## Why Rebuild is Required

The Tailwind CSS fix added new npm dependencies:
- `tailwindcss@4.1.17`
- `postcss@8.5.6`
- `autoprefixer@10.4.21`

**Docker images are immutable**, so existing containers built before these changes won't have these dependencies. You must rebuild the image to include them.

---

## Docker Configuration Overview

### Dockerfile Stages

The frontend `Dockerfile` has multiple stages optimized for different use cases:

#### 1. **Dependencies Stage** (lines 7-19)
```dockerfile
FROM node:20-alpine as dependencies
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline --no-audit
```
- Installs all npm dependencies including new Tailwind packages
- Cached for faster subsequent builds

#### 2. **Builder Stage** (lines 24-40)
```dockerfile
FROM node:20-alpine as builder
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build
```
- Uses dependencies from previous stage
- Builds production bundles with Vite
- **Tailwind CSS is processed here** via PostCSS

#### 3. **Production Stage** (lines 45-76)
```dockerfile
FROM nginx:alpine as production
COPY --from=builder /app/dist /usr/share/nginx/html
```
- Lightweight nginx server
- Serves static files
- No Node.js runtime needed

#### 4. **Development Stage** (lines 81-105)
```dockerfile
FROM node:20-alpine as development
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline --no-audit
```
- Hot reload enabled
- Mounts source code as volume
- **Used by docker-compose.yml**

---

## docker-compose.yml Configuration

The frontend service in `/home/user/toolkit/docker-compose.yml` (lines 561-580):

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    target: development  # Uses development stage
  container_name: toolkit-frontend
  ports:
    - "3000-3019:3000-3019"  # All 19 apps
  volumes:
    - ./frontend:/app        # Mount source code
    - /app/node_modules      # Preserve container's node_modules
```

### Key Points

1. **Target: development**
   - Uses the development Dockerfile stage
   - Includes hot reload for development

2. **Volume Mounts**
   - `./frontend:/app` - Syncs source code changes
   - `/app/node_modules` - Keeps container's npm packages isolated
   - **Result:** Host changes reflect instantly, but npm packages stay in container

3. **Why node_modules is isolated**
   - Host and container may have different OS (macOS/Windows vs Linux)
   - Native dependencies might be incompatible
   - Container has correct architecture-specific builds

---

## Step-by-Step Deployment

### Option 1: Docker Compose (Recommended)

**For First Time Setup:**

```bash
# From project root
cd /home/user/toolkit

# Build and start all services
docker-compose up --build

# Or just the frontend
docker-compose up --build frontend
```

**After Code Changes (No Dependency Changes):**

```bash
# Just restart (hot reload handles code changes)
docker-compose restart frontend
```

**After Dependency Changes (Like This Tailwind Fix):**

```bash
# Rebuild the image
docker-compose build frontend

# Start the service
docker-compose up frontend
```

**To Stop Services:**

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Option 2: Docker CLI

**Development Build:**

```bash
cd /home/user/toolkit/frontend

docker build -t toolkit-frontend:dev \
  --target development \
  .

docker run -d \
  --name toolkit-frontend-dev \
  -p 3000-3019:3000-3019 \
  -v $(pwd):/app \
  -v /app/node_modules \
  toolkit-frontend:dev
```

**Production Build:**

```bash
cd /home/user/toolkit/frontend

docker build -t toolkit-frontend:latest \
  --target production \
  .

docker run -d \
  --name toolkit-frontend-prod \
  -p 8080:8080 \
  toolkit-frontend:latest
```

---

## Verification

### 1. Check Container Status

```bash
# List running containers
docker ps | grep frontend

# View logs
docker-compose logs -f frontend

# Or with Docker CLI
docker logs -f toolkit-frontend
```

### 2. Verify Dependencies Inside Container

```bash
# Access container shell
docker exec -it toolkit-frontend sh

# Check Tailwind is installed
npm list tailwindcss postcss autoprefixer

# Expected output:
# ├── tailwindcss@4.1.17
# ├── postcss@8.5.6
# └── autoprefixer@10.4.21

# Verify PostCSS config exists
ls -la postcss.config.js

# Exit container
exit
```

### 3. Test Application

```bash
# Check health endpoint
curl http://localhost:3000

# Open in browser
# Navigate to http://localhost:3001 (App 01)
# Navigate to http://localhost:3002 (App 02)
# etc.

# Inspect element in browser DevTools
# Verify Tailwind classes generate CSS:
# - bg-primary-600 should have background-color
# - text-neutral-900 should have color
# - etc.
```

---

## Troubleshooting

### Issue 1: Apps Show Unstyled HTML

**Symptom:** Applications load but appear as plain HTML without styling.

**Cause:** Docker image built before Tailwind CSS dependencies were added.

**Solution:**
```bash
# Rebuild the Docker image
docker-compose down
docker-compose build --no-cache frontend
docker-compose up frontend
```

### Issue 2: "Module not found" Errors

**Symptom:** Container logs show errors like "Cannot find module 'tailwindcss'"

**Cause:** node_modules in container is out of sync.

**Solution:**
```bash
# Remove old volumes and rebuild
docker-compose down -v
docker-compose build --no-cache frontend
docker-compose up frontend
```

### Issue 3: Changes Not Reflecting

**Symptom:** Code changes don't appear in the running application.

**Cause:** Volume mount not working or Vite dev server not watching.

**Solution:**
```bash
# Check volume mounts
docker inspect toolkit-frontend | grep -A 10 Mounts

# Restart with proper mounts
docker-compose down
docker-compose up frontend
```

### Issue 4: Port Conflicts

**Symptom:** "Port already in use" error when starting.

**Cause:** Another process is using ports 3000-3019.

**Solution:**
```bash
# Find what's using the ports
lsof -i :3000
lsof -i :3001

# Stop conflicting services or change ports in docker-compose.yml
```

---

## Production Deployment

### Build Optimization

The production Dockerfile stage includes:

1. **Multi-stage build** - Smaller final image (nginx vs full Node.js)
2. **Layer caching** - Dependencies cached separately from source
3. **Security** - Non-root user, minimal attack surface
4. **Health checks** - Automatic container health monitoring

### Environment Variables

Configure environment variables in docker-compose.yml or via CLI:

```yaml
environment:
  VITE_API_BASE_URL: http://api.example.com
  NODE_ENV: production
```

Or with Docker CLI:
```bash
docker run -e VITE_API_BASE_URL=http://api.example.com toolkit-frontend:latest
```

### SSL/HTTPS

For production, use a reverse proxy (nginx, Traefik, Caddy):

```yaml
services:
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/nginx.conf
      - ./ssl-certs:/etc/ssl/certs
    depends_on:
      - frontend
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          cd frontend
          docker build -t frontend:${{ github.sha }} \
            --target production \
            .

      - name: Test image
        run: |
          docker run -d --name test-frontend frontend:${{ github.sha }}
          sleep 5
          curl -f http://localhost:8080 || exit 1

      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker tag frontend:${{ github.sha }} myregistry/frontend:latest
          docker push myregistry/frontend:latest
```

---

## Performance Considerations

### Build Time Optimization

1. **Use .dockerignore** (now included)
   - Excludes node_modules, dist, logs
   - Reduces build context size

2. **Layer Caching**
   - Dependencies installed in separate stage
   - Only rebuilds when package.json changes

3. **BuildKit**
   ```bash
   DOCKER_BUILDKIT=1 docker build -t toolkit-frontend .
   ```

### Runtime Optimization

1. **Production Stage**
   - Uses nginx (much lighter than Node.js)
   - Serves pre-built static files
   - Better performance and lower memory

2. **Resource Limits**
   ```yaml
   frontend:
     deploy:
       resources:
         limits:
           cpus: '1.0'
           memory: 512M
   ```

---

## Summary

### Files Modified for Docker Compatibility

| File | Status | Purpose |
|------|--------|---------|
| `frontend/Dockerfile` | ✅ Already correct | Multi-stage build with all stages |
| `frontend/package.json` | ✅ Updated | Includes Tailwind dependencies |
| `frontend/package-lock.json` | ✅ Updated | Locked dependency versions |
| `frontend/postcss.config.js` | ✅ Created | PostCSS + Tailwind configuration |
| `frontend/.dockerignore` | ✅ Created | Optimizes build context |
| `docker-compose.yml` | ✅ Already correct | Frontend service configuration |

### Required Actions for Docker Users

1. **Rebuild the Docker image** (one-time after this fix):
   ```bash
   docker-compose build frontend
   ```

2. **Start the service**:
   ```bash
   docker-compose up frontend
   ```

3. **Verify styling** in browser at http://localhost:3001-3019

### No Changes Needed

- Dockerfile is already correctly configured
- docker-compose.yml is already correct
- docker-entrypoint.sh is already correct
- All paths and volume mounts are correct

**The Docker setup will work perfectly once rebuilt!** 🐳

---

## Support

If you encounter issues:

1. Check container logs: `docker-compose logs -f frontend`
2. Verify dependencies in container: `docker exec -it toolkit-frontend npm list tailwindcss`
3. Ensure ports are available: `lsof -i :3000-3019`
4. Try clean rebuild: `docker-compose down -v && docker-compose build --no-cache frontend`

For more details, see:
- `frontend/STYLING_ISSUE_ANALYSIS.md` - Root cause analysis
- `frontend/Dockerfile` - Complete Docker configuration
- `docker-compose.yml` - Service orchestration
