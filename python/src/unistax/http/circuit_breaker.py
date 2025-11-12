"""Circuit breaker for HTTP requests."""

import time
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker state."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation.

    Prevents cascading failures by opening circuit after threshold failures.
    """

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """Initialize CircuitBreaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        """Handle successful call."""
        self.failures = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        """Handle failed call."""
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
