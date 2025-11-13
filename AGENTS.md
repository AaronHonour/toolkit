# Agent Swarm Framework

Autonomous agent system for building intelligent data teams that collaborate to manage data platform operations.

## Overview

The Agent Swarm Framework provides a complete system for creating, managing, and orchestrating autonomous agents that work together to handle data engineering, analysis, and platform operations. Agents have specialized skills, collaborate through an event-driven architecture, and organize into hierarchical teams.

## Key Features

- **🤖 Autonomous Agents** - Self-directed agents with cognitive cycle (Sense → Think → Act)
- **👥 Hierarchical Teams** - Multi-level organizational structures with leaders and members
- **🎯 Skill-Based Matching** - Automatic task assignment based on agent capabilities
- **📡 Event-Driven Communication** - Inter-agent messaging via EventBus
- **📊 Performance Tracking** - Built-in metrics and monitoring
- **🔄 Proactive & Reactive** - Agents can both respond to tasks and take initiative
- **🧩 Multiple Personas** - Pre-configured agent types for different roles

## Architecture

### Agent Cognitive Cycle

Each agent operates on a continuous cognitive cycle:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  SENSE   │────▶│  THINK   │────▶│   ACT    │
└──────────┘     └──────────┘     └──────────┘
      ▲                                  │
      └──────────────────────────────────┘
```

1. **Sense**: Process incoming messages and observe environment
2. **Think**: Decide what action to take based on state and goals
3. **Act**: Execute the decided action (task, message, etc.)

### Component Hierarchy

```
AgentRegistry
├── EventBus (shared communication)
├── MetricsManager (performance tracking)
└── TeamHierarchy
    ├── Team (Division)
    │   ├── Team (Functional)
    │   │   ├── Agent (Leader)
    │   │   ├── Agent (Member)
    │   │   └── Agent (Specialist)
    │   └── Team (Cross-Functional)
    └── Team (Task Force)
```

## Quick Start

### Basic Setup

```python
from unistax.agents import (
    AgentRegistry,
    DataEngineerAgent,
    DataAnalystAgent,
    Skill,
    Task,
    TeamType,
)

# 1. Create registry with shared infrastructure
registry = AgentRegistry()

# 2. Create a team
data_team = registry.create_team(
    name="Data Platform",
    team_type=TeamType.DIVISION,
)

# 3. Create agents
engineer = DataEngineerAgent(
    agent_id="eng_001",
    event_bus=registry.event_bus,
    metrics_manager=registry.metrics_manager,
    team_id=data_team.id,
)

analyst = DataAnalystAgent(
    agent_id="analyst_001",
    event_bus=registry.event_bus,
    metrics_manager=registry.metrics_manager,
    team_id=data_team.id,
)

# 4. Register agents
registry.register(engineer)
registry.register(analyst)

# 5. Create and assign tasks
task = Task(
    type="build_pipeline",
    description="Create customer analytics pipeline",
    priority=8,
    required_skills={"sql": 0.7, "etl": 0.8},
    context={
        "name": "customer_pipeline",
        "source": {"type": "postgres", "table": "raw_customers"},
        "target": {"type": "snowflake", "table": "dim_customers"},
    },
)

# Check if agent can do task
can_do, confidence = engineer.can_do(task)
if can_do:
    await engineer.accept_task(task)
    result = await engineer.execute_task(task)
```

### Running the Demo

```bash
cd python
PYTHONPATH=src:$PYTHONPATH python examples/agent_collaboration_demo.py
```

## Agent Personas

### Data Engineer

**Focus**: Infrastructure, pipelines, data quality

**Skills** (default):
- SQL: 0.90
- Python: 0.85
- ETL: 0.90
- Data Quality: 0.85
- Schema Design: 0.80
- Performance Tuning: 0.75
- Airflow: 0.80
- Spark: 0.70

**Supported Tasks**:
- `build_pipeline` - Create ETL pipelines
- `optimize_query` - Optimize database queries
- `quality_check` - Run data quality validations
- `schema_migration` - Perform schema changes
- `monitor_pipeline` - Monitor pipeline health
- `fix_data_issue` - Fix data quality issues

**Example**:
```python
task = Task(
    type="build_pipeline",
    context={
        "name": "orders_pipeline",
        "source": {"type": "kafka", "topic": "orders"},
        "target": {"type": "redshift", "table": "fact_orders"},
        "transformations": ["dedupe", "validate", "enrich"],
    },
)

result = await engineer.execute_task(task)
# Returns: {"status": "success", "pipeline_name": "orders_pipeline", ...}
```

### Data Analyst

**Focus**: Analysis, insights, reporting

**Skills** (default):
- SQL: 0.90
- Python: 0.75
- Statistics: 0.85
- Data Analysis: 0.90
- Visualization: 0.80
- Business Intelligence: 0.85
- Excel: 0.80
- Reporting: 0.85

**Supported Tasks**:
- `analyze_data` - Perform ad-hoc analysis
- `create_dashboard` - Build visualization dashboards
- `generate_report` - Create business reports
- `execute_query` - Run SQL queries
- `identify_trends` - Analyze patterns and trends
- `calculate_metrics` - Compute business metrics
- `provide_insights` - Generate recommendations

**Example**:
```python
task = Task(
    type="analyze_data",
    context={
        "dataset": "customer_churn",
        "analysis_type": "predictive",
        "metrics": ["churn_rate", "customer_lifetime_value"],
    },
)

result = await analyst.execute_task(task)
# Returns: {"status": "success", "key_findings": [...], ...}
```

## Team Management

### Creating Teams

```python
# Create division (top-level)
platform = registry.create_team(
    name="Data Platform",
    team_type=TeamType.DIVISION,
)

# Create functional teams under division
engineering = registry.create_team(
    name="Data Engineering",
    team_type=TeamType.FUNCTIONAL,
    parent_id=platform.id,
    leader_id="eng_lead_001",
)

analytics = registry.create_team(
    name="Data Analytics",
    team_type=TeamType.FUNCTIONAL,
    parent_id=platform.id,
    leader_id="analyst_lead_001",
)

# Create cross-functional team
product_team = registry.create_team(
    name="Product Analytics",
    team_type=TeamType.CROSS_FUNCTIONAL,
    parent_id=platform.id,
)
```

### Team Types

- **FUNCTIONAL**: Agents with similar skills (e.g., all engineers)
- **CROSS_FUNCTIONAL**: Mixed roles working on a project
- **TASK_FORCE**: Temporary team for specific goal
- **DIVISION**: High-level organizational unit

### Team Operations

```python
# Get team
team = registry.get_team(team_id)

# Get all team members (including leader)
members = team.all_members(include_leader=True)

# Get organizational path
path = registry.team_hierarchy.get_organizational_path(team_id)
print(" > ".join(t.name for t in path))
# Output: Data Platform > Data Engineering > Backend Team

# Get team metrics
metrics = registry.team_hierarchy.get_metrics(team_id, recursive=True)
```

## Agent Discovery

### Find by Persona

```python
# Find all data engineers
engineers = registry.find_by_persona("data_engineer")

# Find all data analysts
analysts = registry.find_by_persona("data_analyst")
```

### Find by Skill

```python
# Find agents with SQL >= 0.8
sql_experts = registry.find_by_skill("sql", min_proficiency=0.8)

# Find agents with multiple skills
ml_agents = registry.find_by_skill("machine_learning", min_proficiency=0.7)
```

### Find by Team

```python
# Find all agents in a team
team_agents = registry.find_by_team(team_id)
```

### Find Available Agents

```python
# Find any available agent
available = registry.find_available()

# Find available engineers
available_engineers = registry.find_available(persona="data_engineer")

# Find agents with < 2 tasks
lightly_loaded = registry.find_available(max_tasks=2)
```

## Inter-Agent Communication

### Sending Messages

```python
# Send request to specific agent
await analyst.send_message(
    to_agent="eng_001",
    msg_type="request",
    content={
        "action": "quality_check",
        "table": "customer_analytics",
        "urgency": "high",
    },
    requires_response=True,
)

# Broadcast to team
await engineer.broadcast_to_team(
    msg_type="notification",
    content={
        "event": "pipeline_deployed",
        "pipeline": "customer_pipeline",
    },
)

# Broadcast to multiple agents
await analyst.send_message(
    to_agent=["eng_001", "eng_002", "analyst_002"],
    msg_type="broadcast",
    content={"announcement": "New dashboard available"},
)
```

### Message Types

- `request` - Request action from another agent
- `response` - Response to a previous request
- `broadcast` - Announce to multiple agents
- `notification` - Inform of an event
- `task_assignment` - Assign a task
- `help_request` - Request assistance
- `peer_review` - Request code/work review

### Event Subscriptions

Agents automatically subscribe to relevant events:

```python
# These events are automatically handled:
- AgentMessageEvent: Messages sent via EventBus
- TaskAssignedEvent: Task assignments
- TaskCompletedEvent: Task completions
- TaskFailedEvent: Task failures
- AgentStateChangeEvent: State transitions
- CollaborationRequestEvent: Collaboration requests
```

## Task Management

### Creating Tasks

```python
task = Task(
    type="analyze_data",
    description="Analyze customer churn patterns",
    priority=7,  # 1-10, higher = more urgent
    required_skills={
        "sql": 0.7,
        "statistics": 0.8,
        "data_analysis": 0.85,
    },
    context={
        "dataset": "customer_events",
        "time_period": "90d",
        "target_metric": "churn_rate",
    },
    dependencies=["task_123"],  # Must complete first
    deadline=datetime.now() + timedelta(hours=4),
)
```

### Task Assignment

```python
# Check if agent can do task
can_do, confidence = agent.can_do(task)
print(f"Can do: {can_do}, Confidence: {confidence:.2%}")

# Accept task
if can_do:
    success = await agent.accept_task(task)

    # Task is now in agent's queue
    assert task in agent.current_tasks
    assert task.status == TaskStatus.ASSIGNED
```

### Task Execution

```python
# Execute task (happens in agent's run loop)
result = await agent.execute_task(task)

# Task moves to history
assert task in agent.task_history
assert task.status == TaskStatus.COMPLETED
assert task.result == result
```

### Task Status Lifecycle

```
PENDING → ASSIGNED → IN_PROGRESS → WAITING_REVIEW → COMPLETED
                                   ↓
                                 FAILED
                                   ↓
                               CANCELLED
```

## Metrics and Monitoring

### Agent Metrics

```python
metrics = agent.get_metrics()

# Returns:
{
    "tasks_completed": 15,
    "tasks_failed": 2,
    "tasks_helped_with": 5,
    "messages_sent": 42,
    "messages_received": 38,
    "collaborations": 8,
    "uptime_seconds": 3600.0,
    "success_rate": 0.88,
    "current_tasks": 2,
    "state": "working",
    "reputation": 1.0,
}
```

### Persona-Specific Metrics

```python
# Data Engineer
eng_stats = engineer.get_engineer_stats()
# Additional metrics:
# - pipelines_maintained
# - tables_monitored
# - quality_checks_run

# Data Analyst
analyst_stats = analyst.get_analyst_stats()
# Additional metrics:
# - dashboards_created
# - reports_generated
# - queries_executed
# - insights_provided
```

### Registry Statistics

```python
stats = registry.get_registry_stats()

# Returns:
{
    "total_agents": 5,
    "active_agents": 4,
    "total_teams": 3,
    "personas": ["data_engineer", "data_analyst"],
    "total_current_tasks": 8,
    "avg_tasks_per_agent": 1.6,
}
```

## Advanced Usage

### Custom Agent Personas

```python
from unistax.agents.base import Agent, Skill, Task

class DataScientistAgent(Agent):
    """Custom Data Scientist persona."""

    def __init__(self, agent_id, **kwargs):
        default_skills = [
            Skill("python", 0.95, "programming"),
            Skill("machine_learning", 0.90, "ml"),
            Skill("statistics", 0.90, "analytics"),
            Skill("deep_learning", 0.85, "ml"),
        ]

        super().__init__(
            agent_id=agent_id,
            persona="data_scientist",
            skills=kwargs.get("skills", default_skills),
            **kwargs,
        )

    async def decide(self):
        """Decision logic."""
        if self.current_tasks:
            return f"execute_task:{self.current_tasks[0].id}"
        return None

    async def execute_task(self, task: Task):
        """Task execution."""
        if task.type == "train_model":
            return await self._train_model(task.context)
        # ... handle other task types
```

### Custom Skills

```python
# Define specialized skills
skills = [
    Skill("python", 0.95, "programming"),
    Skill("tensorflow", 0.85, "ml"),
    Skill("pytorch", 0.80, "ml"),
    Skill("mlflow", 0.90, "ml_ops"),
    Skill("docker", 0.85, "devops"),
]

agent = DataScientistAgent(
    agent_id="ds_001",
    skills=skills,
    event_bus=registry.event_bus,
)
```

### Proactive Behaviors

```python
class ProactiveEngineer(DataEngineerAgent):
    """Engineer that proactively monitors systems."""

    async def decide(self):
        """Enhanced decision logic with proactive monitoring."""
        # Priority 1: Assigned tasks
        if self.current_tasks:
            return f"execute_task:{self.current_tasks[0].id}"

        # Priority 2: Proactive monitoring (when idle)
        if self.state == AgentState.IDLE:
            if self.monitored_tables:
                return "proactive_monitor"

        return None
```

## Integration with Unistax

The agent framework integrates seamlessly with existing unistax infrastructure:

### Logging

```python
from unistax.logging import get_logger

logger = get_logger(__name__)  # Structured logging
```

### Events

```python
from unistax.events import EventBus

event_bus = EventBus()  # Shared across all agents
```

### Metrics

```python
from unistax.metrics import MetricsManager

metrics = MetricsManager()  # Track agent performance
```

### Security (TODO)

```python
# Future integration:
# - JWT authentication for agent-to-agent communication
# - Rate limiting on message sending
# - Secrets management for database credentials
```

## Best Practices

### 1. Use Shared EventBus

Always create a single EventBus and share it across all agents:

```python
# Good
event_bus = EventBus()
agent1 = DataEngineerAgent("a1", event_bus=event_bus)
agent2 = DataAnalystAgent("a2", event_bus=event_bus)

# Bad - agents can't communicate
agent1 = DataEngineerAgent("a1")
agent2 = DataAnalystAgent("a2")
```

### 2. Register Agents

Always register agents with the registry for discovery:

```python
registry = AgentRegistry()
agent = DataEngineerAgent("eng_001", event_bus=registry.event_bus)
registry.register(agent)  # Essential for discovery
```

### 3. Use Skill-Based Assignment

Let the framework match tasks to agents:

```python
# Good - automatic matching
task = Task(
    type="optimize_query",
    required_skills={"sql": 0.8, "performance_tuning": 0.7},
)

for agent in registry.find_available():
    can_do, confidence = agent.can_do(task)
    if can_do and confidence > 0.85:
        await agent.accept_task(task)
        break
```

### 4. Monitor Metrics

Track agent performance:

```python
import asyncio

async def monitor_agents():
    while True:
        for agent in registry.agents.values():
            metrics = agent.get_metrics()
            if metrics["success_rate"] < 0.8:
                logger.warning(f"Agent {agent.agent_id} has low success rate")

        await asyncio.sleep(60)
```

### 5. Handle Failures Gracefully

```python
try:
    result = await agent.execute_task(task)
except Exception as e:
    logger.error(f"Task {task.id} failed: {e}")
    # Task automatically marked as FAILED
    # Metrics updated
    # Failure event published
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/agents/ -v
```

Test coverage includes:
- ✅ Agent base class and cognitive cycle
- ✅ Skills and task matching
- ✅ Team hierarchy and management
- ✅ Agent registry and discovery
- ✅ Data Engineer persona
- ✅ Data Analyst persona
- ✅ Inter-agent messaging
- ✅ Event system integration

## Roadmap

### Phase 1: Core Framework (Completed ✅)
- [x] Base agent class with cognitive cycle
- [x] Skills and task management
- [x] Hierarchical teams
- [x] Agent registry and discovery
- [x] Data Engineer persona
- [x] Data Analyst persona
- [x] EventBus integration
- [x] Metrics tracking
- [x] Comprehensive tests

### Phase 2: Advanced Features (In Progress 🚧)
- [ ] Task queue integration (unistax.tasks + Celery)
- [ ] Security integration (JWT, rate limiting, secrets)
- [ ] Data Scientist persona
- [ ] Data Steward persona
- [ ] Orchestrator for multi-agent workflows

### Phase 3: Intelligence (Planned 📋)
- [ ] ML-based decision making (Reinforcement Learning)
- [ ] Knowledge graph integration
- [ ] Blackboard collaboration pattern
- [ ] Swarm intelligence algorithms
- [ ] HTN (Hierarchical Task Network) planning

### Phase 4: Scale (Future 🔮)
- [ ] Redis-based distributed messaging
- [ ] Agent persistence and recovery
- [ ] Load balancing across agents
- [ ] Multi-datacenter agent deployment

## Examples

See `python/examples/` for complete working examples:

- `agent_collaboration_demo.py` - Basic agent collaboration
- More examples coming soon!

## Contributing

When adding new agent personas:

1. Extend the `Agent` base class
2. Implement `decide()` and `execute_task()`
3. Define default skills
4. Add persona-specific methods
5. Write comprehensive tests
6. Update this documentation

## License

Part of the Unistax project.
