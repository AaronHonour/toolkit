.PHONY: help install install-dev test coverage lint format type-check clean build docs

help:
	@echo "Backend Toolkit - Development Commands"
	@echo ""
	@echo "install          Install package"
	@echo "install-dev      Install package with dev dependencies"
	@echo "test             Run tests"
	@echo "coverage         Run tests with coverage report"
	@echo "lint             Run linter (ruff)"
	@echo "format           Format code (black)"
	@echo "type-check       Run type checker (mypy)"
	@echo "clean            Clean build artifacts"
	@echo "build            Build package"
	@echo "all              Run format, lint, type-check, and test"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest -v

coverage:
	pytest --cov=src/toolkit --cov-report=term-missing --cov-report=html

lint:
	ruff check src/ tests/

format:
	black src/ tests/

type-check:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

all: format lint type-check test
	@echo "All checks passed!"
