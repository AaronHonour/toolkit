"""Database module for connection management and ORM integration."""

from unistax.database.connection import DatabaseManager, DatabaseConfig
from unistax.database.session import SessionManager, get_session
from unistax.database.migrations import MigrationManager
from unistax.database.base import Base, TimestampMixin, SoftDeleteMixin
from unistax.database.optimizations import (
    QueryCache,
    QueryCacheConfig,
    PreparedStatementCache,
    QueryBatcher,
    ReadWriteSplitter,
    ConnectionPoolMonitor,
    QueryProfiler,
    cached_query,
    get_query_cache,
    get_prepared_statement_cache,
    get_query_profiler,
)

__all__ = [
    "DatabaseManager",
    "DatabaseConfig",
    "SessionManager",
    "get_session",
    "MigrationManager",
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    # Performance optimizations
    "QueryCache",
    "QueryCacheConfig",
    "PreparedStatementCache",
    "QueryBatcher",
    "ReadWriteSplitter",
    "ConnectionPoolMonitor",
    "QueryProfiler",
    "cached_query",
    "get_query_cache",
    "get_prepared_statement_cache",
    "get_query_profiler",
]
