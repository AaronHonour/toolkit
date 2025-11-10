"""Integration tests for Gateway API."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestGatewayAPI:
    """Test Gateway API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_health_check(self, client):
        """Test health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_register_service(self, client):
        """Test registering a service."""
        data = {
            "service_name": "products",
            "instances": [
                {"url": "http://localhost:9001", "weight": 1},
                {"url": "http://localhost:9002", "weight": 1},
            ]
        }

        response = client.post("/api/v1/services/register", params=data)
        assert response.status_code == 200

    def test_get_metrics(self, client):
        """Test getting metrics."""
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data

    def test_gateway_route_without_service(self, client):
        """Test routing to nonexistent service."""
        response = client.get("/api/v1/gateway/nonexistent/path")
        assert response.status_code == 503
