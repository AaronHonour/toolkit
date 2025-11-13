"""Distributed tracing module using OpenTelemetry."""

from unistax.tracing.context import TraceContext, get_span_id, get_trace_id
from unistax.tracing.exporters import ExporterConfig, ExporterType
from unistax.tracing.span import SpanKind, SpanManager

from .tracer import Tracer  # type: ignore[attr-defined]
from .tracer import trace_decorator as trace

__all__ = [
    "Tracer",
    "TracerManager",
    "get_tracer",
    "trace",
    "SpanManager",
    "SpanKind",
    "TraceContext",
    "get_trace_id",
    "get_span_id",
    "ExporterConfig",
    "ExporterType",
]
