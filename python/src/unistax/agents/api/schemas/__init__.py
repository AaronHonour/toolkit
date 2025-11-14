"""API schemas for agent framework."""

from unistax.agents.api.schemas.agents import (
    AgentResponse,
    CreateAgentRequest,
    UpdateAgentRequest,
    AgentListResponse,
    AgentStatsResponse,
)
from unistax.agents.api.schemas.tasks import (
    TaskRequest,
    TaskResponse,
    TaskListResponse,
    TaskStatusUpdate,
)
from unistax.agents.api.schemas.teams import (
    TeamResponse,
    CreateTeamRequest,
    UpdateTeamRequest,
    TeamListResponse,
)
from unistax.agents.api.schemas.workflows import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStepResponse,
    WorkflowStatusResponse,
)
from unistax.agents.api.schemas.knowledge import (
    KnowledgeNodeResponse,
    KnowledgeEdgeResponse,
    AddNodeRequest,
    AddEdgeRequest,
    BestPracticeRequest,
    IssueRequest,
)
from unistax.agents.api.schemas.metrics import (
    AgentMetricsResponse,
    SystemMetricsResponse,
)

__all__ = [
    # Agents
    "AgentResponse",
    "CreateAgentRequest",
    "UpdateAgentRequest",
    "AgentListResponse",
    "AgentStatsResponse",
    # Tasks
    "TaskRequest",
    "TaskResponse",
    "TaskListResponse",
    "TaskStatusUpdate",
    # Teams
    "TeamResponse",
    "CreateTeamRequest",
    "UpdateTeamRequest",
    "TeamListResponse",
    # Workflows
    "WorkflowRequest",
    "WorkflowResponse",
    "WorkflowStepResponse",
    "WorkflowStatusResponse",
    # Knowledge
    "KnowledgeNodeResponse",
    "KnowledgeEdgeResponse",
    "AddNodeRequest",
    "AddEdgeRequest",
    "BestPracticeRequest",
    "IssueRequest",
    # Metrics
    "AgentMetricsResponse",
    "SystemMetricsResponse",
]
