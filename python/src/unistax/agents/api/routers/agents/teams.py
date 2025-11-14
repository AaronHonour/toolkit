"""Team management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from unistax.agents import AgentRegistry, Team, TeamType
from unistax.agents.api.dependencies import get_registry
from unistax.agents.api.schemas import (
    CreateTeamRequest,
    TeamListResponse,
    TeamResponse,
    UpdateTeamRequest,
)
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/teams", tags=["Team Management"])
logger = get_logger(__name__)


def _team_to_response(team: Team, registry: AgentRegistry) -> TeamResponse:
    """Convert team to response model.

    Args:
        team: Team instance
        registry: Agent registry

    Returns:
        TeamResponse
    """
    # Count members
    members = [a for a in registry.agents.values() if a.team_id == team.id]

    # Find leader
    leader_id = None
    for agent in members:
        if hasattr(agent, "role") and agent.role == "leader":
            leader_id = agent.agent_id
            break

    # Get sub-teams
    hierarchy = registry.team_hierarchy
    sub_teams = []
    if hierarchy:
        for team_id, parent_id in hierarchy.parent_teams.items():
            if parent_id == team.id:
                sub_teams.append(team_id)

    return TeamResponse(
        team_id=team.id,
        name=team.name,
        team_type=team.type.value,
        parent_team_id=None,  # Would need hierarchy lookup
        description=None,  # Team class doesn't have description
        member_count=len(members),
        leader_id=leader_id,
        sub_teams=sub_teams,
    )


@router.post(
    "",
    response_model=APIResponse[TeamResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create team",
    description="Create a new team",
)
async def create_team(
    request: CreateTeamRequest,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[TeamResponse]:
    """Create a new team."""
    logger.info(f"Creating team: {request.name} (type={request.team_type})")

    # Parse team type
    try:
        team_type = TeamType[request.team_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid team type: {request.team_type}",
        )

    # Create team
    team = registry.create_team(
        name=request.name,
        team_type=team_type,
    )

    # Set parent if provided
    if request.parent_team_id:
        hierarchy = registry.team_hierarchy
        if hierarchy:
            hierarchy.add_team(team, parent_id=request.parent_team_id)

    logger.info(f"Team {team.id} created successfully")

    return APIResponse(
        success=True,
        data=_team_to_response(team, registry),
        message=f"Team {team.id} created successfully",
    )


@router.get(
    "",
    response_model=APIResponse[TeamListResponse],
    summary="List teams",
    description="Get list of all teams",
)
async def list_teams(
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[TeamListResponse]:
    """List all teams."""
    logger.debug("Listing teams")

    teams = list(registry.teams.values())

    return APIResponse(
        success=True,
        data=TeamListResponse(
            teams=[_team_to_response(t, registry) for t in teams],
            total=len(teams),
        ),
    )


@router.get(
    "/{team_id}",
    response_model=APIResponse[TeamResponse],
    summary="Get team",
    description="Get details of a specific team by ID",
)
async def get_team(
    team_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[TeamResponse]:
    """Get team by ID."""
    logger.debug(f"Getting team: {team_id}")

    team = registry.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )

    return APIResponse(success=True, data=_team_to_response(team, registry))


@router.patch(
    "/{team_id}",
    response_model=APIResponse[TeamResponse],
    summary="Update team",
    description="Update team details",
)
async def update_team(
    team_id: str,
    request: UpdateTeamRequest,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[TeamResponse]:
    """Update team."""
    logger.info(f"Updating team: {team_id}")

    team = registry.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )

    # Update name
    if request.name is not None:
        team.name = request.name

    # Update parent
    if request.parent_team_id is not None:
        hierarchy = registry.team_hierarchy
        if hierarchy:
            hierarchy.add_team(team, parent_id=request.parent_team_id)

    logger.info(f"Team {team_id} updated successfully")

    return APIResponse(
        success=True,
        data=_team_to_response(team, registry),
        message=f"Team {team_id} updated successfully",
    )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team",
    description="Delete a team",
)
async def delete_team(
    team_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> None:
    """Delete team."""
    logger.info(f"Deleting team: {team_id}")

    team = registry.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )

    # Check if team has members
    members = [a for a in registry.agents.values() if a.team_id == team_id]
    if members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete team with {len(members)} members. Remove members first.",
        )

    # Remove from registry
    del registry.teams[team_id]

    logger.info(f"Team {team_id} deleted successfully")


@router.get(
    "/{team_id}/members",
    response_model=APIResponse[list[str]],
    summary="Get team members",
    description="Get list of agent IDs in a team",
)
async def get_team_members(
    team_id: str,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[list[str]]:
    """Get team members."""
    logger.debug(f"Getting members for team: {team_id}")

    team = registry.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )

    # Get member IDs
    member_ids = [a.agent_id for a in registry.agents.values() if a.team_id == team_id]

    return APIResponse(success=True, data=member_ids)
