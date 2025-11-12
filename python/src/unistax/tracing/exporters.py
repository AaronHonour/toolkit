"""Trace exporters configuration."""

from dataclasses import dataclass
from enum import Enum

from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SpanExporter


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
    endpoint: str | None = None
    service_name: str | None = None
    agent_host: str | None = None
    agent_port: int | None = None
    max_tag_value_length: int | None = None
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
