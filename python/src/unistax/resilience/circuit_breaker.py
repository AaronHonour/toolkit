"""Circuit breaker pattern implementation."""

import time
from enum import Enum
from functools import wraps


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures.

    Examples:
        >>> breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        >>> @breaker.protected()
        ... def call_external_service():
        ...     return requests.get("https://api.example.com")
    """

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0, half_open_max_calls: int = 1):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0

    def protected(self, fallback=None):
        """Decorator to protect function with circuit breaker.

        Args:
            fallback: Fallback function to call when circuit is open
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.state == CircuitState.OPEN:
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                    else:
                        if fallback:
                            return fallback(*args, **kwargs)
                        raise Exception("Circuit breaker is OPEN")

                if self.state == CircuitState.HALF_OPEN:
                    if self.half_open_calls >= self.half_open_max_calls:
                        raise Exception("Circuit breaker in HALF_OPEN, max calls reached")
                    self.half_open_calls += 1

                try:
                    result = func(*args, **kwargs)
                    self.on_success()
                    return result
                except Exception as e:
                    self.on_failure()
                    raise e

            return wrapper

        return decorator

    def on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0
        self.failures = 0

    def on_failure(self):
        """Handle failed call."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.successes = 0

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.successes = 0

    def reset(self):
        """Reset circuit breaker."""
        self.failures = 0
        self.successes = 0
        self.state = CircuitState.CLOSED
