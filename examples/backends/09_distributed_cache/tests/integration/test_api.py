"""Integration tests for Distributed Cache API."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestCacheAPI:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_put_and_get(self, client):
        # Put value
        response = client.put("/api/v1/cache/testkey", json={"value": "testvalue"})
        assert response.status_code == 200

        # Get value
        response = client.get("/api/v1/cache/testkey")
        assert response.status_code == 200
        assert response.json()["found"] is True
        assert response.json()["value"] == "testvalue"

    def test_get_missing(self, client):
        response = client.get("/api/v1/cache/missing")
        assert response.status_code == 200
        assert response.json()["found"] is False

    def test_get_stats(self, client):
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        assert "hits" in response.json()
        assert "misses" in response.json()

    def test_delete(self, client):
        client.put("/api/v1/cache/deletekey", json={"value": "test"})
        response = client.delete("/api/v1/cache/deletekey")
        assert response.status_code == 200
