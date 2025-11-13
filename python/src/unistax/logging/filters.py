"""Log filters for sensitive data and context management.

Provides filters to protect sensitive information and add context.
"""

import logging
import re

from .context import log_context


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs.

    Supports pattern-based redaction of sensitive information like:
    - Passwords
    - API keys
    - Credit card numbers
    - Email addresses
    - etc.
    """

    DEFAULT_PATTERNS = [
        (r"password['\"]?\s*[:=]\s*['\"]?([^'\"&\s]+)", "password=***"),
        (r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([^'\"&\s]+)", "api_key=***"),
        (r"token['\"]?\s*[:=]\s*['\"]?([^'\"&\s]+)", "token=***"),
        (r"secret['\"]?\s*[:=]\s*['\"]?([^'\"&\s]+)", "secret=***"),
        (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "****-****-****-****"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****"),  # SSN
    ]

    def __init__(self, patterns: list[str] | None = None) -> None:
        """Initialize sensitive data filter.

        Args:
            patterns: List of regex patterns to redact (uses defaults if None)
        """
        super().__init__()

        if patterns:
            self.patterns = [(re.compile(p, re.IGNORECASE), "***") for p in patterns]
        else:
            self.patterns = [
                (re.compile(pattern, re.IGNORECASE), replacement)
                for pattern, replacement in self.DEFAULT_PATTERNS
            ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record by redacting sensitive data.

        Args:
            record: Log record

        Returns:
            True (always pass, but modify record)
        """
        # Redact message
        record.msg = self._redact(str(record.msg))

        # Redact extra fields
        for key, value in list(record.__dict__.items()):
            if isinstance(value, str):
                setattr(record, key, self._redact(value))

        return True

    def _redact(self, text: str) -> str:
        """Redact sensitive data from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        for pattern, replacement in self.patterns:
            text = pattern.sub(replacement, text)
        return text


class ContextFilter(logging.Filter):
    """Filter to add context to log records.

    Injects context variables into log records.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record.

        Args:
            record: Log record

        Returns:
            True (always pass)
        """
        # Add context to record
        context = log_context.get()
        if context:
            for key, value in context.items():
                if not hasattr(record, key):
                    setattr(record, key, value)

        return True


class RateLimitFilter(logging.Filter):
    """Filter to rate-limit log messages.

    Prevents log flooding by limiting messages per time window.
    """

    def __init__(self, rate: int = 10, per_seconds: int = 60) -> None:
        """Initialize rate limit filter.

        Args:
            rate: Maximum number of messages
            per_seconds: Time window in seconds
        """
        super().__init__()
        self.rate = rate
        self.per_seconds = per_seconds
        self._message_counts: dict[str, list[float]] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record based on rate limit.

        Args:
            record: Log record

        Returns:
            True if record should be logged, False otherwise
        """
        import time

        message_key = f"{record.levelname}:{record.getMessage()}"
        current_time = time.time()

        # Initialize or get message times
        if message_key not in self._message_counts:
            self._message_counts[message_key] = []

        message_times = self._message_counts[message_key]

        # Remove old entries
        cutoff_time = current_time - self.per_seconds
        message_times[:] = [t for t in message_times if t > cutoff_time]

        # Check rate limit
        if len(message_times) >= self.rate:
            return False

        # Record message
        message_times.append(current_time)
        return True
