"""Unit tests for Event domain model."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.models.event import Event, EventType


class TestEventModel:
    """Test Event model."""

    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={"page": "/home"},
            timestamp=datetime.now(timezone.utc),
            source="web",
            version="1.0",
        )

        assert event.id is not None
        assert event.event_type == EventType.PAGE_VIEW
        assert event.user_id == "user123"
        assert event.session_id == "session456"
        assert event.properties["page"] == "/home"

    def test_event_slots_optimization(self):
        """Test __slots__ memory optimization."""
        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=datetime.now(timezone.utc),
        )

        # Should not be able to add arbitrary attributes
        with pytest.raises(AttributeError):
            event.new_attribute = "value"

    def test_event_types(self):
        """Test all event types."""
        event_types = [
            EventType.PAGE_VIEW,
            EventType.BUTTON_CLICK,
            EventType.FORM_SUBMIT,
            EventType.API_CALL,
            EventType.ERROR,
        ]

        for event_type in event_types:
            event = Event(
                id=str(uuid4()),
                event_type=event_type,
                user_id="user123",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            assert event.event_type == event_type

    def test_event_with_complex_properties(self):
        """Test event with complex property structure."""
        properties = {
            "page": "/product/123",
            "referrer": "https://google.com",
            "user_agent": "Mozilla/5.0",
            "screen_resolution": "1920x1080",
            "metadata": {
                "nested": "value",
                "list": [1, 2, 3],
            },
        }

        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties=properties,
            timestamp=datetime.now(timezone.utc),
        )

        assert event.properties["page"] == "/product/123"
        assert event.properties["metadata"]["nested"] == "value"
        assert event.properties["metadata"]["list"] == [1, 2, 3]

    def test_event_default_values(self):
        """Test event with default values."""
        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=datetime.now(timezone.utc),
        )

        assert event.source == "unknown"
        assert event.version == "1.0"

    def test_event_timestamp(self):
        """Test event timestamp handling."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=now,
        )

        assert event.timestamp == now
        assert isinstance(event.timestamp, datetime)

    def test_event_id_uniqueness(self):
        """Test that event IDs are unique."""
        event1 = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=datetime.now(timezone.utc),
        )

        event2 = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=datetime.now(timezone.utc),
        )

        assert event1.id != event2.id

    def test_event_session_tracking(self):
        """Test event session tracking."""
        session_id = "session123"

        events = [
            Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id="user123",
                session_id=session_id,
                properties={"page": f"/page{i}"},
                timestamp=datetime.now(timezone.utc),
            )
            for i in range(5)
        ]

        # All events should have same session
        for event in events:
            assert event.session_id == session_id

    def test_event_user_tracking(self):
        """Test event user tracking across sessions."""
        user_id = "user123"

        events = [
            Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=user_id,
                session_id=f"session{i}",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            for i in range(5)
        ]

        # All events should have same user
        for event in events:
            assert event.user_id == user_id

    def test_event_error_tracking(self):
        """Test error event tracking."""
        error_properties = {
            "error_type": "TypeError",
            "error_message": "Cannot read property 'x' of undefined",
            "stack_trace": "at line 123",
            "url": "/app/page",
        }

        event = Event(
            id=str(uuid4()),
            event_type=EventType.ERROR,
            user_id="user123",
            session_id="session456",
            properties=error_properties,
            timestamp=datetime.now(timezone.utc),
        )

        assert event.event_type == EventType.ERROR
        assert event.properties["error_type"] == "TypeError"
        assert "stack_trace" in event.properties

    def test_event_api_call_tracking(self):
        """Test API call event tracking."""
        api_properties = {
            "endpoint": "/api/users",
            "method": "GET",
            "status_code": 200,
            "duration_ms": 150,
            "response_size": 1024,
        }

        event = Event(
            id=str(uuid4()),
            event_type=EventType.API_CALL,
            user_id="user123",
            session_id="session456",
            properties=api_properties,
            timestamp=datetime.now(timezone.utc),
        )

        assert event.event_type == EventType.API_CALL
        assert event.properties["endpoint"] == "/api/users"
        assert event.properties["status_code"] == 200

    def test_event_button_click_tracking(self):
        """Test button click event tracking."""
        click_properties = {
            "button_id": "submit-btn",
            "button_text": "Submit Form",
            "page": "/checkout",
            "position": {"x": 100, "y": 200},
        }

        event = Event(
            id=str(uuid4()),
            event_type=EventType.BUTTON_CLICK,
            user_id="user123",
            session_id="session456",
            properties=click_properties,
            timestamp=datetime.now(timezone.utc),
        )

        assert event.event_type == EventType.BUTTON_CLICK
        assert event.properties["button_id"] == "submit-btn"

    def test_event_form_submit_tracking(self):
        """Test form submit event tracking."""
        form_properties = {
            "form_id": "signup-form",
            "form_name": "User Registration",
            "fields": ["email", "password", "name"],
            "validation_errors": [],
        }

        event = Event(
            id=str(uuid4()),
            event_type=EventType.FORM_SUBMIT,
            user_id="user123",
            session_id="session456",
            properties=form_properties,
            timestamp=datetime.now(timezone.utc),
        )

        assert event.event_type == EventType.FORM_SUBMIT
        assert event.properties["form_id"] == "signup-form"
        assert len(event.properties["fields"]) == 3

    def test_event_source_tracking(self):
        """Test event source tracking."""
        sources = ["web", "mobile", "api", "webhook"]

        for source in sources:
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id="user123",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
                source=source,
            )
            assert event.source == source

    def test_event_version_tracking(self):
        """Test event version tracking."""
        versions = ["1.0", "1.1", "2.0"]

        for version in versions:
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id="user123",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
                version=version,
            )
            assert event.version == version
