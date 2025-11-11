#!/bin/bash
# Comprehensive test runner for High-Performance REST API

set -e

echo "========================================="
echo "High-Performance REST API - Test Suite"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

echo ""
echo "========================================="
echo "Running Unit Tests"
echo "========================================="
pytest tests/unit/ -v -m unit --tb=short
UNIT_EXIT=$?

echo ""
echo "========================================="
echo "Running Integration Tests"
echo "========================================="
pytest tests/integration/ -v -m integration --tb=short
INTEGRATION_EXIT=$?

echo ""
echo "========================================="
echo "Running Performance Benchmarks"
echo "========================================="
pytest tests/benchmarks/ -v -m benchmark --tb=short
BENCHMARK_EXIT=$?

echo ""
echo "========================================="
echo "Generating Coverage Report"
echo "========================================="
pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml -m "unit or integration"
COVERAGE_EXIT=$?

echo ""
echo "========================================="
echo "Test Results Summary"
echo "========================================="

if [ $UNIT_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Unit Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Unit Tests: FAILED${NC}"
fi

if [ $INTEGRATION_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Integration Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Integration Tests: FAILED${NC}"
fi

if [ $BENCHMARK_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Performance Benchmarks: PASSED${NC}"
else
    echo -e "${RED}✗ Performance Benchmarks: FAILED${NC}"
fi

if [ $COVERAGE_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Coverage Report: GENERATED${NC}"
    echo -e "  View coverage report: ${BLUE}open htmlcov/index.html${NC}"
else
    echo -e "${RED}✗ Coverage Report: FAILED${NC}"
fi

echo ""

# Overall exit code
if [ $UNIT_EXIT -eq 0 ] && [ $INTEGRATION_EXIT -eq 0 ] && [ $BENCHMARK_EXIT -eq 0 ]; then
    echo -e "${GREEN}========================================="
    echo "All Tests Passed! ✓"
    echo "=========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================="
    echo "Some Tests Failed ✗"
    echo "=========================================${NC}"
    exit 1
fi
