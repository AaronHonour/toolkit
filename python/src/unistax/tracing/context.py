"""Trace context management."""

from typing import Optional
from opentelemetry import trace
from opentelemetry.trace import SpanContext
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class TraceContext:
    """Manage trace context propagation."""

    def __init__(self):
        """Initialize trace context."""
        self.propagator = TraceContextTextMapPropagator()

    def inject(self, carrier: dict):
        """Inject trace context into carrier.

        Args:
            carrier: Carrier dictionary (e.g., HTTP headers)

        Example:
            headers = {}
            trace_context.inject(headers)
            requests.get(url, headers=headers)
        """
        self.propagator.inject(carrier)

    def extract(self, carrier: dict) -> SpanContext:
        """Extract trace context from carrier.

        Args:
            carrier: Carrier dictionary (e.g., HTTP headers)

        Returns:
            Span context

        Example:
            context = trace_context.extract(request.headers)
        """
        ctx = self.propagator.extract(carrier)
        return trace.get_current_span(ctx).get_span_context()

    @staticmethod
    def get_current_trace_id() -> Optional[str]:
        """Get current trace ID.

        Returns:
            Trace ID as hex string or None
        """
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().trace_id, "032x")
        return None

    @staticmethod
    def get_current_span_id() -> Optional[str]:
        """Get current span ID.

        Returns:
            Span ID as hex string or None
        """
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().span_id, "016x")
        return None


# Global instance
_trace_context = TraceContext()


def get_trace_id() -> Optional[str]:
    """Get current trace ID.

    Returns:
        Trace ID as hex string or None
    """
    return TraceContext.get_current_trace_id()


def get_span_id() -> Optional[str]:
    """Get current span ID.

    Returns:
        Span ID as hex string or None
    """
    return TraceContext.get_current_span_id()


def inject_context(carrier: dict):
    """Inject trace context into carrier.

    Args:
        carrier: Carrier dictionary
    """
    _trace_context.inject(carrier)


def extract_context(carrier: dict) -> SpanContext:
    """Extract trace context from carrier.

    Args:
        carrier: Carrier dictionary

    Returns:
        Span context
    """
    return _trace_context.extract(carrier)
