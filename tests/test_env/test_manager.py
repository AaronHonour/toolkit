"""Tests for environment manager."""

import os
from pathlib import Path

import pytest

from unistax.env import EnvManager, Environment


class TestEnvManager:
    """Test EnvManager class."""

    def test_init_default(self):
        """Test default initialization."""
        env = EnvManager(load_env_file=False)
        assert env.get_environment() in [
            Environment.DEVELOPMENT,
            Environment.TESTING,
            Environment.STAGING,
            Environment.PRODUCTION,
        ]

    def test_init_with_environment(self):
        """Test initialization with specific environment."""
        env = EnvManager(environment=Environment.PRODUCTION, load_env_file=False)
        assert env.get_environment() == Environment.PRODUCTION

    def test_get_existing_var(self):
        """Test getting existing environment variable."""
        os.environ["TEST_VAR"] = "test_value"
        env = EnvManager(load_env_file=False)
        assert env.get("TEST_VAR") == "test_value"

    def test_get_missing_var(self):
        """Test getting missing variable with default."""
        env = EnvManager(load_env_file=False)
        assert env.get("MISSING_VAR", default="default") == "default"

    def test_require_existing_var(self):
        """Test requiring existing variable."""
        os.environ["REQUIRED_VAR"] = "value"
        env = EnvManager(load_env_file=False)
        assert env.require("REQUIRED_VAR") == "value"

    def test_require_missing_var(self):
        """Test requiring missing variable."""
        env = EnvManager(load_env_file=False)
        with pytest.raises(ValueError, match="Required environment variable not set"):
            env.require("MISSING_VAR")

    def test_get_int(self):
        """Test getting integer value."""
        os.environ["INT_VAR"] = "42"
        env = EnvManager(load_env_file=False)
        assert env.get_int("INT_VAR") == 42
        assert env.get_int("MISSING", default=10) == 10

    def test_get_int_invalid(self):
        """Test getting invalid integer."""
        os.environ["INVALID_INT"] = "not_a_number"
        env = EnvManager(load_env_file=False)
        with pytest.raises(ValueError):
            env.get_int("INVALID_INT")

    def test_get_float(self):
        """Test getting float value."""
        os.environ["FLOAT_VAR"] = "3.14"
        env = EnvManager(load_env_file=False)
        assert env.get_float("FLOAT_VAR") == 3.14
        assert env.get_float("MISSING", default=1.0) == 1.0

    def test_get_bool(self):
        """Test getting boolean value."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("yes", True),
            ("1", True),
            ("on", True),
            ("false", False),
            ("no", False),
            ("0", False),
            ("off", False),
        ]

        env = EnvManager(load_env_file=False)

        for value, expected in test_cases:
            os.environ["BOOL_VAR"] = value
            assert env.get_bool("BOOL_VAR") == expected

    def test_get_list(self):
        """Test getting list value."""
        os.environ["LIST_VAR"] = "a,b,c"
        env = EnvManager(load_env_file=False)
        assert env.get_list("LIST_VAR") == ["a", "b", "c"]

    def test_get_list_with_custom_separator(self):
        """Test getting list with custom separator."""
        os.environ["LIST_VAR"] = "a:b:c"
        env = EnvManager(load_env_file=False)
        assert env.get_list("LIST_VAR", separator=":") == ["a", "b", "c"]

    def test_get_list_strips_whitespace(self):
        """Test that list items are stripped of whitespace."""
        os.environ["LIST_VAR"] = "a , b , c"
        env = EnvManager(load_env_file=False)
        assert env.get_list("LIST_VAR") == ["a", "b", "c"]

    def test_get_dict(self):
        """Test getting dictionary value."""
        os.environ["DICT_VAR"] = "key1=value1,key2=value2"
        env = EnvManager(load_env_file=False)
        result = env.get_dict("DICT_VAR")
        assert result == {"key1": "value1", "key2": "value2"}

    def test_set(self):
        """Test setting environment variable."""
        env = EnvManager(load_env_file=False)
        env.set("NEW_VAR", "new_value")
        assert os.environ["NEW_VAR"] == "new_value"
        assert env.get("NEW_VAR") == "new_value"

    def test_add_required(self):
        """Test adding required variable."""
        env = EnvManager(load_env_file=False)
        env.add_required("REQUIRED_VAR")

        with pytest.raises(ValueError, match="Missing required environment variables"):
            env.validate_required()

    def test_validate_required_success(self):
        """Test successful required variable validation."""
        os.environ["REQUIRED_VAR"] = "value"
        env = EnvManager(load_env_file=False)
        env.add_required("REQUIRED_VAR")
        env.validate_required()  # Should not raise

    def test_is_environment_checks(self):
        """Test environment type checks."""
        env = EnvManager(environment=Environment.DEVELOPMENT, load_env_file=False)
        assert env.is_development() is True
        assert env.is_production() is False

        env = EnvManager(environment=Environment.PRODUCTION, load_env_file=False)
        assert env.is_production() is True
        assert env.is_development() is False

    def test_to_dict(self):
        """Test exporting to dictionary."""
        env = EnvManager(load_env_file=False)
        env.set("VAR1", "value1")
        env.set("VAR2", "value2")
        exported = env.to_dict()
        assert "VAR1" in exported
        assert "VAR2" in exported

    def test_detect_environment(self):
        """Test environment detection from ENV variable."""
        os.environ["ENV"] = "production"
        env = EnvManager(load_env_file=False)
        assert env.get_environment() == Environment.PRODUCTION

    def test_load_env_file(self, env_file: Path):
        """Test loading from .env file."""
        env = EnvManager(env_file=env_file)
        assert env.get("TEST_VAR") == "test_value"
        assert env.get_int("TEST_INT") == 42
        assert env.get_bool("TEST_BOOL") is True
