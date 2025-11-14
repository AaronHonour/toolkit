"""Agent discovery and search endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from unistax.agents import AgentRegistry, Task
from unistax.agents.api.dependencies import get_registry
from unistax.agents.api.schemas import AgentListResponse
from unistax.agents.api.routers.agents.management import _agent_to_response
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/discovery", tags=["Agent Discovery"])
logger = get_logger(__name__)


@router.get(
    "/by-persona/{persona}",
    response_model=APIResponse[AgentListResponse],
    summary="Find agents by persona",
    description="Discover agents with a specific persona",
)
async def find_by_persona(
    persona: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentListResponse]:
    """Find agents by persona."""
    logger.debug(f"Finding agents by persona: {persona}")

    agents = registry.find_by_persona(persona)

    return APIResponse(
        success=True,
        data=AgentListResponse(
            agents=[_agent_to_response(a) for a in agents],
            total=len(agents),
            page=1,
            page_size=len(agents),
        ),
    )


@router.get(
    "/by-skill",
    response_model=APIResponse[AgentListResponse],
    summary="Find agents by skill",
    description="Discover agents with a specific skill and minimum proficiency",
)
async def find_by_skill(
    skill: str = Query(..., description="Skill name"),
    min_proficiency: float = Query(0.0, ge=0.0, le=1.0, description="Minimum proficiency"),
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentListResponse]:
    """Find agents by skill."""
    logger.debug(f"Finding agents by skill: {skill} (min={min_proficiency})")

    agents = registry.find_by_skill(skill, min_proficiency=min_proficiency)

    return APIResponse(
        success=True,
        data=AgentListResponse(
            agents=[_agent_to_response(a) for a in agents],
            total=len(agents),
            page=1,
            page_size=len(agents),
        ),
    )


@router.get(
    "/by-team/{team_id}",
    response_model=APIResponse[AgentListResponse],
    summary="Find agents by team",
    description="Discover agents belonging to a specific team",
)
async def find_by_team(
    team_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentListResponse]:
    """Find agents by team."""
    logger.debug(f"Finding agents by team: {team_id}")

    agents = registry.find_by_team(team_id)

    return APIResponse(
        success=True,
        data=AgentListResponse(
            agents=[_agent_to_response(a) for a in agents],
            total=len(agents),
            page=1,
            page_size=len(agents),
        ),
    )


@router.post(
    "/for-task",
    response_model=APIResponse[AgentListResponse],
    summary="Find agents for task",
    description="Find suitable agents for a given task based on required skills",
)
async def find_for_task(
    task_type: str = Query(..., description="Task type"),
    required_skills: dict[str, float] | None = Query(None, description="Required skills"),
    priority: int = Query(5, ge=1, le=10, description="Task priority"),
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[AgentListResponse]:
    """Find agents suitable for a task."""
    logger.debug(f"Finding agents for task: type={task_type}")

    # Create task
    task = Task(
        id="discovery",
        type=task_type,
        priority=priority,
        required_skills=required_skills or {},
    )

    # Find suitable agents
    agents_with_confidence = registry.find_agents_for_task(task)

    # Sort by confidence (highest first)
    agents_with_confidence.sort(key=lambda x: x[1], reverse=True)

    agents = [a for a, conf in agents_with_confidence]

    return APIResponse(
        success=True,
        data=AgentListResponse(
            agents=[_agent_to_response(a) for a in agents],
            total=len(agents),
            page=1,
            page_size=len(agents),
        ),
        meta={
            "confidence_scores": {
                agents[i].agent_id: agents_with_confidence[i][1]
                for i in range(len(agents))
            }
        },
    )


@router.get(
    "/statistics",
    response_model=APIResponse[dict],
    summary="Get discovery statistics",
    description="Get statistics about registered agents, personas, skills, and teams",
)
async def get_statistics(
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[dict]:
    """Get registry statistics."""
    logger.debug("Getting discovery statistics")

    stats = registry.get_statistics()

    return APIResponse(success=True, data=stats)
