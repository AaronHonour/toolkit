"""Tests for configuration manager."""

import os
from pathlib import Path

import pytest

from unistax.config import ConfigManager


class TestConfigManager:
    """Test ConfigManager class."""

    def test_init_empty(self):
        """Test initialization with no data."""
        config = ConfigManager()
        assert config.get("any_key") is None

    def test_init_with_data(self):
        """Test initialization with data."""
        data = {"key": "value"}
        config = ConfigManager(data)
        assert config.get("key") == "value"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {"app": {"name": "test"}}
        config = ConfigManager.from_dict(data)
        assert config.get("app.name") == "test"

    def test_from_yaml(self, config_file: Path):
        """Test loading from YAML file."""
        config = ConfigManager.from_yaml(config_file)
        assert config.get("app.name") == "test-app"
        assert config.get("database.port") == 5432

    def test_from_yaml_missing_file(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            ConfigManager.from_yaml("nonexistent.yaml")

    def test_get_nested(self, sample_config: dict):
        """Test getting nested values."""
        config = ConfigManager(sample_config)
        assert config.get("database.host") == "localhost"
        assert config.get("database.credentials.username") == "admin"

    def test_get_with_default(self, sample_config: dict):
        """Test getting with default value."""
        config = ConfigManager(sample_config)
        assert config.get("nonexistent", default="default") == "default"

    def test_get_int(self, sample_config: dict):
        """Test getting integer value."""
        config = ConfigManager(sample_config)
        assert config.get_int("database.port") == 5432
        assert config.get_int("nonexistent", default=8000) == 8000

    def test_get_bool(self, sample_config: dict):
        """Test getting boolean value."""
        config = ConfigManager(sample_config)
        assert config.get_bool("app.debug") is True
        assert config.get_bool("nonexistent", default=False) is False

    def test_get_bool_from_string(self):
        """Test boolean conversion from string."""
        config = ConfigManager({"flag1": "true", "flag2": "yes", "flag3": "1"})
        assert config.get_bool("flag1") is True
        assert config.get_bool("flag2") is True
        assert config.get_bool("flag3") is True

    def test_get_list(self, sample_config: dict):
        """Test getting list value."""
        config = ConfigManager(sample_config)
        features = config.get_list("features")
        assert features == ["auth", "logging", "metrics"]

    def test_get_dict(self, sample_config: dict):
        """Test getting dictionary value."""
        config = ConfigManager(sample_config)
        creds = config.get_dict("database.credentials")
        assert creds["username"] == "admin"
        assert creds["password"] == "secret"

    def test_require_existing(self, sample_config: dict):
        """Test requiring existing value."""
        config = ConfigManager(sample_config)
        assert config.require("app.name") == "test-app"

    def test_require_missing(self, sample_config: dict):
        """Test requiring missing value."""
        config = ConfigManager(sample_config)
        with pytest.raises(ValueError, match="Required configuration key not found"):
            config.require("nonexistent")

    def test_set(self, sample_config: dict):
        """Test setting value."""
        config = ConfigManager(sample_config)
        config.set("new.key", "value")
        assert config.get("new.key") == "value"

    def test_set_nested(self, sample_config: dict):
        """Test setting nested value."""
        config = ConfigManager(sample_config)
        config.set("new.nested.key", "value")
        assert config.get("new.nested.key") == "value"

    def test_update(self, sample_config: dict):
        """Test updating configuration."""
        config = ConfigManager(sample_config)
        config.update({"app": {"version": "2.0.0"}, "new_key": "value"})
        assert config.get("app.version") == "2.0.0"
        assert config.get("new_key") == "value"
        # Original keys should still exist
        assert config.get("app.name") == "test-app"

    def test_cache(self, sample_config: dict):
        """Test caching mechanism."""
        config = ConfigManager(sample_config)

        # First access
        value1 = config.get("database.host")

        # Modify underlying data
        config._data["database"]["host"] = "newhost"

        # Should get cached value
        value2 = config.get("database.host")
        assert value1 == value2

        # Clear cache and get new value
        config.clear_cache()
        value3 = config.get("database.host")
        assert value3 == "newhost"

    def test_to_dict(self, sample_config: dict):
        """Test exporting to dictionary."""
        config = ConfigManager(sample_config)
        exported = config.to_dict()
        assert exported == sample_config

    def test_env_interpolation(self, config_file: Path):
        """Test environment variable interpolation."""
        os.environ["TEST_HOST"] = "example.com"
        os.environ["TEST_PORT"] = "8080"

        config_path = config_file.parent / "env_config.yaml"
        with open(config_path, "w") as f:
            f.write("host: ${TEST_HOST}\n")
            f.write("port: ${TEST_PORT}\n")

        config = ConfigManager.from_yaml(config_path)
        assert config.get("host") == "example.com"
        assert config.get("port") == "8080"
