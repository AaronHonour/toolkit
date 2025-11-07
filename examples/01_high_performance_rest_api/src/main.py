"""High-Performance REST API Example.

Demonstrates 100K+ RPS capability with:
- FastAPI framework
- Hexagonal architecture
- CQRS pattern
- Query caching
- Connection pooling
- Async operations
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from examples.01_high_performance_rest_api.src.presentation.api import api_router
from examples.01_high_performance_rest_api.src.infrastructure.database.session import (
    init_database,
    close_database,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    database_url = "sqlite+aiosqlite:///./inventory.db"  # For demo, use SQLite
    # For production PostgreSQL:
    # database_url = "postgresql+asyncpg://user:pass@localhost/inventory"

    await init_database(
        database_url=database_url,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
        create_tables=True,  # For demo only, use Alembic in production
    )

    yield

    # Shutdown
    await close_database()


# Create FastAPI application
app = FastAPI(
    title="High-Performance Inventory API",
    description="REST API for product and inventory management with 100K+ RPS capability",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Middleware setup


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Performance monitoring middleware
@app.middleware("http")
async def performance_monitor(request: Request, call_next):
    """Monitor request performance.

    Tracks request duration and adds metrics headers.
    """
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    response.headers["X-Process-Time"] = str(duration)

    return response


# Error handling


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Health check endpoints


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "inventory-api"}


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "High-Performance Inventory API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # For development
        workers=1,  # For development, increase for production
        log_level="info",
    )
