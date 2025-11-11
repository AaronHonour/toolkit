# Example 20: Service Dependency Graph Builder

A comprehensive service dependency analysis tool that automatically discovers, visualizes, and analyzes service dependencies.

## Overview

This example demonstrates the **Service Dependency Graph Builder** - a powerful toolkit for understanding microservice architectures through:

- **Automatic Discovery**: Detect dependencies from APIs, databases, message queues, and configuration
- **Graph Analysis**: Identify circular dependencies, calculate blast radius, find bottlenecks
- **Impact Analysis**: Assess the impact of failures, deployments, and changes
- **Visualization**: Export graphs to D3.js, Cytoscape, Mermaid, and Graphviz formats

## Features

### 1. Dependency Discovery
- **API Call Detection**: Parse traces, logs, and code for HTTP dependencies
- **Database Connections**: Analyze connection strings and configurations
- **Message Queues**: Map publishers/subscribers to topics
- **Configuration-Based**: Extract dependencies from config files and env vars

### 2. Graph Algorithms
- **Circular Dependency Detection**: Tarjan's strongly connected components algorithm
- **Blast Radius Calculation**: BFS-based impact analysis for failures
- **Service Criticality**: PageRank-variant scoring for importance
- **Bottleneck Detection**: Betweenness centrality for identifying choke points
- **Deployment Ordering**: Topological sort for safe deployment sequences

### 3. Analysis & Insights
- Comprehensive dependency analysis reports
- Impact assessment for failures, deployments, and changes
- Risk level evaluation (LOW, MEDIUM, HIGH, CRITICAL)
- Actionable recommendations and mitigation strategies

### 4. Visualization
- **D3.js Force-Directed Graph**: Interactive web visualization
- **Cytoscape.js**: Advanced graph exploration
- **Mermaid Diagrams**: Documentation-ready diagrams
- **Graphviz DOT**: Publication-quality graphics

## Architecture

```
Service Dependency Graph Builder
├── Domain Layer
│   ├── ServiceNode: Service entity
│   ├── DependencyEdge: Relationship between services
│   └── ServiceDependencyGraph: Aggregate root
├── Application Layer
│   ├── Commands: RegisterService, RecordDependency, DiscoverDependencies
│   ├── Queries: GetGraph, AnalyzeCircular, CalculateBlastRadius
│   └── Services: GraphService, AnalysisService
├── Infrastructure Layer
│   └── Repository: In-memory graph storage (extensible to Neo4j)
└── Presentation Layer
    └── REST API: FastAPI endpoints for all operations
```

## API Endpoints

### Service Management
```
POST   /api/v1/services              # Register a service
GET    /api/v1/services              # List all services
GET    /api/v1/services/{name}       # Get service details
DELETE /api/v1/services/{name}       # Remove service
```

### Dependency Management
```
POST   /api/v1/dependencies          # Record dependency
GET    /api/v1/dependencies          # List all dependencies
GET    /api/v1/dependencies/{source}/{target}  # Get specific dependency
```

### Discovery
```
POST   /api/v1/discovery/scan        # Trigger discovery scan
GET    /api/v1/discovery/results     # Get discovery results
```

### Analysis
```
GET    /api/v1/analysis/graph        # Get complete graph
GET    /api/v1/analysis/circular     # Detect circular dependencies
GET    /api/v1/analysis/criticality  # Calculate service criticality
GET    /api/v1/analysis/blast-radius/{service}  # Calculate blast radius
GET    /api/v1/analysis/bottlenecks  # Identify bottlenecks
GET    /api/v1/analysis/deployment-order  # Get deployment order
POST   /api/v1/analysis/impact       # Analyze change impact
```

### Visualization
```
GET    /api/v1/visualize?format=d3   # Export for D3.js
GET    /api/v1/visualize?format=cytoscape  # Export for Cytoscape
GET    /api/v1/visualize?format=mermaid    # Export as Mermaid
GET    /api/v1/visualize?format=graphviz   # Export as Graphviz DOT
```

## Usage Example

### 1. Register Services
```python
import httpx

# Register services
services = [
    {"name": "api-gateway", "type": "gateway", "endpoints": ["/api"]},
    {"name": "user-service", "type": "api", "endpoints": ["/users"]},
    {"name": "order-service", "type": "api", "endpoints": ["/orders"]},
    {"name": "postgres-users", "type": "database"},
]

for service in services:
    httpx.post("http://localhost:8000/api/v1/services", json=service)
```

### 2. Record Dependencies
```python
dependencies = [
    {"source": "api-gateway", "target": "user-service", "type": "api_call"},
    {"source": "api-gateway", "target": "order-service", "type": "api_call"},
    {"source": "user-service", "target": "postgres-users", "type": "database"},
    {"source": "order-service", "target": "user-service", "type": "api_call"},
]

for dep in dependencies:
    httpx.post("http://localhost:8000/api/v1/dependencies", json=dep)
```

### 3. Analyze the Graph
```python
# Get complete analysis
analysis = httpx.get("http://localhost:8000/api/v1/analysis/graph").json()

# Check for circular dependencies
circular = httpx.get("http://localhost:8000/api/v1/analysis/circular").json()

# Calculate blast radius for user-service failure
blast_radius = httpx.get(
    "http://localhost:8000/api/v1/analysis/blast-radius/user-service"
).json()

# Get critical services
criticality = httpx.get("http://localhost:8000/api/v1/analysis/criticality").json()
```

### 4. Analyze Impact
```python
# Analyze impact of deploying user-service with breaking changes
impact = httpx.post(
    "http://localhost:8000/api/v1/analysis/impact",
    json={
        "service_name": "user-service",
        "change_type": "breaking_change",
        "expected_downtime_minutes": 5
    }
).json()

print(f"Risk Level: {impact['risk_level']}")
print(f"Affected Services: {impact['total_affected']}")
print(f"Recommendations: {impact['recommendations']}")
```

### 5. Visualize
```python
# Get graph in D3.js format for frontend visualization
d3_data = httpx.get(
    "http://localhost:8000/api/v1/visualize?format=d3"
).json()

# Get Mermaid diagram for documentation
mermaid = httpx.get(
    "http://localhost:8000/api/v1/visualize?format=mermaid"
).text()
print(mermaid)
```

## Performance

- **Graph Construction**: O(V + E) where V = services, E = dependencies
- **Circular Detection**: O(V + E) using Tarjan's algorithm
- **Blast Radius**: O(V + E) using BFS
- **PageRank**: O(k * E) where k = iterations (typically < 100)
- **Supports**: 1000+ services, 10000+ dependencies

## Running the Example

```bash
# Install dependencies
cd examples/backends/20_service_dependency_graph
pip install -r requirements.txt

# Run the server
python -m uvicorn src.main:app --reload

# Access API docs
open http://localhost:8000/docs
```

## Use Cases

1. **Architecture Understanding**: Visualize complex microservice relationships
2. **Impact Analysis**: Assess change impact before deployments
3. **Incident Response**: Calculate blast radius during outages
4. **Technical Debt**: Identify and break circular dependencies
5. **Capacity Planning**: Find bottlenecks and critical services
6. **Deployment Planning**: Generate safe deployment orders

## Technologies

- **FastAPI**: High-performance async REST API
- **Unistax Graph**: Custom graph data structures
- **Unistax Algorithms**: Tarjan, PageRank, BFS, betweenness centrality
- **Unistax Discovery**: Automatic dependency detection
- **Unistax Analysis**: Impact and risk assessment

## Next Steps

- Add Neo4j persistence for large-scale graphs
- Implement real-time WebSocket updates
- Add machine learning for anomaly detection
- Integrate with distributed tracing (Jaeger, Zipkin)
- Build frontend visualization dashboard
