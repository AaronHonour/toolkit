"""Configuration loaders and processors.

Provides utilities for loading configuration from various sources
and processing them (e.g., environment variable interpolation).
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class YAMLLoader:
    """YAML file loader with error handling.

    Supports safe loading and provides detailed error messages.
    """

    def load(self, path: str | Path) -> dict[str, Any]:
        """Load YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}") from e

    def dump(self, data: dict[str, Any], path: str | Path) -> None:
        """Dump data to YAML file.

        Args:
            data: Data to dump
            path: Output file path
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


class EnvInterpolator:
    """Environment variable interpolator.

    Supports syntax:
    - ${VAR_NAME} - Required variable
    - ${VAR_NAME:default} - Variable with default value
    - ${VAR_NAME:-default} - Variable with default if empty/unset

    Examples:
        >>> interpolator = EnvInterpolator()
        >>> interpolator.interpolate_string("Host: ${DB_HOST:localhost}")
        'Host: localhost'
    """

    # Pattern: ${VAR_NAME} or ${VAR_NAME:default} or ${VAR_NAME:-default}
    ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+)(?:(:-|:)([^}]*))?\}")

    def interpolate(self, data: Any) -> Any:
        """Recursively interpolate environment variables in data structure.

        Args:
            data: Data to interpolate (dict[str, Any], list[Any], or string)

        Returns:
            Data with interpolated values
        """
        if isinstance(data, dict):
            return {k: self.interpolate(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.interpolate(item) for item in data]
        elif isinstance(data, str):
            return self.interpolate_string(data)
        else:
            return data

    def interpolate_string(self, value: str) -> str:
        """Interpolate environment variables in a string.

        Args:
            value: String potentially containing environment variable references

        Returns:
            String with interpolated values

        Raises:
            ValueError: If required environment variable is not set
        """

        def replace_var(match: re.Match[str]) -> str:
            var_name = match.group(1)
            separator = match.group(2)  # : or :-
            default_value = match.group(3) if match.group(3) is not None else ""

            env_value = os.environ.get(var_name)

            # No separator: variable is required
            if separator is None:
                if env_value is None:
                    raise ValueError(f"Required environment variable not set: {var_name}")
                return env_value

            # :- separator: use default if variable is unset or empty
            if separator == ":-":
                if not env_value:
                    return default_value
                return env_value

            # : separator: use default if variable is unset
            if separator == ":":
                if env_value is None:
                    return default_value
                return env_value

            return env_value or default_value

        return self.ENV_VAR_PATTERN.sub(replace_var, value)
