"""Trace exporters configuration."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from opentelemetry.sdk.trace.export import SpanExporter, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.zipkin.json import ZipkinExporter


class ExporterType(str, Enum):
    """Exporter type enumeration."""

    CONSOLE = "console"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OTLP = "otlp"


@dataclass
class ExporterConfig:
    """Exporter configuration."""

    type: ExporterType
    endpoint: Optional[str] = None
    service_name: Optional[str] = None
    agent_host: Optional[str] = None
    agent_port: Optional[int] = None
    max_tag_value_length: Optional[int] = None
    insecure: bool = False


def create_exporter(config: ExporterConfig) -> SpanExporter:
    """Create span exporter from configuration.

    Args:
        config: Exporter configuration

    Returns:
        SpanExporter instance

    Raises:
        ValueError: If exporter type is unknown
    """
    if config.type == ExporterType.CONSOLE:
        return ConsoleSpanExporter()

    elif config.type == ExporterType.JAEGER:
        kwargs = {}
        if config.agent_host:
            kwargs["agent_host_name"] = config.agent_host
        if config.agent_port:
            kwargs["agent_port"] = config.agent_port
        if config.max_tag_value_length:
            kwargs["max_tag_value_length"] = config.max_tag_value_length

        return JaegerExporter(**kwargs)

    elif config.type == ExporterType.ZIPKIN:
        kwargs = {}
        if config.endpoint:
            kwargs["endpoint"] = config.endpoint
        if config.max_tag_value_length:
            kwargs["max_tag_value_length"] = config.max_tag_value_length

        return ZipkinExporter(**kwargs)

    elif config.type == ExporterType.OTLP:
        kwargs = {}
        if config.endpoint:
            kwargs["endpoint"] = config.endpoint
        if config.insecure:
            kwargs["insecure"] = config.insecure

        return OTLPSpanExporter(**kwargs)

    else:
        raise ValueError(f"Unknown exporter type: {config.type}")
