"""Integration tests for Export API."""

import pytest
from fastapi.testclient import TestClient

from src.main import app, ExportFormat, CompressionType


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestExportAPI:
    """Test Export API endpoints."""

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

    def test_create_export_job(self, client):
        """Test creating export job."""
        response = client.post(
            "/api/v1/export",
            params={
                "format": "json",
                "compression": "none",
                "record_count": 100,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

    def test_create_json_export(self, client):
        """Test creating JSON export."""
        response = client.post(
            "/api/v1/export",
            params={
                "format": "json",
                "compression": "lz4",
                "record_count": 100,
            }
        )

        assert response.status_code == 200
        assert response.json()["format"] == "json"

    def test_create_csv_export(self, client):
        """Test creating CSV export."""
        response = client.post(
            "/api/v1/export",
            params={
                "format": "csv",
                "compression": "gzip",
                "record_count": 100,
            }
        )

        assert response.status_code == 200
        assert response.json()["format"] == "csv"

    def test_create_msgpack_export(self, client):
        """Test creating MessagePack export."""
        response = client.post(
            "/api/v1/export",
            params={
                "format": "msgpack",
                "compression": "snappy",
                "record_count": 100,
            }
        )

        assert response.status_code == 200
        assert response.json()["format"] == "msgpack"

    def test_get_export_status(self, client):
        """Test getting export status."""
        # Create export
        create_response = client.post(
            "/api/v1/export",
            params={
                "format": "json",
                "compression": "none",
                "record_count": 10,
            }
        )

        job_id = create_response.json()["job_id"]

        # Get status
        import time
        time.sleep(0.1)  # Give it time to process

        status_response = client.get(f"/api/v1/exports/{job_id}/status")

        assert status_response.status_code == 200
        data = status_response.json()
        assert data["job_id"] == job_id

    def test_get_metrics(self, client):
        """Test getting metrics."""
        response = client.get("/api/v1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_jobs" in data
        assert "total_records_exported" in data

    def test_large_export(self, client):
        """Test large export."""
        response = client.post(
            "/api/v1/export",
            params={
                "format": "json",
                "compression": "lz4",
                "record_count": 10000,
            }
        )

        assert response.status_code == 200

    def test_multiple_exports(self, client):
        """Test multiple concurrent exports."""
        for i in range(5):
            response = client.post(
                "/api/v1/export",
                params={
                    "format": "json",
                    "compression": "none",
                    "record_count": 100,
                }
            )
            assert response.status_code == 200

    def test_different_compressions(self, client):
        """Test different compression types."""
        compressions = ["none", "lz4", "snappy", "gzip"]

        for compression in compressions:
            response = client.post(
                "/api/v1/export",
                params={
                    "format": "json",
                    "compression": compression,
                    "record_count": 100,
                }
            )
            assert response.status_code == 200
