"""Service Dependency Graph Builder - Main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.api import services, dependencies, analysis, discovery, visualization

app = FastAPI(
    title="Service Dependency Graph Builder",
    description="Automatic service dependency discovery, analysis, and visualization",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(dependencies.router, prefix="/api/v1/dependencies", tags=["Dependencies"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["Discovery"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(visualization.router, prefix="/api/v1/visualize", tags=["Visualization"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Service Dependency Graph Builder",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "services": "/api/v1/services",
            "dependencies": "/api/v1/dependencies",
            "discovery": "/api/v1/discovery",
            "analysis": "/api/v1/analysis",
            "visualization": "/api/v1/visualize",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
