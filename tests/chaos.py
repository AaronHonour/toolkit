"""Chaos engineering framework for reliability testing."""

import random
import time
from typing import Any, Callable, Optional
from contextlib import contextmanager
from functools import wraps
from enum import Enum


class FailureType(Enum):
    """Types of failures to inject."""

    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    SLOW_RESPONSE = "slow_response"
    RANDOM_EXCEPTION = "random_exception"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"


class ChaosMonkey:
    """Inject failures for chaos testing."""

    def __init__(self, failure_rate: float = 0.1):
        """Initialize chaos monkey.

        Args:
            failure_rate: Probability of failure (0.0-1.0)
        """
        self.failure_rate = failure_rate
        self.enabled = True

    def should_fail(self) -> bool:
        """Determine if should inject failure."""
        return self.enabled and random.random() < self.failure_rate

    def inject_network_error(self):
        """Inject network error."""
        if self.should_fail():
            raise ConnectionError("Chaos: Simulated network error")

    def inject_timeout(self):
        """Inject timeout."""
        if self.should_fail():
            raise TimeoutError("Chaos: Simulated timeout")

    def inject_slow_response(self, max_delay: float = 5.0):
        """Inject slow response."""
        if self.should_fail():
            delay = random.uniform(1.0, max_delay)
            time.sleep(delay)

    def inject_random_exception(self):
        """Inject random exception."""
        if self.should_fail():
            exceptions = [
                ValueError("Chaos: Invalid value"),
                RuntimeError("Chaos: Runtime error"),
                KeyError("Chaos: Key not found"),
                AttributeError("Chaos: Attribute error"),
            ]
            raise random.choice(exceptions)

    def inject_data_corruption(self, data: Any) -> Any:
        """Inject data corruption."""
        if self.should_fail():
            if isinstance(data, str):
                return data[:len(data)//2]  # Truncate
            elif isinstance(data, (list, tuple)):
                return data[:len(data)//2]  # Truncate
            elif isinstance(data, dict):
                return {k: None for k in data}  # Nullify values
            elif isinstance(data, (int, float)):
                return 0  # Zero out
        return data

    def chaos_decorator(
        self,
        failure_types: Optional[list[FailureType]] = None
    ) -> Callable:
        """Decorator to add chaos to function.

        Example:
            monkey = ChaosMonkey(failure_rate=0.2)

            @monkey.chaos_decorator([FailureType.TIMEOUT, FailureType.SLOW_RESPONSE])
            def my_function():
                # This function will randomly fail
                pass
        """
        if failure_types is None:
            failure_types = [FailureType.RANDOM_EXCEPTION]

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for failure_type in failure_types:
                    if failure_type == FailureType.NETWORK_ERROR:
                        self.inject_network_error()
                    elif failure_type == FailureType.TIMEOUT:
                        self.inject_timeout()
                    elif failure_type == FailureType.SLOW_RESPONSE:
                        self.inject_slow_response()
                    elif failure_type == FailureType.RANDOM_EXCEPTION:
                        self.inject_random_exception()

                result = func(*args, **kwargs)

                # Corrupt result data if configured
                if FailureType.DATA_CORRUPTION in failure_types:
                    result = self.inject_data_corruption(result)

                return result

            return wrapper

        return decorator


class FaultInjector:
    """Advanced fault injection for testing."""

    @staticmethod
    @contextmanager
    def intermittent_failure(
        failure_rate: float = 0.5,
        exception: Exception = RuntimeError("Intermittent failure")
    ):
        """Context manager for intermittent failures.

        Example:
            with FaultInjector.intermittent_failure(0.3):
                result = unreliable_operation()
        """
        if random.random() < failure_rate:
            raise exception
        yield

    @staticmethod
    @contextmanager
    def resource_limit(
        cpu_percent: Optional[float] = None,
        memory_mb: Optional[float] = None
    ):
        """Simulate resource constraints.

        Args:
            cpu_percent: CPU usage limit
            memory_mb: Memory limit in MB
        """
        # This is a simplified version
        # In production, would use cgroups or similar
        yield

    @staticmethod
    @contextmanager
    def packet_loss(loss_rate: float = 0.1):
        """Simulate packet loss.

        Args:
            loss_rate: Probability of packet loss (0.0-1.0)
        """
        if random.random() < loss_rate:
            raise ConnectionError("Simulated packet loss")
        yield

    @staticmethod
    def corrupt_data(data: bytes, corruption_rate: float = 0.01) -> bytes:
        """Corrupt data bytes.

        Args:
            data: Original data
            corruption_rate: Probability of corrupting each byte

        Returns:
            Potentially corrupted data
        """
        result = bytearray(data)
        for i in range(len(result)):
            if random.random() < corruption_rate:
                result[i] = random.randint(0, 255)
        return bytes(result)


class ResilienceTest:
    """Test resilience patterns."""

    @staticmethod
    def test_retry(
        func: Callable,
        max_retries: int = 3,
        chaos_monkey: Optional[ChaosMonkey] = None
    ) -> dict:
        """Test retry mechanism.

        Args:
            func: Function to test
            max_retries: Maximum retry attempts
            chaos_monkey: Chaos monkey for failure injection

        Returns:
            Test results
        """
        if chaos_monkey is None:
            chaos_monkey = ChaosMonkey(failure_rate=0.5)

        attempts = 0
        successes = 0
        failures = 0

        for _ in range(100):  # Run 100 tests
            for attempt in range(max_retries):
                attempts += 1
                try:
                    if chaos_monkey.should_fail():
                        raise RuntimeError("Chaos failure")
                    func()
                    successes += 1
                    break
                except Exception:
                    if attempt == max_retries - 1:
                        failures += 1

        return {
            "total_attempts": attempts,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / 100,
            "avg_attempts": attempts / 100,
        }

    @staticmethod
    def test_circuit_breaker(
        func: Callable,
        failure_threshold: int = 5,
        timeout: float = 60,
        chaos_monkey: Optional[ChaosMonkey] = None
    ) -> dict:
        """Test circuit breaker pattern.

        Args:
            func: Function to test
            failure_threshold: Failures before opening
            timeout: Recovery timeout
            chaos_monkey: Chaos monkey for failure injection

        Returns:
            Test results
        """
        if chaos_monkey is None:
            chaos_monkey = ChaosMonkey(failure_rate=0.7)

        consecutive_failures = 0
        circuit_open = False
        tests = 100
        blocked = 0
        successes = 0
        failures = 0

        for _ in range(tests):
            if circuit_open:
                blocked += 1
                continue

            try:
                if chaos_monkey.should_fail():
                    raise RuntimeError("Chaos failure")
                func()
                consecutive_failures = 0
                successes += 1
            except Exception:
                consecutive_failures += 1
                failures += 1

                if consecutive_failures >= failure_threshold:
                    circuit_open = True

        return {
            "tests": tests,
            "successes": successes,
            "failures": failures,
            "blocked": blocked,
            "circuit_opened": circuit_open,
            "success_rate": successes / tests if tests > 0 else 0,
        }

    @staticmethod
    def test_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        chaos_monkey: Optional[ChaosMonkey] = None
    ) -> dict:
        """Test fallback mechanism.

        Args:
            primary_func: Primary function
            fallback_func: Fallback function
            chaos_monkey: Chaos monkey

        Returns:
            Test results
        """
        if chaos_monkey is None:
            chaos_monkey = ChaosMonkey(failure_rate=0.5)

        primary_used = 0
        fallback_used = 0
        total_failures = 0
        tests = 100

        for _ in range(tests):
            try:
                if chaos_monkey.should_fail():
                    raise RuntimeError("Chaos failure")
                primary_func()
                primary_used += 1
            except Exception:
                try:
                    fallback_func()
                    fallback_used += 1
                except Exception:
                    total_failures += 1

        return {
            "tests": tests,
            "primary_used": primary_used,
            "fallback_used": fallback_used,
            "total_failures": total_failures,
            "fallback_rate": fallback_used / tests,
        }


class LoadTest:
    """Load testing utilities."""

    @staticmethod
    def spike_test(
        func: Callable,
        baseline_rps: int = 100,
        spike_rps: int = 1000,
        spike_duration: float = 5.0
    ) -> dict:
        """Run spike test.

        Args:
            func: Function to test
            baseline_rps: Baseline requests per second
            spike_rps: Spike requests per second
            spike_duration: Duration of spike in seconds

        Returns:
            Test results
        """
        import threading
        from queue import Queue

        results: Queue = Queue()
        stop_event = threading.Event()

        def worker(rps: int):
            sleep_time = 1.0 / rps
            local_count = 0
            local_errors = 0

            while not stop_event.is_set():
                try:
                    func()
                    local_count += 1
                except Exception:
                    local_errors += 1
                time.sleep(sleep_time)

            results.put({"count": local_count, "errors": local_errors})

        # Baseline phase
        print(f"Baseline phase: {baseline_rps} RPS")
        thread = threading.Thread(target=worker, args=(baseline_rps,))
        thread.start()
        time.sleep(5.0)

        # Spike phase
        print(f"Spike phase: {spike_rps} RPS")
        spike_thread = threading.Thread(target=worker, args=(spike_rps,))
        spike_thread.start()
        time.sleep(spike_duration)

        # Recovery phase
        stop_event.set()
        thread.join()
        spike_thread.join()

        # Collect results
        total_count = 0
        total_errors = 0
        while not results.empty():
            result = results.get()
            total_count += result["count"]
            total_errors += result["errors"]

        return {
            "total_requests": total_count,
            "total_errors": total_errors,
            "error_rate": total_errors / total_count if total_count > 0 else 0,
        }
