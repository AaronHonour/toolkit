"""Tests for configuration loaders."""

import os
from pathlib import Path

import pytest

from unistax.config.loaders import YAMLLoader, EnvInterpolator


class TestYAMLLoader:
    """Test YAMLLoader class."""

    def test_load_valid_file(self, config_file: Path):
        """Test loading valid YAML file."""
        loader = YAMLLoader()
        data = loader.load(config_file)
        assert data["app"]["name"] == "test-app"

    def test_load_missing_file(self):
        """Test loading non-existent file."""
        loader = YAMLLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent.yaml")

    def test_load_invalid_yaml(self, temp_dir: Path):
        """Test loading invalid YAML."""
        invalid_file = temp_dir / "invalid.yaml"
        with open(invalid_file, "w") as f:
            f.write("invalid: yaml: content:")

        loader = YAMLLoader()
        with pytest.raises(ValueError, match="Invalid YAML"):
            loader.load(invalid_file)

    def test_dump(self, temp_dir: Path):
        """Test dumping data to YAML."""
        loader = YAMLLoader()
        data = {"key": "value", "nested": {"key2": "value2"}}
        output_file = temp_dir / "output.yaml"

        loader.dump(data, output_file)

        # Load and verify
        loaded_data = loader.load(output_file)
        assert loaded_data == data


class TestEnvInterpolator:
    """Test EnvInterpolator class."""

    def test_interpolate_simple(self):
        """Test simple variable interpolation."""
        os.environ["VAR"] = "value"
        interpolator = EnvInterpolator()
        result = interpolator.interpolate_string("${VAR}")
        assert result == "value"

    def test_interpolate_in_string(self):
        """Test interpolation within string."""
        os.environ["HOST"] = "localhost"
        interpolator = EnvInterpolator()
        result = interpolator.interpolate_string("Server: ${HOST}")
        assert result == "Server: localhost"

    def test_interpolate_multiple(self):
        """Test multiple variable interpolation."""
        os.environ["HOST"] = "localhost"
        os.environ["PORT"] = "8080"
        interpolator = EnvInterpolator()
        result = interpolator.interpolate_string("${HOST}:${PORT}")
        assert result == "localhost:8080"

    def test_interpolate_with_default(self):
        """Test interpolation with default value."""
        interpolator = EnvInterpolator()
        result = interpolator.interpolate_string("${MISSING:default}")
        assert result == "default"

    def test_interpolate_with_default_dash(self):
        """Test interpolation with :- syntax."""
        interpolator = EnvInterpolator()
        result = interpolator.interpolate_string("${MISSING:-default}")
        assert result == "default"

    def test_interpolate_empty_with_default(self):
        """Test interpolation of empty var with default."""
        os.environ["EMPTY"] = ""
        interpolator = EnvInterpolator()
        # : syntax - use default if unset
        result1 = interpolator.interpolate_string("${EMPTY:default}")
        assert result1 == ""  # Empty string is set, so use it

        # :- syntax - use default if unset or empty
        result2 = interpolator.interpolate_string("${EMPTY:-default}")
        assert result2 == "default"

    def test_interpolate_missing_required(self):
        """Test interpolation of missing required variable."""
        interpolator = EnvInterpolator()
        with pytest.raises(ValueError, match="Required environment variable not set"):
            interpolator.interpolate_string("${REQUIRED_VAR}")

    def test_interpolate_dict(self):
        """Test interpolating dictionary."""
        os.environ["HOST"] = "localhost"
        interpolator = EnvInterpolator()
        data = {"server": {"host": "${HOST}", "port": 8080}}
        result = interpolator.interpolate(data)
        assert result["server"]["host"] == "localhost"
        assert result["server"]["port"] == 8080

    def test_interpolate_list(self):
        """Test interpolating list."""
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "value2"
        interpolator = EnvInterpolator()
        data = ["${VAR1}", "${VAR2}", "static"]
        result = interpolator.interpolate(data)
        assert result == ["value1", "value2", "static"]
