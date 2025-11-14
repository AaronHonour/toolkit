"""Agent Framework REST API.

Provides comprehensive REST API endpoints for managing and orchestrating
autonomous agents.

Quick Start:
    >>> from unistax.agents.api import create_agent_api
    >>>
    >>> app = create_agent_api()
    >>> # Run with: uvicorn module:app

Features:
    - Agent management (CRUD)
    - Task submission and monitoring
    - Team management
    - Agent discovery
    - Workflow orchestration
    - Knowledge graph
    - Metrics and monitoring
    - WebSocket real-time updates
"""

from unistax.agents.api.app import app, create_agent_api
from unistax.agents.api.dependencies import (
    get_event_bus,
    get_knowledge_graph,
    get_metrics_manager,
    get_orchestrator,
    get_registry,
    initialize_agent_system,
    shutdown_agent_system,
)

__all__ = [
    # Application
    "app",
    "create_agent_api",
    # Dependencies
    "get_registry",
    "get_knowledge_graph",
    "get_orchestrator",
    "get_event_bus",
    "get_metrics_manager",
    "initialize_agent_system",
    "shutdown_agent_system",
]
