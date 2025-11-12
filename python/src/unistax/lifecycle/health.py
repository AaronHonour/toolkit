"""Health check system."""

import time
from collections.abc import Callable
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class HealthCheck:
    """Health check definition.

    Attributes:
        name: Check name
        func: Check function (returns bool or HealthStatus)
        check_type: "liveness" or "readiness"
    """

    def __init__(self, name: str, func: Callable, check_type: str = "readiness"):
        """Initialize HealthCheck.

        Args:
            name: Health check name
            func: Function to execute for the check
            check_type: Type of check ("liveness" or "readiness")
        """
        self.name = name
        self.func = func
        self.check_type = check_type

    def execute(self) -> dict[str, Any]:
        """Execute health check.

        Returns:
            Dict with check results
        """
        start_time = time.time()

        try:
            result = self.func()

            # Convert bool to status
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            elif isinstance(result, HealthStatus):
                status = result
            else:
                status = HealthStatus.HEALTHY

            duration = time.time() - start_time

            return {
                "name": self.name,
                "status": status.value,
                "duration_ms": round(duration * 1000, 2),
                "type": self.check_type,
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY.value,
                "duration_ms": round(duration * 1000, 2),
                "type": self.check_type,
                "error": str(e),
            }


class HealthCheckRegistry:
    """Registry for health checks."""

    def __init__(self):
        """Initialize HealthCheckRegistry."""
        self._checks: list[HealthCheck] = []

    def register(self, check: HealthCheck) -> None:
        """Register a health check."""
        self._checks.append(check)

    def check_all(self) -> dict[str, Any]:
        """Run all health checks.

        Returns:
            Dict with all check results
        """
        results = []
        all_healthy = True

        for check in self._checks:
            result = check.execute()
            results.append(result)

            if result["status"] != HealthStatus.HEALTHY.value:
                all_healthy = False

        overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.UNHEALTHY

        return {
            "status": overall_status.value,
            "checks": results,
        }

    def check_liveness(self) -> bool:
        """Run liveness checks.

        Returns:
            True if all liveness checks pass
        """
        for check in self._checks:
            if check.check_type == "liveness":
                result = check.execute()
                if result["status"] != HealthStatus.HEALTHY.value:
                    return False
        return True

    def check_readiness(self) -> bool:
        """Run readiness checks.

        Returns:
            True if all readiness checks pass
        """
        for check in self._checks:
            if check.check_type == "readiness":
                result = check.execute()
                if result["status"] != HealthStatus.HEALTHY.value:
                    return False
        return True
