"""Agent API application factory.

Creates a FastAPI application with all agent endpoints.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from unistax.agents.api import dependencies
from unistax.agents.api.routers.agents import (
    discovery_router,
    knowledge_router,
    management_router,
    metrics_router,
    tasks_router,
    teams_router,
    websocket_router,
    workflows_router,
)
from unistax.events import EventBus
from unistax.logging import get_logger
from unistax.metrics import MetricsManager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager.

    Handles startup and shutdown of the agent system.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    logger.info("Starting agent API")

    # Initialize agent system
    event_bus = EventBus()
    metrics_manager = MetricsManager()

    registry = dependencies.initialize_agent_system(
        event_bus=event_bus,
        metrics_manager=metrics_manager,
    )

    logger.info(
        f"Agent system initialized: {len(registry.agents)} agents, "
        f"{len(registry.teams)} teams"
    )

    yield

    # Shutdown
    logger.info("Shutting down agent API")
    dependencies.shutdown_agent_system()
    logger.info("Agent API shutdown complete")


def create_agent_api(
    title: str = "Agent API",
    version: str = "1.0.0",
    description: str | None = None,
    docs_url: str = "/docs",
    redoc_url: str = "/redoc",
    openapi_url: str = "/openapi.json",
    root_path: str = "",
) -> FastAPI:
    """Create Agent API application.

    Args:
        title: API title
        version: API version
        description: API description
        docs_url: Swagger UI docs URL
        redoc_url: ReDoc docs URL
        openapi_url: OpenAPI schema URL
        root_path: Root path for API (for reverse proxy)

    Returns:
        FastAPI application

    Example:
        >>> app = create_agent_api()
        >>> # Run with: uvicorn module:app --host 0.0.0.0 --port 8000
    """
    if description is None:
        description = """
        # Agent Framework API

        REST API for managing and orchestrating autonomous agents.

        ## Features

        - **Agent Management**: Create, update, delete, and monitor agents
        - **Task Management**: Submit tasks, monitor execution, and track results
        - **Team Management**: Organize agents into hierarchical teams
        - **Discovery**: Find agents by persona, skills, or team
        - **Workflows**: Orchestrate multi-agent workflows with dependencies
        - **Knowledge Graph**: Share knowledge and best practices across agents
        - **Metrics**: Monitor agent and system performance
        - **WebSocket**: Real-time updates via WebSocket connections

        ## Agent Personas

        - **Engineer**: Data engineering, ETL, pipeline development
        - **Analyst**: Data analysis, reporting, visualization
        - **Scientist**: ML model training, experimentation, deployment
        - **Steward**: Data governance, compliance, metadata management

        ## Quick Start

        1. Create an agent: `POST /agents`
        2. Submit a task: `POST /tasks`
        3. Monitor progress: `GET /tasks/{task_id}`
        4. View metrics: `GET /metrics/system`
        """

    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        root_path=root_path,
        lifespan=lifespan,
    )

    # Include routers
    app.include_router(management_router)
    app.include_router(tasks_router)
    app.include_router(teams_router)
    app.include_router(discovery_router)
    app.include_router(workflows_router)
    app.include_router(knowledge_router)
    app.include_router(metrics_router)
    app.include_router(websocket_router)

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """API root endpoint."""
        return {
            "message": "Agent Framework API",
            "version": version,
            "docs": docs_url,
            "endpoints": {
                "agents": "/agents",
                "tasks": "/tasks",
                "teams": "/teams",
                "discovery": "/discovery",
                "workflows": "/workflows",
                "knowledge": "/knowledge",
                "metrics": "/metrics",
                "websocket": "/ws",
            },
        }

    logger.info(f"Agent API created: {title} v{version}")

    return app


# Default application instance
app = create_agent_api()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "unistax.agents.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
