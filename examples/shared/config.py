"""Configuration management for example applications.

Provides consistent configuration patterns across examples.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from toolkit.config import ConfigManager
from toolkit.env import EnvironmentManager


@dataclass
class DatabaseConfig:
    """Database configuration."""

    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class CacheConfig:
    """Cache configuration."""

    backend: str = "redis"
    redis_url: Optional[str] = "redis://localhost:6379/0"
    default_ttl: int = 300
    l1_cache_size: int = 10000


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""

    enable_query_cache: bool = True
    query_cache_size: int = 10000
    enable_compression: bool = True
    compression_threshold: int = 1024
    enable_serialization_optimization: bool = True
    object_pool_size: int = 100


@dataclass
class APIConfig:
    """API server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    log_level: str = "info"


@dataclass
class ExampleConfig:
    """Complete example application configuration."""

    app_name: str
    environment: str
    debug: bool
    database: DatabaseConfig
    cache: CacheConfig
    performance: PerformanceConfig
    api: APIConfig

    @classmethod
    def from_yaml(cls, config_path: str) -> "ExampleConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Loaded configuration
        """
        config = ConfigManager.from_yaml(config_path)

        return cls(
            app_name=config.get("app.name", "example-app"),
            environment=config.get("app.environment", "development"),
            debug=config.get_bool("app.debug", False),
            database=DatabaseConfig(
                url=config.get("database.url", "sqlite:///./data.db"),
                pool_size=config.get_int("database.pool_size", 10),
                max_overflow=config.get_int("database.max_overflow", 20),
                echo=config.get_bool("database.echo", False),
            ),
            cache=CacheConfig(
                backend=config.get("cache.backend", "redis"),
                redis_url=config.get("cache.redis_url", "redis://localhost:6379/0"),
                default_ttl=config.get_int("cache.default_ttl", 300),
                l1_cache_size=config.get_int("cache.l1_cache_size", 10000),
            ),
            performance=PerformanceConfig(
                enable_query_cache=config.get_bool("performance.enable_query_cache", True),
                query_cache_size=config.get_int("performance.query_cache_size", 10000),
                enable_compression=config.get_bool("performance.enable_compression", True),
                compression_threshold=config.get_int("performance.compression_threshold", 1024),
                enable_serialization_optimization=config.get_bool(
                    "performance.enable_serialization_optimization", True
                ),
                object_pool_size=config.get_int("performance.object_pool_size", 100),
            ),
            api=APIConfig(
                host=config.get("api.host", "0.0.0.0"),
                port=config.get_int("api.port", 8000),
                workers=config.get_int("api.workers", 4),
                reload=config.get_bool("api.reload", False),
                log_level=config.get("api.log_level", "info"),
            ),
        )

    @classmethod
    def from_env(cls, app_name: str = "example-app") -> "ExampleConfig":
        """Load configuration from environment variables.

        Args:
            app_name: Application name

        Returns:
            Configuration from environment
        """
        env = EnvironmentManager()

        return cls(
            app_name=app_name,
            environment=env.get("ENVIRONMENT", "development"),
            debug=env.get_bool("DEBUG", False),
            database=DatabaseConfig(
                url=env.get("DATABASE_URL", "sqlite:///./data.db"),
                pool_size=env.get_int("DATABASE_POOL_SIZE", 10),
                max_overflow=env.get_int("DATABASE_MAX_OVERFLOW", 20),
                echo=env.get_bool("DATABASE_ECHO", False),
            ),
            cache=CacheConfig(
                backend=env.get("CACHE_BACKEND", "redis"),
                redis_url=env.get("REDIS_URL", "redis://localhost:6379/0"),
                default_ttl=env.get_int("CACHE_TTL", 300),
                l1_cache_size=env.get_int("L1_CACHE_SIZE", 10000),
            ),
            performance=PerformanceConfig(
                enable_query_cache=env.get_bool("ENABLE_QUERY_CACHE", True),
                query_cache_size=env.get_int("QUERY_CACHE_SIZE", 10000),
                enable_compression=env.get_bool("ENABLE_COMPRESSION", True),
                compression_threshold=env.get_int("COMPRESSION_THRESHOLD", 1024),
                enable_serialization_optimization=env.get_bool(
                    "ENABLE_SERIALIZATION_OPTIMIZATION", True
                ),
                object_pool_size=env.get_int("OBJECT_POOL_SIZE", 100),
            ),
            api=APIConfig(
                host=env.get("API_HOST", "0.0.0.0"),
                port=env.get_int("API_PORT", 8000),
                workers=env.get_int("API_WORKERS", 4),
                reload=env.get_bool("API_RELOAD", False),
                log_level=env.get("LOG_LEVEL", "info"),
            ),
        )


def load_config(config_path: Optional[str] = None) -> ExampleConfig:
    """Load configuration from file or environment.

    Args:
        config_path: Optional path to configuration file.
                    If not provided, loads from environment.

    Returns:
        Application configuration
    """
    if config_path and Path(config_path).exists():
        return ExampleConfig.from_yaml(config_path)
    else:
        return ExampleConfig.from_env()
