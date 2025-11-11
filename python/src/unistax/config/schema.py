"""
Configuration schema validation using Pydantic.

Provides base classes and utilities for defining and validating
configuration schemas.
"""

from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound="ConfigSchema")


class ConfigSchema(BaseModel):
    """
    Base class for configuration schemas.

    Uses Pydantic for validation and type safety.

    Examples:
        >>> class DatabaseConfig(ConfigSchema):
        ...     host: str = "localhost"
        ...     port: int = 5432
        ...     username: str
        ...     password: str
        ...
        >>> config = DatabaseConfig.from_dict({
        ...     "host": "db.example.com",
        ...     "port": 3306,
        ...     "username": "admin",
        ...     "password": "secret"
        ... })
    """

    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields
        validate_assignment=True,  # Validate on attribute assignment
        frozen=False,  # Allow mutation
    )

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create schema instance from dictionary.

        Args:
            data: Configuration data

        Returns:
            Validated schema instance

        Raises:
            ValidationError: If data doesn't match schema
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Export schema as dictionary."""
        return self.model_dump()

    @classmethod
    def from_yaml(cls: Type[T], path: str) -> T:
        """
        Load and validate configuration from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Validated schema instance
        """
        from .loaders import YAMLLoader, EnvInterpolator

        loader = YAMLLoader()
        data = loader.load(path)

        interpolator = EnvInterpolator()
        data = interpolator.interpolate(data)

        return cls.from_dict(data)
