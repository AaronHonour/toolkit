"""Dependency injection for agent API.

Provides shared instances of registry, event bus, and other services.
"""

from typing import AsyncGenerator, Optional

from unistax.agents import AgentRegistry
from unistax.agents.intelligence import AgentKnowledgeGraph
from unistax.agents.orchestrator import AgentOrchestrator
from unistax.events import EventBus
from unistax.logging import get_logger
from unistax.metrics import MetricsManager

logger = get_logger(__name__)

# Global instances (initialized on startup)
_registry: Optional[AgentRegistry] = None
_knowledge_graph: Optional[AgentKnowledgeGraph] = None
_orchestrator: Optional[AgentOrchestrator] = None


def initialize_agent_system(
    event_bus: Optional[EventBus] = None,
    metrics_manager: Optional[MetricsManager] = None,
) -> AgentRegistry:
    """Initialize the agent system.

    Args:
        event_bus: Optional event bus instance
        metrics_manager: Optional metrics manager instance

    Returns:
        Initialized registry
    """
    global _registry, _knowledge_graph, _orchestrator

    logger.info("Initializing agent system")

    # Create registry
    _registry = AgentRegistry(
        event_bus=event_bus or EventBus(),
        metrics_manager=metrics_manager or MetricsManager(),
    )

    # Create knowledge graph
    _knowledge_graph = AgentKnowledgeGraph()

    # Create orchestrator
    _orchestrator = AgentOrchestrator(registry=_registry)

    logger.info("Agent system initialized successfully")

    return _registry


def shutdown_agent_system():
    """Shutdown the agent system."""
    global _registry, _knowledge_graph, _orchestrator

    logger.info("Shutting down agent system")

    _registry = None
    _knowledge_graph = None
    _orchestrator = None

    logger.info("Agent system shutdown complete")


async def get_registry() -> AsyncGenerator[AgentRegistry, None]:
    """Get agent registry dependency.

    Yields:
        AgentRegistry instance
    """
    if _registry is None:
        raise RuntimeError("Agent system not initialized. Call initialize_agent_system() first.")

    yield _registry


async def get_knowledge_graph() -> AsyncGenerator[AgentKnowledgeGraph, None]:
    """Get knowledge graph dependency.

    Yields:
        AgentKnowledgeGraph instance
    """
    if _knowledge_graph is None:
        raise RuntimeError("Agent system not initialized. Call initialize_agent_system() first.")

    yield _knowledge_graph


async def get_orchestrator() -> AsyncGenerator[AgentOrchestrator, None]:
    """Get orchestrator dependency.

    Yields:
        AgentOrchestrator instance
    """
    if _orchestrator is None:
        raise RuntimeError("Agent system not initialized. Call initialize_agent_system() first.")

    yield _orchestrator


def get_event_bus() -> EventBus:
    """Get event bus instance.

    Returns:
        EventBus instance
    """
    if _registry is None:
        raise RuntimeError("Agent system not initialized. Call initialize_agent_system() first.")

    return _registry.event_bus


def get_metrics_manager() -> MetricsManager:
    """Get metrics manager instance.

    Returns:
        MetricsManager instance
    """
    if _registry is None:
        raise RuntimeError("Agent system not initialized. Call initialize_agent_system() first.")

    return _registry.metrics_manager
