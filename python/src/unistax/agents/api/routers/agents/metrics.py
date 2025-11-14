"""Metrics and monitoring endpoints."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from unistax.agents.api.dependencies import get_knowledge_graph, get_registry
from unistax.agents.api.schemas import AgentMetricsResponse, HealthResponse, SystemMetricsResponse
from unistax.agents.intelligence import AgentKnowledgeGraph
from unistax.agents import AgentRegistry
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/metrics", tags=["Metrics & Monitoring"])
logger = get_logger(__name__)

# Track system start time
_system_start_time = time.time()


@router.get(
    "/health",
    response_model=APIResponse[HealthResponse],
    summary="Health check",
    description="Check health status of the agent system",
)
async def health_check(
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[HealthResponse]:
    """Health check endpoint."""
    logger.debug("Health check requested")

    # Count healthy agents (not failed)
    healthy_agents = sum(
        1 for agent in registry.agents.values() if agent.state.value != "failed"
    )
    total_agents = len(registry.agents)

    # Determine health status
    if total_agents == 0:
        health_status = "healthy"  # No agents yet
    elif healthy_agents == total_agents:
        health_status = "healthy"
    elif healthy_agents >= total_agents * 0.7:
        health_status = "degraded"
    else:
        health_status = "unhealthy"

    health = HealthResponse(
        status=health_status,
        timestamp=time.time(),
        version="1.0.0",
        agents_healthy=healthy_agents,
        agents_total=total_agents,
        details={
            "registry": "connected",
            "event_bus": "active",
        },
    )

    return APIResponse(success=True, data=health)


@router.get(
    "/agents/{agent_id}",
    response_model=APIResponse[AgentMetricsResponse],
    summary="Get agent metrics",
    description="Get detailed metrics for a specific agent",
)
async def get_agent_metrics(
    agent_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentMetricsResponse]:
    """Get agent metrics."""
    logger.debug(f"Getting metrics for agent: {agent_id}")

    agent = registry.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Calculate metrics
    total_tasks = agent.completed_tasks + agent.failed_tasks
    success_rate = agent.completed_tasks / total_tasks if total_tasks > 0 else 0.0

    metrics = AgentMetricsResponse(
        agent_id=agent.agent_id,
        uptime_seconds=0.0,  # Would need to track
        total_tasks=total_tasks,
        completed_tasks=agent.completed_tasks,
        failed_tasks=agent.failed_tasks,
        success_rate=success_rate,
        avg_task_duration=None,  # Would need task history
        current_task_count=len(agent.current_tasks),
        messages_sent=agent.messages_sent,
        messages_received=agent.messages_received,
        collaboration_count=0,  # Would need to track
        last_active_timestamp=time.time(),
    )

    return APIResponse(success=True, data=metrics)


@router.get(
    "/system",
    response_model=APIResponse[SystemMetricsResponse],
    summary="Get system metrics",
    description="Get system-wide metrics across all agents",
)
async def get_system_metrics(
    registry: Annotated[AgentRegistry, Depends(get_registry)],
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[SystemMetricsResponse]:
    """Get system-wide metrics."""
    logger.debug("Getting system metrics")

    agents = list(registry.agents.values())

    # Count agents by state
    active_agents = sum(1 for a in agents if a.state.value == "active")
    idle_agents = sum(1 for a in agents if a.state.value == "idle")
    busy_agents = sum(1 for a in agents if a.state.value == "busy")

    # Task counts
    total_tasks = sum(a.completed_tasks + a.failed_tasks for a in agents)
    completed_tasks = sum(a.completed_tasks for a in agents)
    failed_tasks = sum(a.failed_tasks for a in agents)
    running_tasks = sum(len(a.current_tasks) for a in agents)

    # Overall success rate
    success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0

    # Knowledge graph stats
    kg_stats = kg.get_statistics()

    # System uptime
    uptime = time.time() - _system_start_time

    metrics = SystemMetricsResponse(
        total_agents=len(agents),
        active_agents=active_agents,
        idle_agents=idle_agents,
        busy_agents=busy_agents,
        total_teams=len(registry.teams),
        total_tasks=total_tasks,
        pending_tasks=0,  # Would need queue
        running_tasks=running_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        total_workflows=0,  # Would need tracking
        running_workflows=0,
        knowledge_nodes=kg_stats["total_nodes"],
        knowledge_edges=kg_stats["total_edges"],
        system_uptime=uptime,
        avg_task_duration=None,  # Would need task history
        overall_success_rate=success_rate,
        messages_per_second=0.0,  # Would need tracking
    )

    return APIResponse(success=True, data=metrics)
