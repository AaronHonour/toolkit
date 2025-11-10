"""Benchmark framework for performance testing."""

import time
import statistics
import gc
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager
import json


@dataclass
class BenchmarkResult:
    """Benchmark result container."""

    name: str
    iterations: int
    total_time: float
    min_time: float
    max_time: float
    mean_time: float
    median_time: float
    p95_time: float
    p99_time: float
    stddev: float
    ops_per_second: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": self.total_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "mean_time": self.mean_time,
            "median_time": self.median_time,
            "p95_time": self.p95_time,
            "p99_time": self.p99_time,
            "stddev": self.stddev,
            "ops_per_second": self.ops_per_second,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """String representation."""
        return f"""
Benchmark: {self.name}
Iterations: {self.iterations}
Total Time: {self.total_time:.4f}s
Min: {self.min_time*1000:.2f}ms | Max: {self.max_time*1000:.2f}ms
Mean: {self.mean_time*1000:.2f}ms | Median: {self.median_time*1000:.2f}ms
P95: {self.p95_time*1000:.2f}ms | P99: {self.p99_time*1000:.2f}ms
Stddev: {self.stddev*1000:.2f}ms
Throughput: {self.ops_per_second:.2f} ops/sec
"""


class Benchmark:
    """Benchmark runner for performance testing."""

    def __init__(self, name: str = "benchmark"):
        """Initialize benchmark.

        Args:
            name: Benchmark name
        """
        self.name = name
        self.results: List[BenchmarkResult] = []

    def run(
        self,
        func: Callable,
        iterations: int = 1000,
        warmup: int = 10,
        name: Optional[str] = None,
        **kwargs
    ) -> BenchmarkResult:
        """Run benchmark.

        Args:
            func: Function to benchmark
            iterations: Number of iterations
            warmup: Number of warmup iterations
            name: Test name
            **kwargs: Additional metadata

        Returns:
            BenchmarkResult

        Example:
            benchmark = Benchmark()
            result = benchmark.run(my_function, iterations=1000)
            print(result)
        """
        test_name = name or func.__name__

        # Warmup
        for _ in range(warmup):
            func()

        # Force garbage collection
        gc.collect()

        # Run benchmark
        times: List[float] = []
        start_total = time.perf_counter()

        for _ in range(iterations):
            start = time.perf_counter()
            func()
            times.append(time.perf_counter() - start)

        total_time = time.perf_counter() - start_total

        # Calculate statistics
        times.sort()
        result = BenchmarkResult(
            name=test_name,
            iterations=iterations,
            total_time=total_time,
            min_time=min(times),
            max_time=max(times),
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            p95_time=times[int(len(times) * 0.95)],
            p99_time=times[int(len(times) * 0.99)],
            stddev=statistics.stdev(times) if len(times) > 1 else 0.0,
            ops_per_second=iterations / total_time,
            metadata=kwargs,
        )

        self.results.append(result)
        return result

    async def run_async(
        self,
        func: Callable,
        iterations: int = 1000,
        warmup: int = 10,
        name: Optional[str] = None,
        **kwargs
    ) -> BenchmarkResult:
        """Run async benchmark.

        Args:
            func: Async function to benchmark
            iterations: Number of iterations
            warmup: Number of warmup iterations
            name: Test name
            **kwargs: Additional metadata

        Returns:
            BenchmarkResult
        """
        test_name = name or func.__name__

        # Warmup
        for _ in range(warmup):
            await func()

        gc.collect()

        # Run benchmark
        times: List[float] = []
        start_total = time.perf_counter()

        for _ in range(iterations):
            start = time.perf_counter()
            await func()
            times.append(time.perf_counter() - start)

        total_time = time.perf_counter() - start_total

        # Calculate statistics
        times.sort()
        result = BenchmarkResult(
            name=test_name,
            iterations=iterations,
            total_time=total_time,
            min_time=min(times),
            max_time=max(times),
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            p95_time=times[int(len(times) * 0.95)],
            p99_time=times[int(len(times) * 0.99)],
            stddev=statistics.stdev(times) if len(times) > 1 else 0.0,
            ops_per_second=iterations / total_time,
            metadata=kwargs,
        )

        self.results.append(result)
        return result

    def compare(
        self,
        func1: Callable,
        func2: Callable,
        iterations: int = 1000,
        name1: str = "baseline",
        name2: str = "optimized",
    ) -> Dict[str, Any]:
        """Compare two implementations.

        Args:
            func1: Baseline function
            func2: Optimized function
            iterations: Number of iterations
            name1: Name for func1
            name2: Name for func2

        Returns:
            Comparison results

        Example:
            results = benchmark.compare(old_func, new_func, iterations=1000)
            print(f"Speedup: {results['speedup']:.2f}x")
        """
        result1 = self.run(func1, iterations=iterations, name=name1)
        result2 = self.run(func2, iterations=iterations, name=name2)

        speedup = result1.mean_time / result2.mean_time
        improvement = ((result1.mean_time - result2.mean_time) / result1.mean_time) * 100

        return {
            "baseline": result1,
            "optimized": result2,
            "speedup": speedup,
            "improvement_percent": improvement,
            "faster": name2 if speedup > 1 else name1,
        }

    def export_results(self, filename: str):
        """Export results to JSON file.

        Args:
            filename: Output file path
        """
        data = {
            "benchmark_name": self.name,
            "results": [r.to_dict() for r in self.results],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def print_summary(self):
        """Print summary of all results."""
        print(f"\n{'='*60}")
        print(f"Benchmark Summary: {self.name}")
        print(f"{'='*60}")

        for result in self.results:
            print(result)


@contextmanager
def benchmark_context(name: str = "operation"):
    """Context manager for quick benchmarking.

    Example:
        with benchmark_context("database query"):
            users = db.query(User).all()
    """
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"\n{name}: {elapsed*1000:.2f}ms")


class MemoryBenchmark:
    """Memory usage benchmarking."""

    @staticmethod
    def measure_memory(func: Callable, iterations: int = 100) -> Dict[str, float]:
        """Measure memory usage.

        Args:
            func: Function to measure
            iterations: Number of iterations

        Returns:
            Memory statistics in MB
        """
        import tracemalloc

        tracemalloc.start()

        # Warmup
        for _ in range(10):
            func()

        tracemalloc.clear_traces()

        # Measure
        measurements = []
        for _ in range(iterations):
            snapshot_before = tracemalloc.take_snapshot()
            func()
            snapshot_after = tracemalloc.take_snapshot()

            stats = snapshot_after.compare_to(snapshot_before, "lineno")
            total = sum(stat.size_diff for stat in stats) / 1024 / 1024
            measurements.append(total)

        tracemalloc.stop()

        return {
            "min_mb": min(measurements),
            "max_mb": max(measurements),
            "mean_mb": statistics.mean(measurements),
            "median_mb": statistics.median(measurements),
        }


class LoadBenchmark:
    """Load testing benchmark."""

    @staticmethod
    def run_load_test(
        func: Callable,
        duration: float = 10.0,
        concurrency: int = 10,
    ) -> Dict[str, Any]:
        """Run load test.

        Args:
            func: Function to test
            duration: Test duration in seconds
            concurrency: Number of concurrent workers

        Returns:
            Load test results
        """
        import threading
        from queue import Queue

        results_queue: Queue = Queue()
        stop_event = threading.Event()

        def worker():
            local_times = []
            while not stop_event.is_set():
                start = time.perf_counter()
                try:
                    func()
                    local_times.append(time.perf_counter() - start)
                except Exception as e:
                    results_queue.put({"error": str(e)})

            results_queue.put({"times": local_times})

        # Start workers
        threads = []
        for _ in range(concurrency):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Run for duration
        time.sleep(duration)
        stop_event.set()

        # Wait for completion
        for t in threads:
            t.join()

        # Collect results
        all_times = []
        errors = 0

        while not results_queue.empty():
            result = results_queue.get()
            if "error" in result:
                errors += 1
            else:
                all_times.extend(result["times"])

        if not all_times:
            return {"error": "No successful requests"}

        all_times.sort()
        total_requests = len(all_times)

        return {
            "duration": duration,
            "concurrency": concurrency,
            "total_requests": total_requests,
            "requests_per_second": total_requests / duration,
            "errors": errors,
            "error_rate": errors / (total_requests + errors) if total_requests + errors > 0 else 0,
            "latency_min": min(all_times) * 1000,
            "latency_max": max(all_times) * 1000,
            "latency_mean": statistics.mean(all_times) * 1000,
            "latency_median": statistics.median(all_times) * 1000,
            "latency_p95": all_times[int(len(all_times) * 0.95)] * 1000,
            "latency_p99": all_times[int(len(all_times) * 0.99)] * 1000,
        }
