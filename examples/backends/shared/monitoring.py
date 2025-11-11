"""Performance monitoring for example applications.

Provides comprehensive monitoring and metrics collection.
"""

import time
from typing import Optional
from contextlib import contextmanager

from unistax.metrics import MetricsManager
from unistax.logging import LoggerManager
from unistax.database import QueryProfiler, get_query_cache


class PerformanceMonitor:
    """Performance monitoring and metrics collection.

    Tracks application performance metrics for optimization.
    """

    def __init__(self, app_name: str):
        """Initialize performance monitor.

        Args:
            app_name: Application name for metric prefixes
        """
        self.app_name = app_name
        self.metrics = MetricsManager()
        self.logger = LoggerManager().get_logger(f"{app_name}.performance")
        self.query_profiler = QueryProfiler()

    @contextmanager
    def track_request(self, endpoint: str, method: str = "GET"):
        """Track API request performance.

        Args:
            endpoint: API endpoint name
            method: HTTP method

        Example:
            with monitor.track_request("/api/products", "GET"):
                response = await get_products()
        """
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            self.metrics.timing(f"{self.app_name}.request.{endpoint}.{method}", duration)
            self.metrics.increment(f"{self.app_name}.request.{endpoint}.{method}.success")

            if duration > 0.1:  # Log slow requests (>100ms)
                self.logger.warning(
                    f"Slow request: {method} {endpoint} took {duration*1000:.2f}ms"
                )

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.increment(f"{self.app_name}.request.{endpoint}.{method}.error")
            self.logger.error(
                f"Request failed: {method} {endpoint} after {duration*1000:.2f}ms - {str(e)}"
            )
            raise

    @contextmanager
    def track_database_query(self, operation: str):
        """Track database query performance.

        Args:
            operation: Query operation name

        Example:
            with monitor.track_database_query("get_product"):
                product = await repo.get_by_id(product_id)
        """
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            self.metrics.timing(f"{self.app_name}.database.{operation}", duration)
            self.query_profiler.profile_query(operation, duration)

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.increment(f"{self.app_name}.database.{operation}.error")
            raise

    @contextmanager
    def track_cache_operation(self, operation: str):
        """Track cache operation performance.

        Args:
            operation: Cache operation name

        Example:
            with monitor.track_cache_operation("get_product"):
                cached = cache.get(product_id)
        """
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            self.metrics.timing(f"{self.app_name}.cache.{operation}", duration)

        except Exception:
            self.metrics.increment(f"{self.app_name}.cache.{operation}.error")
            raise

    def record_cache_hit(self, cache_type: str):
        """Record cache hit.

        Args:
            cache_type: Type of cache (l1, l2, query, etc.)
        """
        self.metrics.increment(f"{self.app_name}.cache.{cache_type}.hits")

    def record_cache_miss(self, cache_type: str):
        """Record cache miss.

        Args:
            cache_type: Type of cache (l1, l2, query, etc.)
        """
        self.metrics.increment(f"{self.app_name}.cache.{cache_type}.misses")

    def get_performance_summary(self) -> dict:
        """Get performance metrics summary.

        Returns:
            Dictionary of performance metrics
        """
        query_stats = self.query_profiler.get_stats()
        cache_stats = get_query_cache().stats() if get_query_cache() else {}

        return {
            "database": {
                "total_queries": query_stats.get("total", 0),
                "avg_duration_ms": query_stats.get("avg_duration", 0) * 1000,
                "p95_duration_ms": query_stats.get("p95_duration", 0) * 1000,
                "p99_duration_ms": query_stats.get("p99_duration", 0) * 1000,
            },
            "cache": {
                "hits": cache_stats.get("hits", 0),
                "misses": cache_stats.get("misses", 0),
                "hit_rate": cache_stats.get("hit_rate", 0),
            },
        }

    def log_performance_summary(self):
        """Log performance summary to console."""
        summary = self.get_performance_summary()

        self.logger.info("=== Performance Summary ===")
        self.logger.info(f"Database Queries: {summary['database']['total_queries']}")
        self.logger.info(f"  Avg Duration: {summary['database']['avg_duration_ms']:.2f}ms")
        self.logger.info(f"  P95 Duration: {summary['database']['p95_duration_ms']:.2f}ms")
        self.logger.info(f"  P99 Duration: {summary['database']['p99_duration_ms']:.2f}ms")
        self.logger.info(f"Cache Hit Rate: {summary['cache']['hit_rate']*100:.1f}%")
        self.logger.info(f"  Hits: {summary['cache']['hits']}")
        self.logger.info(f"  Misses: {summary['cache']['misses']}")


def setup_monitoring(app_name: str) -> PerformanceMonitor:
    """Setup performance monitoring for application.

    Args:
        app_name: Application name

    Returns:
        Configured performance monitor
    """
    monitor = PerformanceMonitor(app_name)

    # Log initial setup
    monitor.logger.info(f"Performance monitoring initialized for {app_name}")
    monitor.logger.info("Tracking: requests, database queries, cache operations")

    return monitor
