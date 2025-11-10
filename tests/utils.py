"""Testing utilities and base classes."""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from contextlib import contextmanager
import time
import pytest


class TestBase:
    """Base class for all tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test."""
        self.start_time = time.time()
        yield
        elapsed = time.time() - self.start_time
        if elapsed > 1.0:
            pytest.warn(f"Slow test: {elapsed:.2f}s")


class AsyncTestBase(TestBase):
    """Base class for async tests."""

    @pytest.fixture(autouse=True)
    async def async_setup(self):
        """Setup before each async test."""
        yield


@contextmanager
def assert_time_limit(seconds: float, operation: str = "operation"):
    """Assert operation completes within time limit.

    Example:
        with assert_time_limit(0.1, "cache get"):
            value = cache.get("key")
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    assert elapsed < seconds, f"{operation} took {elapsed:.3f}s, expected < {seconds}s"


@contextmanager
def measure_time(description: str = "operation"):
    """Measure and print operation time.

    Example:
        with measure_time("database query"):
            users = db.query(User).all()
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"\n{description}: {elapsed:.3f}s")


class PerformanceAssertion:
    """Performance assertion helpers."""

    @staticmethod
    def assert_latency_p95(func: Callable, max_latency: float, iterations: int = 100):
        """Assert p95 latency is below threshold."""
        latencies = []
        for _ in range(iterations):
            start = time.time()
            func()
            latencies.append(time.time() - start)

        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        assert p95 < max_latency, f"p95 latency {p95:.3f}s > {max_latency}s"

    @staticmethod
    def assert_throughput(func: Callable, min_rps: float, duration: float = 1.0):
        """Assert throughput is above threshold."""
        start = time.time()
        count = 0

        while time.time() - start < duration:
            func()
            count += 1

        actual_rps = count / duration
        assert actual_rps >= min_rps, f"Throughput {actual_rps:.1f} RPS < {min_rps} RPS"

    @staticmethod
    async def assert_async_latency_p95(
        func: Callable, max_latency: float, iterations: int = 100
    ):
        """Assert async p95 latency is below threshold."""
        latencies = []
        for _ in range(iterations):
            start = time.time()
            await func()
            latencies.append(time.time() - start)

        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        assert p95 < max_latency, f"p95 latency {p95:.3f}s > {max_latency}s"


class MemoryAssertion:
    """Memory usage assertion helpers."""

    @staticmethod
    @contextmanager
    def assert_memory_limit(max_mb: float):
        """Assert operation uses less than max memory."""
        import tracemalloc

        tracemalloc.start()
        yield
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        assert peak_mb < max_mb, f"Peak memory {peak_mb:.1f}MB > {max_mb}MB"


def parametrize_with_cases(*cases: Dict[str, Any]):
    """Parametrize test with named cases.

    Example:
        @parametrize_with_cases(
            {"name": "small", "size": 10},
            {"name": "large", "size": 1000}
        )
        def test_something(size):
            assert process(size) == expected
    """
    ids = [case.pop("name") for case in cases]
    keys = cases[0].keys()
    values = [tuple(case[k] for k in keys) for case in cases]
    return pytest.mark.parametrize(",".join(keys), values, ids=ids)
