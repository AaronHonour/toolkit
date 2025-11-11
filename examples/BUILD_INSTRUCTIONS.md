# Building Unistax Examples

This guide explains how to build all example services without overwhelming Docker Desktop.

## Problem

Building all 20+ services at once with `docker compose build` can crash Docker Desktop due to:
- High memory usage (100+ packages per service)
- CPU overload (20 parallel builds)
- Disk I/O saturation
- Windows Docker Desktop resource limits

## Solution: Batch Building

We provide scripts that build services in manageable batches of 5-8 services at a time.

## Usage

### Option 1: Python Script (Recommended - Cross Platform)

```bash
cd examples
python build-batches.py
```

**Advantages:**
- Works on Windows, macOS, Linux
- Shows progress and timing
- Automatic error handling
- Pauses between batches

### Option 2: Windows Batch File

```cmd
cd examples
build-batches.bat
```

### Option 3: Bash Script (Git Bash/WSL)

```bash
cd examples
bash build-batches.sh
```

## What Gets Built

The scripts build in this order:

1. **Infrastructure** (8 services): postgres, redis, zookeeper, kafka, loki, prometheus, jaeger, timescale
2. **Apps 01-05**: REST API, Analytics, File Processor, Gateway, Data Export
3. **Apps 06-10**: Kappa, Event Sourcing, TimeSeries, Cache, Message Queue
4. **Apps 11-15**: Rate Limiter, Lambda, CDC, Recommendations, Search
5. **Apps 16-19 + Frontend**: Feature Store, OLAP, Tracing, Probabilistic + React frontend

## After Building

### Start All Services

```bash
docker compose up -d
```

### Start Subset (Faster)

```bash
# Just core infrastructure + a few apps
docker compose up -d postgres redis app01 app03 frontend
```

### Check Status

```bash
docker compose ps
```

### Run Tests

```bash
# Run tests in app01
docker compose exec app01 pytest -v

# Run tests in all apps (one at a time)
for i in {01..19}; do
  echo "Testing app$i..."
  docker compose exec app$i pytest -v || true
done
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app01

# Last 50 lines
docker compose logs --tail=50 frontend
```

### Stop Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove containers (keeps images)
docker compose down

# Stop, remove containers, and remove volumes (clean slate)
docker compose down -v
```

## Troubleshooting

### Docker Desktop Crashes During Build

**Symptom**: Build hangs, Docker Desktop becomes unresponsive, or you see "EOF" errors

**Solution**:
1. Restart Docker Desktop
2. Use the batch build scripts above
3. If still failing, reduce batch size in the script

### Out of Disk Space

**Symptom**: "no space left on device" errors

**Solution**:
```bash
# Clean up old images and build cache
docker system prune -a

# See disk usage
docker system df
```

### Build Cache Issues

**Symptom**: Changes not reflected, or weird build errors

**Solution**:
```bash
# Rebuild without cache (one service)
docker compose build --no-cache app01

# Rebuild all without cache (use batch script instead)
python build-batches.py  # Already uses --no-cache
```

### Port Conflicts

**Symptom**: "port is already allocated" errors

**Solution**:
```bash
# Stop other services using the same ports
docker compose down

# Or edit docker-compose.yml to use different ports
```

## Performance Tips

1. **Increase Docker Desktop Resources**
   - Settings → Resources → Advanced
   - Increase CPUs to at least 4
   - Increase Memory to at least 8GB

2. **Enable WSL 2 Backend** (Windows only)
   - Settings → General → Use WSL 2 based engine
   - Much better performance than Hyper-V

3. **Build Only What You Need**
   ```bash
   # Just build specific services
   docker compose build app01 app03 frontend
   ```

4. **Use Build Cache**
   - Don't use `--no-cache` unless necessary
   - The batch scripts will automatically use cache

## Quick Start (After Building)

```bash
# 1. Start core services
docker compose up -d postgres redis frontend app01

# 2. Wait for startup (30 seconds)
sleep 30

# 3. Test the API
curl http://localhost:8001/health

# 4. Test the frontend
curl http://localhost:3000

# 5. Run tests
docker compose exec app01 pytest -v
```
