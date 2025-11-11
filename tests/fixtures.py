"""Pytest fixtures for testing toolkit modules."""

import pytest
import tempfile
import os
from typing import Generator
from unittest.mock import MagicMock, Mock


# Configuration fixtures
@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Provide temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_config_file(temp_dir) -> str:
    """Create test config YAML file."""
    config_path = os.path.join(temp_dir, "config.yaml")
    with open(config_path, "w") as f:
        f.write("""
app:
  name: test-app
  debug: true

database:
  url: sqlite:///:memory:

redis:
  host: localhost
  port: 6379
""")
    return config_path


# Database fixtures
@pytest.fixture
def mock_db_session():
    """Provide mock database session."""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.first.return_value = None
    session.all.return_value = []
    return session


@pytest.fixture
def mock_engine():
    """Provide mock database engine."""
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = MagicMock()
    return engine


# Cache fixtures
@pytest.fixture
def mock_redis_client():
    """Provide mock Redis client."""
    client = MagicMock()
    client.get.return_value = None
    client.set.return_value = True
    client.delete.return_value = 1
    client.exists.return_value = False
    return client


@pytest.fixture
def in_memory_cache():
    """Provide in-memory cache for testing."""
    from unistax.cache import CacheManager
    return CacheManager(backend="memory")


# HTTP fixtures
@pytest.fixture
def mock_http_response():
    """Provide mock HTTP response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"status": "success"}
    response.text = '{"status": "success"}'
    return response


@pytest.fixture
def mock_http_client(mock_http_response):
    """Provide mock HTTP client."""
    client = MagicMock()
    client.get.return_value = mock_http_response
    client.post.return_value = mock_http_response
    return client


# Logging fixtures
@pytest.fixture
def mock_logger():
    """Provide mock logger."""
    logger = MagicMock()
    logger.debug.return_value = None
    logger.info.return_value = None
    logger.warning.return_value = None
    logger.error.return_value = None
    logger.critical.return_value = None
    return logger


# Metrics fixtures
@pytest.fixture
def mock_metrics():
    """Provide mock metrics manager."""
    metrics = MagicMock()
    metrics.counter.return_value = None
    metrics.gauge.return_value = None
    metrics.histogram.return_value = None
    return metrics


# Event bus fixtures
@pytest.fixture
def mock_event_bus():
    """Provide mock event bus."""
    bus = MagicMock()
    bus.subscribe.return_value = None
    bus.publish.return_value = None
    return bus


# DI container fixtures
@pytest.fixture
def test_container():
    """Provide DI container for testing."""
    from unistax.di import Container
    container = Container()
    yield container
    # Cleanup


# Storage fixtures
@pytest.fixture
def temp_storage(temp_dir):
    """Provide temporary file storage."""
    from unistax.storage import LocalStorage
    return LocalStorage(base_path=temp_dir)


# Queue fixtures
@pytest.fixture
def mock_queue():
    """Provide mock message queue."""
    queue = MagicMock()
    queue.send.return_value = "message-id-123"
    queue.receive.return_value = []
    return queue


# Task fixtures
@pytest.fixture
def mock_celery_app():
    """Provide mock Celery app."""
    app = MagicMock()
    app.send_task.return_value = MagicMock()
    return app


@pytest.fixture
def mock_scheduler():
    """Provide mock scheduler."""
    scheduler = MagicMock()
    scheduler.add_job.return_value = "job-id-123"
    return scheduler


# Notification fixtures
@pytest.fixture
def mock_notification_channel():
    """Provide mock notification channel."""
    channel = MagicMock()
    channel.send.return_value = "notification-id-123"
    return channel


# Security fixtures
@pytest.fixture
def test_jwt_secret():
    """Provide test JWT secret."""
    return "test-secret-key-for-jwt"


@pytest.fixture
def mock_password_hasher():
    """Provide mock password hasher."""
    hasher = MagicMock()
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    return hasher


# Repository fixtures
@pytest.fixture
def mock_repository():
    """Provide mock repository."""
    repo = MagicMock()
    repo.add.return_value = None
    repo.get.return_value = None
    repo.update.return_value = None
    repo.delete.return_value = None
    repo.find.return_value = []
    return repo


# API fixtures
@pytest.fixture
def test_client():
    """Provide FastAPI test client."""
    from fastapi.testclient import TestClient
    from unistax.api import APIApplication

    app = APIApplication(title="Test API")
    return TestClient(app.get_app())


# Pagination fixtures
@pytest.fixture
def pagination_params():
    """Provide test pagination params."""
    from unistax.pagination import PaginationParams
    return PaginationParams(page=1, page_size=20)


# Feature flag fixtures
@pytest.fixture
def mock_feature_manager():
    """Provide mock feature manager."""
    manager = MagicMock()
    manager.is_enabled.return_value = True
    return manager


# Audit fixtures
@pytest.fixture
def mock_audit_logger():
    """Provide mock audit logger."""
    logger = MagicMock()
    logger.log.return_value = None
    return logger


# Tracing fixtures
@pytest.fixture
def mock_tracer():
    """Provide mock tracer."""
    tracer = MagicMock()
    tracer.start_span.return_value.__enter__.return_value = MagicMock()
    return tracer


# Performance testing fixtures
@pytest.fixture
def performance_metrics():
    """Provide dictionary for collecting performance metrics."""
    return {
        "latencies": [],
        "throughput": [],
        "memory": [],
        "cpu": [],
    }


@pytest.fixture
def benchmark_iterations():
    """Number of iterations for benchmarks."""
    return 100


# Async fixtures
@pytest.fixture
async def async_mock_db_session():
    """Provide async mock database session."""
    session = MagicMock()
    # Configure async methods
    return session


# Cleanup fixtures
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    yield
    # Reset any global state here


@pytest.fixture(autouse=True)
def reset_factories():
    """Reset factory sequences."""
    from tests.factories import Factory
    Factory.reset_sequence()
    yield
