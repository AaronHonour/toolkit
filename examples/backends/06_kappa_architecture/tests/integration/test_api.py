"""Integration tests for Kappa Architecture API."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestKappaAPI:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_ingest_event(self, client):
        response = client.post("/api/v1/events", json={
            "event_type": "page_view",
            "user_id": "user123",
            "data": {"page": "/home"}
        })
        assert response.status_code == 200
        assert "id" in response.json()

    def test_ingest_batch(self, client):
        response = client.post("/api/v1/events/batch", json={
            "events": [
                {"event_type": "page_view", "user_id": f"user{i}", "data": {}}
                for i in range(10)
            ]
        })
        assert response.status_code == 200
        assert response.json()["ingested"] == 10

    def test_get_metrics(self, client):
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200

    def test_get_aggregation_view(self, client):
        # Ingest some events first
        for i in range(5):
            client.post("/api/v1/events", json={
                "event_type": "page_view",
                "user_id": f"user{i}",
                "data": {}
            })

        response = client.get("/api/v1/views/aggregation")
        assert response.status_code == 200
