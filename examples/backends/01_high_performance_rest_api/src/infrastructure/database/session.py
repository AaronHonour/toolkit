"""Database session management with connection pooling.

Provides optimized database session management with:
- Connection pooling
- Session lifecycle management
- Transaction support
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from src.infrastructure.database.models import Base


class DatabaseSession:
    """Database session manager with connection pooling.

    Provides high-performance session management with configurable
    connection pooling and lifecycle hooks.
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_pre_ping: bool = True,
        echo: bool = False,
    ):
        """Initialize database session manager.

        Args:
            database_url: Database connection URL
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_pre_ping: Enable connection health checks
            echo: Enable SQL query logging
        """
        self._database_url = database_url
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_pre_ping = pool_pre_ping
        self._echo = echo

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    async def initialize(self) -> None:
        """Initialize database engine and session factory."""
        # Create engine with connection pooling
        self._engine = create_async_engine(
            self._database_url,
            echo=self._echo,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_pre_ping=self._pool_pre_ping,
            # poolclass is automatically set for async engines
            poolclass=NullPool if self._pool_size == 0 else None,
        )

        # Create session factory
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Keep objects usable after commit
        )

    async def create_tables(self) -> None:
        """Create all database tables.

        Only for development/testing. Use Alembic migrations in production.
        """
        if not self._engine:
            await self.initialize()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables.

        Only for development/testing.
        """
        if not self._engine:
            await self.initialize()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup.

        Yields:
            AsyncSession instance

        Example:
            async with db.session() as session:
                result = await session.execute(query)
                await session.commit()
        """
        if not self._session_factory:
            await self.initialize()

        session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        """Close database engine and cleanup connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database session manager
_db_session: Optional[DatabaseSession] = None


def get_session() -> DatabaseSession:
    """Get global database session manager.

    Returns:
        DatabaseSession instance

    Raises:
        RuntimeError: If database not initialized
    """
    global _db_session
    if _db_session is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first."
        )
    return _db_session


async def init_database(
    database_url: str,
    pool_size: int = 20,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    echo: bool = False,
    create_tables: bool = False,
) -> DatabaseSession:
    """Initialize global database session.

    Args:
        database_url: Database connection URL
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        pool_pre_ping: Enable connection health checks
        echo: Enable SQL query logging
        create_tables: Create tables on initialization

    Returns:
        DatabaseSession instance
    """
    global _db_session

    _db_session = DatabaseSession(
        database_url=database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        echo=echo,
    )

    await _db_session.initialize()

    if create_tables:
        await _db_session.create_tables()

    return _db_session


async def close_database() -> None:
    """Close global database session."""
    global _db_session
    if _db_session:
        await _db_session.close()
        _db_session = None
