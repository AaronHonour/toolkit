#!/bin/bash
# =============================================================================
# Docker Setup Validation Script
# Validates Docker configuration without requiring Docker to be running
# =============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker Setup Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track validation status
ERRORS=0
WARNINGS=0

# =============================================================================
# Check 1: Required Files Exist
# =============================================================================
echo -e "${BLUE}[1/8] Checking required files...${NC}"

FILES=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    "Makefile"
    "frontend/Dockerfile"
    "frontend/nginx.conf"
    "docs/Dockerfile"
    "docs/nginx.conf"
    "docs/package.json"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# =============================================================================
# Check 2: Dockerfile Syntax
# =============================================================================
echo -e "${BLUE}[2/8] Validating Dockerfile syntax...${NC}"

for dockerfile in "Dockerfile" "frontend/Dockerfile" "docs/Dockerfile"; do
    if [ -f "$dockerfile" ]; then
        if grep -q "^FROM.*as" "$dockerfile"; then
            echo -e "  ${GREEN}✓${NC} $dockerfile (multi-stage)"
        else
            echo -e "  ${YELLOW}⚠${NC} $dockerfile (single-stage)"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
done
echo ""

# =============================================================================
# Check 3: Security - Non-root Users
# =============================================================================
echo -e "${BLUE}[3/8] Checking security (non-root users)...${NC}"

for dockerfile in "Dockerfile" "frontend/Dockerfile"; do
    if [ -f "$dockerfile" ]; then
        if grep -q "USER toolkit" "$dockerfile"; then
            echo -e "  ${GREEN}✓${NC} $dockerfile uses non-root user"
        else
            echo -e "  ${RED}✗${NC} $dockerfile runs as root"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done
echo ""

# =============================================================================
# Check 4: Package.json ESM Support
# =============================================================================
echo -e "${BLUE}[4/8] Checking ESM module support...${NC}"

if [ -f "docs/package.json" ]; then
    if grep -q '"type".*"module"' "docs/package.json"; then
        echo -e "  ${GREEN}✓${NC} docs/package.json has ESM support"
    else
        echo -e "  ${RED}✗${NC} docs/package.json missing 'type: module' (VitePress requires ESM)"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# =============================================================================
# Check 5: Docker Compose Services
# =============================================================================
echo -e "${BLUE}[5/8] Validating docker-compose services...${NC}"

SERVICES=(
    "postgres"
    "redis"
    "kafka"
    "zookeeper"
    "timescale"
    "frontend"
    "docs"
)

for service in "${SERVICES[@]}"; do
    if grep -q "^  $service:" "docker-compose.yml"; then
        echo -e "  ${GREEN}✓${NC} $service"
    else
        echo -e "  ${RED}✗${NC} $service (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for all 19 backend services
BACKEND_COUNT=$(grep -c "^  app[0-9][0-9]" "docker-compose.yml" || echo "0")
if [ "$BACKEND_COUNT" -eq 19 ]; then
    echo -e "  ${GREEN}✓${NC} All 19 backend services defined"
else
    echo -e "  ${RED}✗${NC} Found $BACKEND_COUNT backend services (expected 19)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# =============================================================================
# Check 6: Build Targets
# =============================================================================
echo -e "${BLUE}[6/8] Checking docker-compose build targets...${NC}"

if grep -A5 "^  frontend:" "docker-compose.yml" | grep -q "target: development"; then
    echo -e "  ${GREEN}✓${NC} frontend targets development stage"
else
    echo -e "  ${YELLOW}⚠${NC} frontend build target not specified"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -A5 "^  docs:" "docker-compose.yml" | grep -q "target: development"; then
    echo -e "  ${GREEN}✓${NC} docs targets development stage"
else
    echo -e "  ${RED}✗${NC} docs build target not specified (will fail)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# =============================================================================
# Check 7: Health Checks
# =============================================================================
echo -e "${BLUE}[7/8] Checking health checks...${NC}"

HEALTH_SERVICES=("postgres" "redis" "kafka" "timescale")
for service in "${HEALTH_SERVICES[@]}"; do
    if grep -A15 "^  $service:" "docker-compose.yml" | grep -q "healthcheck:"; then
        echo -e "  ${GREEN}✓${NC} $service has health check"
    else
        echo -e "  ${YELLOW}⚠${NC} $service missing health check"
        WARNINGS=$((WARNINGS + 1))
    fi
done
echo ""

# =============================================================================
# Check 8: Makefile Commands
# =============================================================================
echo -e "${BLUE}[8/8] Validating Makefile commands...${NC}"

MAKE_TARGETS=("dev" "dev-infra" "down" "logs" "ps")
for target in "${MAKE_TARGETS[@]}"; do
    if grep -q "^$target:" "Makefile"; then
        echo -e "  ${GREEN}✓${NC} make $target"
    else
        echo -e "  ${RED}✗${NC} make $target (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for modern docker compose syntax
if grep -q "docker compose" "Makefile"; then
    echo -e "  ${GREEN}✓${NC} Uses modern 'docker compose' syntax"
else
    echo -e "  ${YELLOW}⚠${NC} Uses old 'docker-compose' syntax"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo -e "${GREEN}Your Docker setup is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Build containers:    make dev"
    echo "  2. View logs:           make logs"
    echo "  3. Stop all services:   make down"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo -e "${YELLOW}Your setup will work but has non-critical issues.${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo -e "${RED}Please fix the errors above before building.${NC}"
    exit 1
fi
