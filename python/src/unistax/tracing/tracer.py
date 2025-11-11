"""Tracer management using OpenTelemetry."""

from typing import Callable, Optional
from functools import wraps
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from unistax.tracing.exporters import ExporterConfig, create_exporter

# Global tracer provider
_tracer_provider: Optional[TracerProvider] = None


class TracerManager:
    """Manage OpenTelemetry tracing."""

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "production",
    ):
        """Initialize tracer manager.

        Args:
            service_name: Service name
            service_version: Service version
            environment: Environment name
        """
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self._setup_tracer()

    def _setup_tracer(self):
        """Setup tracer provider."""
        global _tracer_provider

        # Create resource
        resource = Resource(
            attributes={
                SERVICE_NAME: self.service_name,
                "service.version": self.service_version,
                "deployment.environment": self.environment,
            }
        )

        # Create tracer provider
        _tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(_tracer_provider)

    def add_exporter(self, exporter_config: ExporterConfig):
        """Add span exporter.

        Args:
            exporter_config: Exporter configuration
        """
        exporter = create_exporter(exporter_config)
        span_processor = BatchSpanProcessor(exporter)
        _tracer_provider.add_span_processor(span_processor)

    def get_tracer(self, name: Optional[str] = None) -> trace.Tracer:
        """Get tracer instance.

        Args:
            name: Tracer name

        Returns:
            Tracer instance
        """
        tracer_name = name or self.service_name
        return trace.get_tracer(tracer_name)

    def shutdown(self, timeout: int = 30):
        """Shutdown tracer provider.

        Args:
            timeout: Shutdown timeout (seconds)
        """
        if _tracer_provider:
            _tracer_provider.shutdown()


def get_tracer(name: Optional[str] = None) -> trace.Tracer:
    """Get global tracer.

    Args:
        name: Tracer name

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name or "toolkit")


def trace(
    name: Optional[str] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
    attributes: Optional[dict] = None,
):
    """Decorator to trace function execution.

    Args:
        name: Span name (defaults to function name)
        kind: Span kind
        attributes: Span attributes

    Returns:
        Decorator

    Example:
        @trace(name="process_order", kind=SpanKind.SERVER)
        def process_order(order_id: int):
            # Processing logic
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or func.__name__

            with tracer.start_as_current_span(
                span_name, kind=kind, attributes=attributes or {}
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            description=str(e),
                        )
                    )
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator
