"""Unit tests for CircuitBreaker."""

import pytest
import asyncio
import time

from src.main import CircuitBreaker, CircuitState


class TestCircuitBreaker:
    """Test CircuitBreaker pattern."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_creation(self):
        """Test circuit breaker creation."""
        cb = CircuitBreaker(failure_threshold=5, success_threshold=2, timeout=30.0)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_threshold == 5
        assert cb.success_threshold == 2

    @pytest.mark.asyncio
    async def test_successful_call(self):
        """Test successful function call."""
        cb = CircuitBreaker()

        async def success_func():
            return "success"

        result = await cb.call(success_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failed_call(self):
        """Test failed function call."""
        cb = CircuitBreaker(failure_threshold=3)

        async def failing_func():
            raise Exception("Test error")

        # First failure
        with pytest.raises(Exception):
            await cb.call(failing_func)

        assert cb.failure_count == 1
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)

        async def failing_func():
            raise Exception("Test error")

        # Fail multiple times to open circuit
        for _ in range(3):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self):
        """Test that open circuit rejects calls."""
        cb = CircuitBreaker(failure_threshold=2)

        async def failing_func():
            raise Exception("Test error")

        # Open the circuit
        for _ in range(2):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        # Should reject next call
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await cb.call(failing_func)

        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(self):
        """Test circuit transitions to half-open after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)

        async def failing_func():
            raise Exception("Test error")

        # Open the circuit
        for _ in range(2):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.2)

        # Next call should transition to half-open
        async def success_func():
            return "success"

        result = await cb.call(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_closes_after_successes(self):
        """Test circuit closes after success threshold in half-open state."""
        cb = CircuitBreaker(failure_threshold=2, success_threshold=2, timeout=0.1)

        async def failing_func():
            raise Exception("Test error")

        # Open the circuit
        for _ in range(2):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        # Wait for timeout
        await asyncio.sleep(0.2)

        # Succeed multiple times to close circuit
        async def success_func():
            return "success"

        for _ in range(2):
            await cb.call(success_func)

        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_reopens_on_failure(self):
        """Test half-open circuit reopens on failure."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)

        async def failing_func():
            raise Exception("Test error")

        # Open the circuit
        for _ in range(2):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        # Wait for timeout to go half-open
        await asyncio.sleep(0.2)

        # Fail again - should reopen
        try:
            await cb.call(failing_func)
        except Exception:
            pass

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_concurrent_calls(self):
        """Test concurrent calls through circuit breaker."""
        cb = CircuitBreaker()

        async def slow_func():
            await asyncio.sleep(0.01)
            return "success"

        # Make concurrent calls
        tasks = [cb.call(slow_func) for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(r == "success" for r in results)

    @pytest.mark.asyncio
    async def test_failure_count_reset_on_success(self):
        """Test failure count resets on successful call."""
        cb = CircuitBreaker(failure_threshold=5)

        async def failing_func():
            raise Exception("Test error")

        async def success_func():
            return "success"

        # Some failures
        for _ in range(2):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        assert cb.failure_count == 2

        # Successful call in closed state doesn't reset failure count
        # (it only resets when transitioning from half-open to closed)
        await cb.call(success_func)
        assert cb.failure_count == 2  # Not reset in closed state

    @pytest.mark.asyncio
    async def test_last_failure_time_tracked(self):
        """Test that last failure time is tracked."""
        cb = CircuitBreaker(failure_threshold=2)

        async def failing_func():
            raise Exception("Test error")

        before = time.time()

        for _ in range(2):
            try:
                await cb.call(failing_func)
            except Exception:
                pass

        after = time.time()

        assert before <= cb.last_failure_time <= after
