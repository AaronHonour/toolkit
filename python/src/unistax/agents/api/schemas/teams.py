"""Team API schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class CreateTeamRequest(BaseModel):
    """Request to create a team."""

    name: str = Field(..., description="Team name")
    team_type: str = Field(
        ..., description="Team type (division, functional, cross_functional, task_force)"
    )
    parent_team_id: Optional[str] = Field(None, description="Parent team ID for hierarchy")
    description: Optional[str] = Field(None, description="Team description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Data Platform",
                "team_type": "division",
                "description": "Enterprise data platform team",
            }
        }


class UpdateTeamRequest(BaseModel):
    """Request to update team."""

    name: Optional[str] = Field(None, description="New team name")
    description: Optional[str] = Field(None, description="New description")
    parent_team_id: Optional[str] = Field(None, description="New parent team")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Data Platform & Analytics",
                "description": "Expanded platform and analytics team",
            }
        }


class TeamResponse(BaseModel):
    """Team response."""

    team_id: str
    name: str
    team_type: str
    parent_team_id: Optional[str]
    description: Optional[str]
    member_count: int
    leader_id: Optional[str]
    sub_teams: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "data_platform",
                "name": "Data Platform",
                "team_type": "division",
                "parent_team_id": None,
                "description": "Enterprise data platform team",
                "member_count": 5,
                "leader_id": "engineer_001",
                "sub_teams": ["etl_team", "analytics_team"],
            }
        }


class TeamListResponse(BaseModel):
    """List of teams response."""

    teams: list[TeamResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "teams": [
                    {
                        "team_id": "data_platform",
                        "name": "Data Platform",
                        "team_type": "division",
                        "parent_team_id": None,
                        "member_count": 5,
                        "leader_id": "engineer_001",
                        "sub_teams": [],
                    }
                ],
                "total": 1,
            }
        }
