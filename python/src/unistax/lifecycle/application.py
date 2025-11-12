"""Application lifecycle management."""

import asyncio
import signal
import sys
from collections.abc import Callable
from enum import Enum
from typing import Any

from .health import HealthCheck, HealthCheckRegistry
from .hooks import LifecycleHook


class LifecycleEvent(str, Enum):
    """Application lifecycle events."""

    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    READY = "ready"


class Application:
    """Application lifecycle manager.

    Manages startup, shutdown, and health checks.

    Examples:
        >>> app = Application()
        >>>
        >>> @app.on_startup
        ... async def init_db():
        ...     await db.connect()
        >>>
        >>> @app.on_shutdown
        ... async def cleanup():
        ...     await db.disconnect()
        >>>
        >>> @app.health_check
        ... def db_health():
        ...     return db.ping()
        >>>
        >>> await app.start()
    """

    def __init__(self, name: str = "app", shutdown_timeout: float = 30.0):
        """Initialize application.

        Args:
            name: Application name
            shutdown_timeout: Graceful shutdown timeout in seconds
        """
        self.name = name
        self.shutdown_timeout = shutdown_timeout
        self._startup_hooks: list[LifecycleHook] = []
        self._shutdown_hooks: list[LifecycleHook] = []
        self._health_registry = HealthCheckRegistry()
        self._is_running = False
        self._signal_handlers_installed = False

    def on_startup(self, func: Callable) -> Callable:
        """Register startup hook.

        Args:
            func: Startup function (can be sync or async)

        Returns:
            Original function
        """
        hook = LifecycleHook(LifecycleEvent.STARTUP, func)
        self._startup_hooks.append(hook)
        return func

    def on_shutdown(self, func: Callable) -> Callable:
        """Register shutdown hook.

        Args:
            func: Shutdown function (can be sync or async)

        Returns:
            Original function
        """
        hook = LifecycleHook(LifecycleEvent.SHUTDOWN, func)
        self._shutdown_hooks.append(hook)
        return func

    def health_check(
        self, name: str | None = None, check_type: str = "readiness"
    ) -> Callable:
        """Register health check.

        Args:
            name: Health check name (defaults to function name)
            check_type: "liveness" or "readiness"

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            check_name = name or func.__name__
            health_check = HealthCheck(check_name, func, check_type)
            self._health_registry.register(health_check)
            return func

        return decorator

    async def start(self) -> None:
        """Start the application.

        Runs all startup hooks and installs signal handlers.
        """
        if self._is_running:
            return

        print(f"Starting application: {self.name}")

        # Install signal handlers
        self._install_signal_handlers()

        # Run startup hooks
        for hook in self._startup_hooks:
            try:
                await hook.execute()
                print(f"✓ Startup hook executed: {hook.func.__name__}")
            except Exception as e:
                print(f"✗ Startup hook failed: {hook.func.__name__}: {e}")
                raise

        self._is_running = True
        print(f"✓ Application started: {self.name}")

    async def stop(self) -> None:
        """Stop the application.

        Runs all shutdown hooks with timeout.
        """
        if not self._is_running:
            return

        print(f"Stopping application: {self.name}")
        self._is_running = False

        # Run shutdown hooks with timeout
        try:
            await asyncio.wait_for(
                self._run_shutdown_hooks(), timeout=self.shutdown_timeout
            )
            print(f"✓ Application stopped gracefully: {self.name}")
        except asyncio.TimeoutError:
            print(f"⚠ Shutdown timeout exceeded: {self.name}")

    async def _run_shutdown_hooks(self) -> None:
        """Run all shutdown hooks."""
        for hook in reversed(self._shutdown_hooks):  # Reverse order
            try:
                await hook.execute()
                print(f"✓ Shutdown hook executed: {hook.func.__name__}")
            except Exception as e:
                print(f"⚠ Shutdown hook error: {hook.func.__name__}: {e}")
                # Continue with other hooks

    def _install_signal_handlers(self) -> None:
        """Install signal handlers for graceful shutdown."""
        if self._signal_handlers_installed:
            return

        def signal_handler(sig, frame):
            print(f"\nReceived signal {sig}, initiating graceful shutdown...")
            asyncio.create_task(self.stop())

        # Only on Unix systems
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

        self._signal_handlers_installed = True

    def get_health_status(self) -> dict[str, Any]:
        """Get application health status.

        Returns:
            Dictionary with health check results
        """
        return self._health_registry.check_all()

    def is_healthy(self) -> bool:
        """Check if application is healthy.

        Returns:
            True if all health checks pass
        """
        status = self.get_health_status()
        return status.get("status") == "healthy"

    def is_ready(self) -> bool:
        """Check if application is ready to serve requests.

        Returns:
            True if running and readiness checks pass
        """
        if not self._is_running:
            return False

        return self._health_registry.check_readiness()

    def is_alive(self) -> bool:
        """Check if application is alive (liveness check).

        Returns:
            True if running and liveness checks pass
        """
        if not self._is_running:
            return False

        return self._health_registry.check_liveness()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Application(name={self.name}, running={self._is_running})"
