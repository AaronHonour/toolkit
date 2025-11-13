"""Agent Swarm Module.

Provides autonomous agents for data platform operations with:
- Hierarchical team structures
- Inter-agent communication via EventBus
- Task execution with skill-based matching
- Metrics and audit logging
- Proactive and reactive behaviors

Integrates with unistax infrastructure:
- unistax.logging for structured logging
- unistax.events for inter-agent messaging
- unistax.queue for task distribution
- unistax.metrics for performance tracking
- unistax.audit for action auditing
- unistax.security for JWT authentication
- unistax.ratelimit for message rate limiting
- unistax.secrets for secure credential management
"""

from unistax.agents.base import (
    Agent,
    AgentMessageEvent,
    AgentState,
    AgentStateChangeEvent,
    CollaborationRequestEvent,
    Message,
    Skill,
    Task,
    TaskAssignedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    TaskStatus,
    TeamRole,
)
from unistax.agents.personas.data_analyst import DataAnalystAgent
from unistax.agents.personas.data_engineer import DataEngineerAgent
from unistax.agents.registry import AgentRegistry
from unistax.agents.task_integration import AgentTaskQueue, AgentTaskScheduler
from unistax.agents.team import Team, TeamHierarchy, TeamType

__all__ = [
    # Base agent classes
    "Agent",
    "AgentState",
    "Skill",
    "Task",
    "TaskStatus",
    "Message",
    "TeamRole",
    # Events
    "AgentMessageEvent",
    "TaskAssignedEvent",
    "TaskCompletedEvent",
    "TaskFailedEvent",
    "AgentStateChangeEvent",
    "CollaborationRequestEvent",
    # Team classes
    "Team",
    "TeamType",
    "TeamHierarchy",
    # Registry
    "AgentRegistry",
    # Task Integration
    "AgentTaskQueue",
    "AgentTaskScheduler",
    # Personas
    "DataEngineerAgent",
    "DataAnalystAgent",
]
