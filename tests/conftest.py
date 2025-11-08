"""Pytest configuration and fixtures."""

import os
import tempfile
import asyncio
from pathlib import Path
from typing import Generator, Dict, Any

import pytest
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config() -> dict:
    """Sample configuration dictionary."""
    return {
        "app": {
            "name": "test-app",
            "version": "1.0.0",
            "debug": True,
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {"username": "admin", "password": "secret"},
        },
        "features": ["auth", "logging", "metrics"],
    }


@pytest.fixture
def config_file(temp_dir: Path, sample_config: dict) -> Path:
    """Create temporary config file."""
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(sample_config, f)
    return config_path


@pytest.fixture
def env_file(temp_dir: Path) -> Path:
    """Create temporary .env file."""
    env_path = temp_dir / ".env"
    with open(env_path, "w") as f:
        f.write("TEST_VAR=test_value\n")
        f.write("TEST_INT=42\n")
        f.write("TEST_BOOL=true\n")
        f.write("TEST_LIST=a,b,c\n")
    return env_path


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    # Store original env
    original_env = dict(os.environ)

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Event Loop Fixtures (for async tests)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Cache Fixtures
# ============================================================================

@pytest.fixture
def cache_config() -> Dict[str, Any]:
    """Cache configuration for tests."""
    return {
        "backend": "memory",
        "ttl": 300,
        "max_size": 100,
        "serializer": "json"
    }


@pytest.fixture
def sample_cache_data() -> Dict[str, Any]:
    """Sample data for cache tests."""
    return {
        "user:1": {"id": 1, "name": "Alice", "email": "alice@example.com"},
        "user:2": {"id": 2, "name": "Bob", "email": "bob@example.com"},
        "product:1": {"id": 1, "name": "Laptop", "price": 1299.99},
        "product:2": {"id": 2, "name": "Mouse", "price": 29.99}
    }


# ============================================================================
# Rate Limiting Fixtures
# ============================================================================

@pytest.fixture
def rate_limit_config() -> Dict[str, Any]:
    """Rate limiter configuration for tests."""
    return {
        "algorithm": "token_bucket",
        "rate": 100,  # 100 requests
        "period": 60,  # per 60 seconds
        "burst": 10   # allow burst of 10
    }


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def sample_users() -> list[Dict[str, Any]]:
    """Sample user data for tests."""
    return [
        {"id": 1, "username": "alice", "email": "alice@example.com", "active": True},
        {"id": 2, "username": "bob", "email": "bob@example.com", "active": True},
        {"id": 3, "username": "charlie", "email": "charlie@example.com", "active": False},
    ]


@pytest.fixture
def sample_products() -> list[Dict[str, Any]]:
    """Sample product data for tests."""
    return [
        {"id": 1, "sku": "LAP001", "name": "Laptop", "price": 1299.99, "stock": 50},
        {"id": 2, "sku": "MOU001", "name": "Mouse", "price": 29.99, "stock": 200},
        {"id": 3, "sku": "KEY001", "name": "Keyboard", "price": 89.99, "stock": 150},
    ]


@pytest.fixture
def sample_events() -> list[Dict[str, Any]]:
    """Sample events for event bus tests."""
    return [
        {"type": "user.created", "user_id": 1, "timestamp": "2024-01-01T00:00:00Z"},
        {"type": "user.updated", "user_id": 1, "timestamp": "2024-01-02T00:00:00Z"},
        {"type": "product.created", "product_id": 1, "timestamp": "2024-01-03T00:00:00Z"},
    ]


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def large_dataset() -> list[int]:
    """Large dataset for performance tests."""
    return list(range(10000))


@pytest.fixture
def performance_thresholds() -> Dict[str, float]:
    """Performance thresholds in seconds."""
    return {
        "lru_cache_operation": 0.00001,  # 10 microseconds per op (100K ops/sec)
        "rate_limit_check": 0.00001,     # 10 microseconds per check
        "event_dispatch": 0.000001,      # 1 microsecond per event (1M events/sec)
        "config_get": 0.000001,          # 1 microsecond per get
    }


# ============================================================================
# Hypothesis Configuration (Property-Based Testing)
# ============================================================================

try:
    from hypothesis import settings, Verbosity

    # Configure hypothesis profiles
    settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
    settings.register_profile("dev", max_examples=100)
    settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)

    # Load profile from environment or use default
    settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
except ImportError:
    # Hypothesis not installed, skip configuration
    pass
