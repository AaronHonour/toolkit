"""Performance profiling tools."""

import cProfile
import pstats
import io
from typing import Callable, Optional
import time
import functools
from contextlib import contextmanager


class Profiler:
    """Performance profiler for identifying bottlenecks."""

    @staticmethod
    def profile_function(func: Callable, *args, **kwargs) -> tuple:
        """Profile function execution.

        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Tuple of (result, profile_stats)

        Example:
            result, stats = Profiler.profile_function(slow_function, arg1, arg2)
            print(stats)
        """
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Get stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions

        return result, stream.getvalue()

    @staticmethod
    def profile_decorator(func: Callable) -> Callable:
        """Decorator to profile function.

        Example:
            @Profiler.profile_decorator
            def slow_function():
                # code
                pass
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result, stats = Profiler.profile_function(func, *args, **kwargs)
            print(f"\nProfile for {func.__name__}:")
            print(stats)
            return result

        return wrapper

    @staticmethod
    @contextmanager
    def profile_context(name: str = "block"):
        """Context manager for profiling code block.

        Example:
            with Profiler.profile_context("database operations"):
                # code to profile
                pass
        """
        profiler = cProfile.Profile()
        profiler.enable()

        yield

        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)

        print(f"\nProfile for {name}:")
        print(stream.getvalue())


class PerformanceMonitor:
    """Monitor performance metrics over time."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {
            "calls": {},
            "total_time": {},
            "avg_time": {},
        }

    def monitor(self, func: Callable) -> Callable:
        """Decorator to monitor function performance.

        Example:
            monitor = PerformanceMonitor()

            @monitor.monitor
            def my_function():
                pass

            print(monitor.get_report())
        """
        func_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start

                if func_name not in self.metrics["calls"]:
                    self.metrics["calls"][func_name] = 0
                    self.metrics["total_time"][func_name] = 0.0

                self.metrics["calls"][func_name] += 1
                self.metrics["total_time"][func_name] += elapsed
                self.metrics["avg_time"][func_name] = (
                    self.metrics["total_time"][func_name] /
                    self.metrics["calls"][func_name]
                )

        return wrapper

    def get_report(self) -> str:
        """Get performance report.

        Returns:
            Formatted report
        """
        report = "\n=== Performance Report ===\n\n"

        # Sort by total time
        sorted_funcs = sorted(
            self.metrics["calls"].keys(),
            key=lambda f: self.metrics["total_time"][f],
            reverse=True
        )

        for func_name in sorted_funcs:
            calls = self.metrics["calls"][func_name]
            total = self.metrics["total_time"][func_name]
            avg = self.metrics["avg_time"][func_name]

            report += f"{func_name}:\n"
            report += f"  Calls: {calls}\n"
            report += f"  Total Time: {total:.3f}s\n"
            report += f"  Avg Time: {avg*1000:.2f}ms\n\n"

        return report
