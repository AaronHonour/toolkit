"""
Log formatters for structured and JSON output.

Provides formatters that support structured logging with extra fields.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Any


class StructuredFormatter(logging.Formatter):
    """
    Structured log formatter.

    Outputs logs in a human-readable format with structured fields.

    Format: timestamp | level | logger | message | key=value ...
    """

    def __init__(self, include_extra: bool = True) -> None:
        """
        Initialize formatter.

        Args:
            include_extra: Whether to include extra fields
        """
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        # Base fields
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        parts = [timestamp, level, logger_name, message]

        # Add extra fields
        if self.include_extra:
            extra_fields = self._get_extra_fields(record)
            if extra_fields:
                extra_str = " ".join(f"{k}={v}" for k, v in extra_fields.items())
                parts.append(extra_str)

        # Add exception info
        if record.exc_info:
            parts.append(self.formatException(record.exc_info))

        return " | ".join(str(p) for p in parts)

    def _get_extra_fields(self, record: logging.LogRecord) -> dict[str, Any]:
        """Extract extra fields from record."""
        # Standard fields to exclude
        standard_fields = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_info",
            "exc_text",
            "stack_info",
        }

        return {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_fields and not key.startswith("_")
        }


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter.

    Outputs logs as JSON objects for machine parsing.
    """

    def __init__(self, include_exc_info: bool = True) -> None:
        """
        Initialize formatter.

        Args:
            include_exc_info: Whether to include exception info
        """
        super().__init__()
        self.include_exc_info = include_exc_info

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        extra_fields = self._get_extra_fields(record)
        if extra_fields:
            log_data["extra"] = extra_fields

        # Add exception info
        if self.include_exc_info and record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_data, default=str)

    def _get_extra_fields(self, record: logging.LogRecord) -> dict[str, Any]:
        """Extract extra fields from record."""
        standard_fields = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_info",
            "exc_text",
            "stack_info",
        }

        return {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_fields and not key.startswith("_")
        }
