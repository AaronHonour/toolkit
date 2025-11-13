"""Notification channel backends."""

import uuid
from abc import ABC, abstractmethod

from unistax.notifications.manager import Notification


class ChannelBackend(ABC):
    """Base channel backend."""

    @abstractmethod
    def send(self, notification: Notification) -> str:
        """Send notification."""
        pass


class EmailChannel(ChannelBackend):
    """Email channel."""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str) -> None:
        """Initialize email channel."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send(self, notification: Notification) -> str:
        """Send email."""
        # Implementation requires smtplib or email library
        return str(uuid.uuid4())


class SMSChannel(ChannelBackend):
    """SMS channel."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        """Initialize SMS channel."""
        self.api_key = api_key
        self.api_secret = api_secret

    def send(self, notification: Notification) -> str:
        """Send SMS."""
        # Implementation requires Twilio or similar
        return str(uuid.uuid4())


class PushChannel(ChannelBackend):
    """Push notification channel."""

    def __init__(self, api_key: str) -> None:
        """Initialize push channel."""
        self.api_key = api_key

    def send(self, notification: Notification) -> str:
        """Send push notification."""
        # Implementation requires FCM or APNS
        return str(uuid.uuid4())
