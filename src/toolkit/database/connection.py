"""Database connection management."""

from typing import Any, Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager
from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from toolkit.config import ConfigManager


@dataclass
class DatabaseConfig:
    """Database configuration."""

    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False
    connect_args: Optional[Dict[str, Any]] = None


class DatabaseManager:
    """Database connection and engine management."""

    def __init__(self, config: DatabaseConfig):
        """Initialize database manager.

        Args:
            config: Database configuration
        """
        self.config = config
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None

    @classmethod
    def from_yaml(cls, path: str, prefix: str = "database") -> "DatabaseManager":
        """Create from YAML configuration.

        Args:
            path: Path to YAML file
            prefix: Configuration prefix

        Returns:
            DatabaseManager instance
        """
        config_manager = ConfigManager.from_yaml(path)
        db_config = config_manager.get(prefix, default={})

        config = DatabaseConfig(
            url=db_config.get("url"),
            pool_size=db_config.get("pool_size", 5),
            max_overflow=db_config.get("max_overflow", 10),
            pool_timeout=db_config.get("pool_timeout", 30),
            pool_recycle=db_config.get("pool_recycle", 3600),
            echo=db_config.get("echo", False),
            echo_pool=db_config.get("echo_pool", False),
            connect_args=db_config.get("connect_args"),
        )

        return cls(config)

    def get_engine(self) -> Engine:
        """Get or create database engine.

        Returns:
            SQLAlchemy engine
        """
        if self._engine is None:
            kwargs = {
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
                "pool_recycle": self.config.pool_recycle,
                "echo": self.config.echo,
                "echo_pool": self.config.echo_pool,
            }

            if self.config.connect_args:
                kwargs["connect_args"] = self.config.connect_args

            self._engine = create_engine(self.config.url, **kwargs)

            # Add connection pool events for monitoring
            event.listen(self._engine, "connect", self._on_connect)
            event.listen(self._engine, "checkout", self._on_checkout)

        return self._engine

    def get_session_factory(self) -> sessionmaker:
        """Get session factory.

        Returns:
            SQLAlchemy session factory
        """
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.get_engine(), expire_on_commit=False
            )

        return self._session_factory

    @contextmanager
    def session(self):
        """Create a session context.

        Yields:
            Database session
        """
        session_factory = self.get_session_factory()
        session = session_factory()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self):
        """Dispose of database connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None

    def _on_connect(self, dbapi_conn, connection_record):
        """Handle connection event."""
        # Can add custom connection setup here
        pass

    def _on_checkout(self, dbapi_conn, connection_record, connection_proxy):
        """Handle checkout event."""
        # Can add connection checkout tracking here
        pass

    def health_check(self) -> bool:
        """Check database health.

        Returns:
            True if database is healthy
        """
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
