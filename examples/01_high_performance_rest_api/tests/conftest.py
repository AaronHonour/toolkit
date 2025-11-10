"""Pytest configuration and fixtures for tests."""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from examples.01_high_performance_rest_api.src.infrastructure.database.models import Base
from examples.01_high_performance_rest_api.src.infrastructure.database.session import DatabaseSession
from examples.01_high_performance_rest_api.src.main import app


# Event loop configuration
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database fixtures
@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[DatabaseSession, None]:
    """Create test database with clean state for each test."""
    # Use in-memory SQLite for fast tests
    database_url = "sqlite+aiosqlite:///:memory:"

    db = DatabaseSession(
        database_url=database_url,
        pool_size=5,
        max_overflow=0,
        pool_pre_ping=False,
        echo=False,
    )

    await db.initialize()
    await db.create_tables()

    yield db

    await db.close()


@pytest.fixture(scope="function")
async def db_session(test_db: DatabaseSession) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for tests."""
    async with test_db.session() as session:
        yield session
        await session.rollback()


# FastAPI fixtures
@pytest.fixture(scope="function")
async def test_app(test_db: DatabaseSession) -> FastAPI:
    """Get FastAPI app instance for tests."""
    # Override database dependency
    from examples.01_high_performance_rest_api.src.presentation.dependencies import get_db_session
    from examples.01_high_performance_rest_api.src.infrastructure.database.session import _db_session

    # Temporarily replace global db
    import examples.01_high_performance_rest_api.src.infrastructure.database.session as session_module
    original_db = session_module._db_session
    session_module._db_session = test_db

    yield app

    # Restore original
    session_module._db_session = original_db


@pytest.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Get async HTTP client for API tests."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


# Test data factories
@pytest.fixture
def sample_product_data() -> dict:
    """Sample product data for tests."""
    return {
        "sku": f"TEST-{uuid4().hex[:8].upper()}",
        "name": "Test Product",
        "description": "A test product for unit tests",
        "category": "Test Category",
        "price": "99.99",
        "cost": "45.00",
        "tags": ["test", "sample"],
        "metadata": {"test": True},
    }


@pytest.fixture
def sample_inventory_data(sample_product_data) -> dict:
    """Sample inventory data for tests."""
    return {
        "product_id": str(uuid4()),
        "quantity": 100,
        "reorder_point": 20,
        "reorder_quantity": 50,
        "warehouse_location": "A-101",
    }


# Benchmark fixtures
@pytest.fixture
def benchmark_product_data() -> list[dict]:
    """Generate multiple product data for benchmarks."""
    return [
        {
            "sku": f"BENCH-{i:08d}",
            "name": f"Benchmark Product {i}",
            "description": f"Product for benchmark test {i}",
            "category": f"Category-{i % 10}",
            "price": "99.99",
            "cost": "45.00",
            "tags": ["benchmark"],
            "metadata": {},
        }
        for i in range(1000)
    ]
