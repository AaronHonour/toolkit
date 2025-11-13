"""Span management utilities."""

from enum import Enum
from typing import Any

from opentelemetry import trace  # type: ignore[import-not-found]
from opentelemetry.trace import SpanKind as OTelSpanKind  # type: ignore[import-not-found]
from opentelemetry.trace import Status, StatusCode  # type: ignore[import-not-found,unused-ignore]


class SpanKind(str, Enum):
    """Span kind enumeration."""

    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


def _get_otel_span_kind(kind: SpanKind) -> OTelSpanKind:
    """Convert SpanKind to OpenTelemetry SpanKind.

    Args:
        kind: SpanKind

    Returns:
        OpenTelemetry SpanKind
    """
    mapping = {
        SpanKind.INTERNAL: OTelSpanKind.INTERNAL,
        SpanKind.SERVER: OTelSpanKind.SERVER,
        SpanKind.CLIENT: OTelSpanKind.CLIENT,
        SpanKind.PRODUCER: OTelSpanKind.PRODUCER,
        SpanKind.CONSUMER: OTelSpanKind.CONSUMER,
    }
    return mapping[kind]


class SpanManager:
    """Manage span creation and manipulation."""

    def __init__(self, tracer: trace.Tracer) -> None:
        """Initialize span manager.

        Args:
            tracer: Tracer instance
        """
        self.tracer = tracer

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
        links: list[Any] | None = None,
    ) -> trace.Span:
        """Start a new span.

        Args:
            name: Span name
            kind: Span kind
            attributes: Span attributes
            links: Span links

        Returns:
            Span instance
        """
        return self.tracer.start_span(
            name,
            kind=_get_otel_span_kind(kind),
            attributes=attributes or {},
            links=links or [],
        )

    def add_event(
        self,
        span: trace.Span,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Add event to span.

        Args:
            span: Span instance
            name: Event name
            attributes: Event attributes
        """
        span.add_event(name, attributes=attributes or {})

    def set_attribute(self, span: trace.Span, key: str, value: Any) -> None:
        """Set span attribute.

        Args:
            span: Span instance
            key: Attribute key
            value: Attribute value
        """
        span.set_attribute(key, value)

    def set_attributes(self, span: trace.Span, attributes: dict[str, Any]) -> None:
        """Set multiple span attributes.

        Args:
            span: Span instance
            attributes: Attributes dictionary
        """
        span.set_attributes(attributes)

    def set_status(
        self,
        span: trace.Span,
        status_code: StatusCode,
        description: str | None = None,
    ) -> None:
        """Set span status.

        Args:
            span: Span instance
            status_code: Status code
            description: Status description
        """
        span.set_status(Status(status_code, description))

    def record_exception(
        self,
        span: trace.Span,
        exception: Exception,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Record exception in span.

        Args:
            span: Span instance
            exception: Exception to record
            attributes: Additional attributes
        """
        span.record_exception(exception, attributes=attributes or {})

    def end_span(self, span: trace.Span) -> None:
        """End a span.

        Args:
            span: Span instance
        """
        span.end()


def get_current_span() -> trace.Span:
    """Get current active span.

    Returns:
        Current span
    """
    return trace.get_current_span()


def is_recording() -> bool:
    """Check if current span is recording.

    Returns:
        True if recording
    """
    span = get_current_span()
    return span.is_recording()  # type: ignore[no-any-return]
