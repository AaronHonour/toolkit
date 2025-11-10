.PHONY: help dev dev-infra down clean test test-backend test-frontend build logs ps install-backend install-frontend lint format security

# =============================================================================
# Composable Toolkit - Makefile
# One-command setup and management
# =============================================================================

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(BLUE)Composable Toolkit - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Quick Start:$(NC)"
	@echo "  make dev          - Start full stack (all 19 services + infrastructure)"
	@echo "  make dev-infra    - Start only infrastructure (databases, kafka, redis)"
	@echo "  make down         - Stop all services"
	@echo ""
	@echo "$(GREEN)Available Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-18s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Development
# =============================================================================

dev: ## Start full development stack (all services)
	@echo "$(GREEN)Starting full Composable Toolkit stack...$(NC)"
	@echo "This will start:"
	@echo "  - Infrastructure (Postgres, Redis, Kafka, TimescaleDB)"
	@echo "  - 19 Backend Services (ports 8001-8019)"
	@echo "  - Frontend Development Server (port 3000)"
	@echo "  - Documentation Site (port 5173)"
	@echo ""
	@docker compose up -d
	@echo ""
	@echo "$(GREEN)✓ All services started!$(NC)"
	@echo ""
	@echo "$(BLUE)Backend Services:$(NC)"
	@echo "  App 01 (Inventory):        http://localhost:8001"
	@echo "  App 02 (Analytics):        http://localhost:8002"
	@echo "  App 03 (File Processing):  http://localhost:8003"
	@echo "  App 04-19:                 http://localhost:8004-8019"
	@echo ""
	@echo "$(BLUE)Frontend & Docs:$(NC)"
	@echo "  Frontend:                  http://localhost:3000"
	@echo "  Documentation:             http://localhost:5173"
	@echo ""
	@echo "$(YELLOW)View logs:$(NC) make logs"
	@echo "$(YELLOW)Stop all:$(NC)  make down"

dev-infra: ## Start only infrastructure services
	@echo "$(GREEN)Starting infrastructure services...$(NC)"
	@docker compose up -d postgres redis kafka zookeeper timescale
	@echo "$(GREEN)✓ Infrastructure ready!$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker compose down
	@echo "$(GREEN)✓ All services stopped$(NC)"

logs: ## Show logs from all services
	@docker compose logs -f

ps: ## Show running services
	@docker compose ps

# =============================================================================
# Installation
# =============================================================================

install-backend: ## Install backend dependencies
	@pip install -e ".[dev,all]"

install-frontend: ## Install frontend dependencies
	@cd frontend && npm ci

install: install-backend install-frontend ## Install all dependencies

# =============================================================================
# Testing
# =============================================================================

test-backend: ## Run backend tests
	@pytest -v --cov=src/toolkit --cov-report=term --cov-report=html

test-frontend: ## Run frontend tests
	@cd frontend && npm test -- --run

test: test-backend test-frontend ## Run all tests

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run all linters
	@ruff check src/ tests/
	@black --check src/ tests/
	@cd frontend && npm run lint

format: ## Format all code
	@black src/ tests/
	@cd frontend && npm run format

security: ## Run security scans
	@bandit -r src/
	@safety check
	@cd frontend && npm audit

# =============================================================================
# Cleanup
# =============================================================================

clean: ## Clean up generated files
	@rm -rf build/ dist/ *.egg-info .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete

# =============================================================================
# Building
# =============================================================================

build: clean ## Build package
	@python -m build
