"""Configuration Manager implementation.

Provides a thread-safe, cached configuration manager with support for:
- YAML loading
- Nested access with dot notation
- Environment variable interpolation
- Type-safe getters
- Hot-reloading
"""

import threading
from pathlib import Path
from typing import Any, TypeVar

from .loaders import EnvInterpolator, YAMLLoader

T = TypeVar("T")


class ConfigManager:
    """Thread-safe configuration manager with caching and hot-reload support.

    Examples:
        >>> config = ConfigManager.from_yaml("config.yaml")
        >>> db_host = config.get("database.host", default="localhost")
        >>> db_port = config.get_int("database.port", default=5432)
        >>> features = config.get_list("features", default=[])
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """Initialize configuration manager.

        Args:
            data: Initial configuration data
        """
        self._data: dict[str, Any] = data or {}
        self._cache: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._interpolator = EnvInterpolator()

    @classmethod
    def from_yaml(
        cls,
        path: str | Path,
        interpolate: bool = True,
        validate: bool = True,
    ) -> "ConfigManager":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML file
            interpolate: Whether to interpolate environment variables
            validate: Whether to validate configuration

        Returns:
            ConfigManager instance

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid
        """
        loader = YAMLLoader()
        data = loader.load(path)

        if interpolate:
            interpolator = EnvInterpolator()
            data = interpolator.interpolate(data)

        return cls(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfigManager":
        """Create configuration manager from dictionary."""
        return cls(data)

    def get(self, key: str, default: T | None = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key: Configuration key (supports dot notation, e.g., "database.host")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Examples:
            >>> config.get("database.host")
            'localhost'
            >>> config.get("database.credentials.password")
            'secret'
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        value = self._get_nested(key)
        if value is None:
            return default

        # Cache the result
        with self._lock:
            self._cache[key] = value

        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer value."""
        value = self.get(key, default)
        return int(value) if value is not None else default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float value."""
        value = self.get(key, default)
        return float(value) if value is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value.

        Handles string representations: "true", "yes", "1" -> True
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value) if value is not None else default

    def get_list(self, key: str, default: list[Any] | None = None) -> list[Any]:
        """Get list value."""
        value = self.get(key, default or [])
        return list(value) if isinstance(value, (list, tuple)) else default or []

    def get_dict(self, key: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get dictionary value."""
        value = self.get(key, default or {})
        return dict(value) if isinstance(value, dict) else default or {}

    def require(self, key: str) -> Any:
        """Get required configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            ValueError: If key not found
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required configuration key not found: {key}")
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation.

        Args:
            key: Configuration key
            value: Value to set
        """
        with self._lock:
            self._set_nested(key, value)
            # Invalidate cache for this key and parent keys
            self._invalidate_cache(key)

    def update(self, data: dict[str, Any]) -> None:
        """Update configuration with new data.

        Args:
            data: Dictionary to merge into configuration
        """
        with self._lock:
            self._deep_merge(self._data, data)
            self._cache.clear()

    def reload(self, path: str | Path) -> None:
        """Reload configuration from file.

        Args:
            path: Path to YAML file
        """
        loader = YAMLLoader()
        data = loader.load(path)
        data = self._interpolator.interpolate(data)

        with self._lock:
            self._data = data
            self._cache.clear()

    def clear_cache(self) -> None:
        """Clear configuration cache."""
        with self._lock:
            self._cache.clear()

    def to_dict(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return dict(self._data)

    def _get_nested(self, key: str) -> Any:
        """Get nested value using dot notation."""
        keys = key.split(".")
        value = self._data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return None
            else:
                return None

        return value

    def _set_nested(self, key: str, value: Any) -> None:
        """Set nested value using dot notation."""
        keys = key.split(".")
        data = self._data

        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def _invalidate_cache(self, key: str) -> None:
        """Invalidate cache for key and all sub-keys."""
        keys_to_remove = [k for k in self._cache if k.startswith(key)]
        for k in keys_to_remove:
            del self._cache[k]

    def _deep_merge(self, base: dict[str, Any], updates: dict[str, Any]) -> None:
        """Deep merge updates into base dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ConfigManager(keys={list(self._data.keys())})"
