"""Distributed tracing module using OpenTelemetry."""

from unistax.tracing.context import TraceContext, get_span_id, get_trace_id
from unistax.tracing.exporters import ExporterConfig, ExporterType
from unistax.tracing.span import SpanKind, SpanManager
from .tracer import Tracer, trace_decorator as trace  # type: ignore[attr-defined]

__all__ = [
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
