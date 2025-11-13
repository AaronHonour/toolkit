"""Database module for connection management and ORM integration."""

from unistax.database.base import Base, SoftDeleteMixin, TimestampMixin
from unistax.database.connection import DatabaseConfig, DatabaseManager
from unistax.database.migrations import MigrationManager
from unistax.database.optimizations import (
    ConnectionPoolMonitor,
    PreparedStatementCache,
    QueryBatcher,
    QueryCache,
    QueryCacheConfig,
    QueryProfiler,
    ReadWriteSplitter,
    cached_query,
    get_prepared_statement_cache,
    get_query_cache,
    get_query_profiler,
)
from unistax.database.session import SessionManager, get_session

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
