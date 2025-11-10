"""Integration tests for File Processing API."""

import pytest
import io
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestFileProcessingAPI:
    """Test File Processing API endpoints."""

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

    def test_upload_file(self, client):
        """Test file upload."""
        file_content = b"hello world"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "uppercase"}

        response = client.post("/api/v1/files/process", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "job_id" in result

    def test_upload_multiple_files(self, client):
        """Test uploading multiple files."""
        for i in range(5):
            file_content = f"file{i}".encode()
            files = {"file": (f"test{i}.txt", io.BytesIO(file_content), "text/plain")}
            data = {"operation": "uppercase"}

            response = client.post("/api/v1/files/process", files=files, data=data)
            assert response.status_code == 200

    def test_get_job_status(self, client):
        """Test getting job status."""
        # Upload file first
        file_content = b"test"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "uppercase"}

        upload_response = client.post("/api/v1/files/process", files=files, data=data)
        job_id = upload_response.json()["job_id"]

        # Get status
        response = client.get(f"/api/v1/jobs/{job_id}/status")

        assert response.status_code == 200
        status = response.json()
        assert status["id"] == job_id

    def test_download_processed_file(self, client):
        """Test downloading processed file."""
        # Upload and process file
        file_content = b"hello"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "uppercase"}

        upload_response = client.post("/api/v1/files/process", files=files, data=data)
        job_id = upload_response.json()["job_id"]

        # Download result
        response = client.get(f"/api/v1/jobs/{job_id}/download")

        assert response.status_code == 200
        assert response.content == b"HELLO"

    def test_uppercase_operation(self, client):
        """Test uppercase operation."""
        file_content = b"hello world"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "uppercase"}

        upload_response = client.post("/api/v1/files/process", files=files, data=data)
        job_id = upload_response.json()["job_id"]

        response = client.get(f"/api/v1/jobs/{job_id}/download")
        assert response.content == b"HELLO WORLD"

    def test_lowercase_operation(self, client):
        """Test lowercase operation."""
        file_content = b"HELLO WORLD"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "lowercase"}

        upload_response = client.post("/api/v1/files/process", files=files, data=data)
        job_id = upload_response.json()["job_id"]

        response = client.get(f"/api/v1/jobs/{job_id}/download")
        assert response.content == b"hello world"

    def test_large_file_processing(self, client):
        """Test processing large file."""
        file_content = b"x" * 1000000  # 1MB
        files = {"file": ("large.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "uppercase"}

        response = client.post("/api/v1/files/process", files=files, data=data)

        assert response.status_code == 200

    def test_get_metrics(self, client):
        """Test getting service metrics."""
        response = client.get("/api/v1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_processed" in data

    def test_concurrent_file_uploads(self, client):
        """Test concurrent file uploads."""
        import concurrent.futures

        def upload_file(i):
            file_content = f"file{i}".encode()
            files = {"file": (f"test{i}.txt", io.BytesIO(file_content), "text/plain")}
            data = {"operation": "uppercase"}
            return client.post("/api/v1/files/process", files=files, data=data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_file, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        for response in results:
            assert response.status_code == 200

    def test_invalid_job_id(self, client):
        """Test handling invalid job ID."""
        response = client.get("/api/v1/jobs/invalid-uuid/status")

        assert response.status_code == 422  # Invalid UUID format

    def test_empty_file(self, client):
        """Test uploading empty file."""
        file_content = b""
        files = {"file": ("empty.txt", io.BytesIO(file_content), "text/plain")}
        data = {"operation": "uppercase"}

        response = client.post("/api/v1/files/process", files=files, data=data)

        assert response.status_code == 200

    def test_different_file_types(self, client):
        """Test processing different file types."""
        file_types = [
            ("test.txt", b"text content", "text/plain"),
            ("test.json", b'{"key": "value"}', "application/json"),
            ("test.csv", b"col1,col2\nval1,val2", "text/csv"),
        ]

        for filename, content, media_type in file_types:
            files = {"file": (filename, io.BytesIO(content), media_type)}
            data = {"operation": "uppercase"}

            response = client.post("/api/v1/files/process", files=files, data=data)
            assert response.status_code == 200
