"""Integration tests for Analytics API."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from src.main import app
from src.domain.models.event import EventType


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAnalyticsAPI:
    """Test Analytics API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Real-Time Analytics Dashboard"
        assert "version" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics-dashboard"

    def test_ingest_single_event(self, client):
        """Test ingesting single event."""
        event_data = {
            "id": str(uuid4()),
            "event_type": "page_view",
            "user_id": "user123",
            "session_id": "session456",
            "properties": {"page": "/home"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "web",
            "version": "1.0",
        }

        response = client.post("/api/v1/events", json=event_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ingested"
        assert data["event_id"] == event_data["id"]

    def test_ingest_multiple_events(self, client):
        """Test ingesting multiple events."""
        # Ingest 10 events
        for i in range(10):
            event_data = {
                "id": str(uuid4()),
                "event_type": "page_view",
                "user_id": f"user{i}",
                "session_id": "session456",
                "properties": {"page": f"/page{i}"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            response = client.post("/api/v1/events", json=event_data)
            assert response.status_code == 200

    def test_ingest_different_event_types(self, client):
        """Test ingesting different event types."""
        event_types = ["page_view", "button_click", "form_submit", "api_call", "error"]

        for event_type in event_types:
            event_data = {
                "id": str(uuid4()),
                "event_type": event_type,
                "user_id": "user123",
                "session_id": "session456",
                "properties": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            response = client.post("/api/v1/events", json=event_data)
            assert response.status_code == 200

    def test_ingest_duplicate_event(self, client):
        """Test that duplicate events are handled."""
        event_data = {
            "id": str(uuid4()),
            "event_type": "page_view",
            "user_id": "user123",
            "session_id": "session456",
            "properties": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Ingest first time
        response1 = client.post("/api/v1/events", json=event_data)
        assert response1.status_code == 200

        # Ingest same event again
        response2 = client.post("/api/v1/events", json=event_data)
        # Should still return 200 but might be flagged as duplicate
        assert response2.status_code == 200

    def test_get_analytics(self, client):
        """Test getting analytics."""
        # Ingest some events first
        for i in range(5):
            event_data = {
                "id": str(uuid4()),
                "event_type": "page_view",
                "user_id": f"user{i}",
                "session_id": f"session{i}",
                "properties": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            client.post("/api/v1/events", json=event_data)

        # Get analytics
        response = client.get("/api/v1/analytics")

        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "unique_users" in data
        assert "unique_sessions" in data

    def test_get_metrics(self, client):
        """Test getting metrics."""
        response = client.get("/api/v1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "events_processed" in data
        assert "events_per_second" in data
        assert "buffer_size" in data

    def test_ingest_event_with_complex_properties(self, client):
        """Test ingesting event with complex properties."""
        event_data = {
            "id": str(uuid4()),
            "event_type": "page_view",
            "user_id": "user123",
            "session_id": "session456",
            "properties": {
                "page": "/product/123",
                "referrer": "https://google.com",
                "metadata": {
                    "nested": "value",
                    "list": [1, 2, 3],
                },
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = client.post("/api/v1/events", json=event_data)

        assert response.status_code == 200

    def test_ingest_error_event(self, client):
        """Test ingesting error event."""
        event_data = {
            "id": str(uuid4()),
            "event_type": "error",
            "user_id": "user123",
            "session_id": "session456",
            "properties": {
                "error_type": "TypeError",
                "error_message": "Cannot read property 'x'",
                "stack_trace": "at line 123",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = client.post("/api/v1/events", json=event_data)

        assert response.status_code == 200

    def test_ingest_api_call_event(self, client):
        """Test ingesting API call event."""
        event_data = {
            "id": str(uuid4()),
            "event_type": "api_call",
            "user_id": "user123",
            "session_id": "session456",
            "properties": {
                "endpoint": "/api/users",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 150,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = client.post("/api/v1/events", json=event_data)

        assert response.status_code == 200

    def test_high_volume_ingestion(self, client):
        """Test high-volume event ingestion."""
        # Ingest 100 events rapidly
        for i in range(100):
            event_data = {
                "id": str(uuid4()),
                "event_type": "page_view",
                "user_id": f"user{i}",
                "session_id": f"session{i % 10}",
                "properties": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            response = client.post("/api/v1/events", json=event_data)
            assert response.status_code == 200

        # Verify analytics reflect the events
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200

    def test_analytics_aggregation(self, client):
        """Test analytics aggregation across multiple events."""
        # Ingest events for multiple users and sessions
        for user_id in range(5):
            for session_id in range(3):
                for _ in range(2):
                    event_data = {
                        "id": str(uuid4()),
                        "event_type": "page_view",
                        "user_id": f"user{user_id}",
                        "session_id": f"session{session_id}",
                        "properties": {},
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    client.post("/api/v1/events", json=event_data)

        # Get analytics
        response = client.get("/api/v1/analytics")
        data = response.json()

        # Should have 5 unique users
        assert data["unique_users"] >= 5

        # Should have 3 unique sessions
        assert data["unique_sessions"] >= 3

        # Should have 30 total events (5 users * 3 sessions * 2 events)
        assert data["total_events"] >= 30

    def test_event_type_filtering(self, client):
        """Test that analytics can track different event types."""
        event_types = ["page_view", "button_click", "form_submit"]

        for event_type in event_types:
            for i in range(10):
                event_data = {
                    "id": str(uuid4()),
                    "event_type": event_type,
                    "user_id": f"user{i}",
                    "session_id": "session123",
                    "properties": {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                client.post("/api/v1/events", json=event_data)

        # Get analytics
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200

    def test_session_tracking(self, client):
        """Test session tracking across events."""
        session_id = "session_xyz"

        # Multiple events in same session
        for i in range(5):
            event_data = {
                "id": str(uuid4()),
                "event_type": "page_view",
                "user_id": "user123",
                "session_id": session_id,
                "properties": {"page": f"/page{i}"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            client.post("/api/v1/events", json=event_data)

        # Get analytics
        response = client.get("/api/v1/analytics")
        data = response.json()

        # Should track single session
        assert data["unique_sessions"] >= 1

    def test_concurrent_event_ingestion(self, client):
        """Test concurrent event ingestion."""
        import concurrent.futures

        def ingest_event(i):
            event_data = {
                "id": str(uuid4()),
                "event_type": "page_view",
                "user_id": f"user{i}",
                "session_id": f"session{i}",
                "properties": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            return client.post("/api/v1/events", json=event_data)

        # Ingest 50 events concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(ingest_event, i) for i in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        for response in results:
            assert response.status_code == 200

    def test_invalid_event_type(self, client):
        """Test handling of invalid event type."""
        event_data = {
            "id": str(uuid4()),
            "event_type": "invalid_type",
            "user_id": "user123",
            "session_id": "session456",
            "properties": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = client.post("/api/v1/events", json=event_data)

        # Should return error for invalid type
        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        # Missing user_id
        event_data = {
            "id": str(uuid4()),
            "event_type": "page_view",
            "session_id": "session456",
            "properties": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = client.post("/api/v1/events", json=event_data)

        # Should return validation error
        assert response.status_code == 422
