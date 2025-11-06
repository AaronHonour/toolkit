"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from typing import Generator

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
