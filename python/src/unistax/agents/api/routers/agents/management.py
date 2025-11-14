"""Agent management endpoints (CRUD)."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from unistax.agents import (
    AgentRegistry,
    DataAnalystAgent,
    DataEngineerAgent,
    DataScientistAgent,
    DataStewardAgent,
)
from unistax.agents.api.dependencies import get_event_bus, get_metrics_manager, get_registry
from unistax.agents.api.schemas import (
    AgentListResponse,
    AgentResponse,
    AgentStatsResponse,
    CreateAgentRequest,
    UpdateAgentRequest,
)
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/agents", tags=["Agent Management"])
logger = get_logger(__name__)


def _agent_to_response(agent) -> AgentResponse:
    """Convert agent to response model.

    Args:
        agent: Agent instance

    Returns:
        AgentResponse
    """
    return AgentResponse(
        agent_id=agent.agent_id,
        persona=agent.persona,
        state=agent.state.value,
        team_id=agent.team_id,
        skills={name: skill.proficiency for name, skill in agent.skills.items()},
        current_tasks=[t.id for t in agent.current_tasks],
        completed_tasks=agent.completed_tasks,
        failed_tasks=agent.failed_tasks,
        messages_sent=agent.messages_sent,
        messages_received=agent.messages_received,
        created_at=datetime.now(),  # Would need to add this to agent
        last_active=datetime.now(),
    )


@router.post(
    "",
    response_model=APIResponse[AgentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create agent",
    description="Create a new agent with specified persona and configuration",
)
async def create_agent(
    request: CreateAgentRequest,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentResponse]:
    """Create a new agent."""
    logger.info(f"Creating agent: {request.agent_id} (persona={request.persona})")

    # Check if agent already exists
    if request.agent_id in registry.agents:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent {request.agent_id} already exists",
        )

    # Create agent based on persona
    event_bus = get_event_bus()
    metrics_manager = get_metrics_manager()

    persona_map = {
        "engineer": DataEngineerAgent,
        "analyst": DataAnalystAgent,
        "scientist": DataScientistAgent,
        "steward": DataStewardAgent,
    }

    agent_class = persona_map.get(request.persona)
    if not agent_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid persona: {request.persona}. Must be one of: {list(persona_map.keys())}",
        )

    # Create agent
    agent = agent_class(
        agent_id=request.agent_id,
        event_bus=event_bus,
        metrics_manager=metrics_manager,
        team_id=request.team_id,
    )

    # Override skills if provided
    if request.skills:
        from unistax.agents import Skill

        agent.skills = {
            name: Skill(name=name, proficiency=prof) for name, prof in request.skills.items()
        }

    # Register agent
    registry.register(agent)

    logger.info(f"Agent {request.agent_id} created successfully")

    return APIResponse(
        success=True,
        data=_agent_to_response(agent),
        message=f"Agent {request.agent_id} created successfully",
    )


@router.get(
    "",
    response_model=APIResponse[AgentListResponse],
    summary="List agents",
    description="Get list of all registered agents with pagination",
)
async def list_agents(
    registry: Annotated[AgentRegistry, Depends(get_registry)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    persona: str | None = Query(None, description="Filter by persona"),
    team_id: str | None = Query(None, description="Filter by team ID"),
    state: str | None = Query(None, description="Filter by state"),
) -> APIResponse[AgentListResponse]:
    """List all registered agents."""
    logger.debug(f"Listing agents: page={page}, page_size={page_size}")

    # Get all agents
    agents = list(registry.agents.values())

    # Apply filters
    if persona:
        agents = [a for a in agents if a.persona == persona]

    if team_id:
        agents = [a for a in agents if a.team_id == team_id]

    if state:
        agents = [a for a in agents if a.state.value == state]

    # Pagination
    total = len(agents)
    start = (page - 1) * page_size
    end = start + page_size
    page_agents = agents[start:end]

    return APIResponse(
        success=True,
        data=AgentListResponse(
            agents=[_agent_to_response(a) for a in page_agents],
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.get(
    "/{agent_id}",
    response_model=APIResponse[AgentResponse],
    summary="Get agent",
    description="Get details of a specific agent by ID",
)
async def get_agent(
    agent_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentResponse]:
    """Get agent by ID."""
    logger.debug(f"Getting agent: {agent_id}")

    agent = registry.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    return APIResponse(success=True, data=_agent_to_response(agent))


@router.patch(
    "/{agent_id}",
    response_model=APIResponse[AgentResponse],
    summary="Update agent",
    description="Update agent configuration",
)
async def update_agent(
    agent_id: str,
    request: UpdateAgentRequest,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentResponse]:
    """Update agent configuration."""
    logger.info(f"Updating agent: {agent_id}")

    agent = registry.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Update team
    if request.team_id is not None:
        agent.team_id = request.team_id

    # Update skills
    if request.skills:
        from unistax.agents import Skill

        agent.skills = {
            name: Skill(name=name, proficiency=prof) for name, prof in request.skills.items()
        }

    logger.info(f"Agent {agent_id} updated successfully")

    return APIResponse(
        success=True,
        data=_agent_to_response(agent),
        message=f"Agent {agent_id} updated successfully",
    )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete agent",
    description="Unregister and delete an agent",
)
async def delete_agent(
    agent_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> None:
    """Delete agent."""
    logger.info(f"Deleting agent: {agent_id}")

    agent = registry.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Unregister agent
    registry.unregister(agent_id)

    logger.info(f"Agent {agent_id} deleted successfully")


@router.get(
    "/{agent_id}/stats",
    response_model=APIResponse[AgentStatsResponse],
    summary="Get agent statistics",
    description="Get detailed statistics for a specific agent",
)
async def get_agent_stats(
    agent_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentStatsResponse]:
    """Get agent statistics."""
    logger.debug(f"Getting stats for agent: {agent_id}")

    agent = registry.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Calculate stats
    total_tasks = agent.completed_tasks + agent.failed_tasks
    success_rate = agent.completed_tasks / total_tasks if total_tasks > 0 else 0.0

    stats = AgentStatsResponse(
        agent_id=agent.agent_id,
        total_tasks=total_tasks,
        completed_tasks=agent.completed_tasks,
        failed_tasks=agent.failed_tasks,
        success_rate=success_rate,
        avg_task_duration=None,  # Would need task history
        messages_sent=agent.messages_sent,
        messages_received=agent.messages_received,
        uptime_seconds=0.0,  # Would need to track
        last_active=datetime.now(),
    )

    return APIResponse(success=True, data=stats)
