"""Graph algorithms for dependency analysis.

Implements efficient algorithms for:
- Circular dependency detection (Tarjan's SCC)
- Blast radius calculation (BFS)
- Service criticality (PageRank variant)
- Bottleneck detection (Betweenness centrality)
- Dependency ordering (Topological sort)
"""

from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class CircularDependency:
    """Represents a circular dependency cycle."""

    services: list[str]
    cycle_length: int

    @property
    def cycle_path(self) -> str:
        """Get a human-readable cycle path."""
        return " → ".join(self.services + [self.services[0]])


@dataclass
class BlastRadiusResult:
    """Result of blast radius calculation."""

    failed_service: str
    affected_services: set[str]
    impact_levels: dict[str, int]  # Service -> distance from failure
    total_affected: int

    @property
    def critical_services(self) -> set[str]:
        """Services directly dependent on the failed service."""
        return {svc for svc, level in self.impact_levels.items() if level == 1}


@dataclass
class CriticalityScore:
    """Service criticality score and ranking."""

    service: str
    score: float
    rank: int
    is_critical: bool
    reasons: list[str]


def tarjan_scc(adj_list: dict[str, set[str]]) -> list[list[str]]:
    """Find strongly connected components using Tarjan's algorithm.

    This detects circular dependencies in the service graph.

    Args:
        adj_list: Adjacency list representation of the graph

    Returns:
        List of strongly connected components (each is a list of services)
    """
    index_counter = [0]
    stack: list[str] = []
    lowlinks: dict[str, int] = {}
    index: dict[str, int] = {}
    on_stack: set[str] = set()
    sccs: list[list[str]] = []

    def strongconnect(node: str) -> None:
        # Set the depth index for this node
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        # Consider successors
        for successor in adj_list.get(node, set()):
            if successor not in index:
                # Successor has not yet been visited; recurse
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in on_stack:
                # Successor is in stack and hence in current SCC
                lowlinks[node] = min(lowlinks[node], index[successor])

        # If node is a root node, pop the stack and generate an SCC
        if lowlinks[node] == index[node]:
            scc: list[str] = []
            while True:
                successor = stack.pop()
                on_stack.remove(successor)
                scc.append(successor)
                if successor == node:
                    break
            sccs.append(scc)

    # Run for all nodes
    for node in adj_list:
        if node not in index:
            strongconnect(node)

    return sccs


def detect_circular_dependencies(adj_list: dict[str, set[str]]) -> list[CircularDependency]:
    """Detect all circular dependencies in the service graph.

    Args:
        adj_list: Adjacency list representation of the graph

    Returns:
        List of circular dependencies found
    """
    sccs = tarjan_scc(adj_list)

    # Filter to only cycles (SCCs with more than one node, or self-loops)
    circular_deps: list[CircularDependency] = []

    for scc in sccs:
        # Check if it's a cycle
        if len(scc) > 1:
            circular_deps.append(
                CircularDependency(
                    services=scc,
                    cycle_length=len(scc),
                )
            )
        elif len(scc) == 1:
            # Check for self-loop
            node = scc[0]
            if node in adj_list.get(node, set()):
                circular_deps.append(
                    CircularDependency(
                        services=[node],
                        cycle_length=1,
                    )
                )

    return circular_deps


def calculate_blast_radius(
    adj_list: dict[str, set[str]],
    failed_service: str,
) -> BlastRadiusResult:
    """Calculate the blast radius of a service failure using BFS.

    Determines all services that would be affected if the specified
    service fails, along with their impact levels (distance from failure).

    Args:
        adj_list: Adjacency list representation of the graph
        failed_service: The service that has failed

    Returns:
        BlastRadiusResult with affected services and impact levels
    """
    if failed_service not in adj_list:
        return BlastRadiusResult(
            failed_service=failed_service,
            affected_services=set(),
            impact_levels={},
            total_affected=0,
        )

    # BFS to find all affected services
    queue = deque([(failed_service, 0)])
    visited: set[str] = {failed_service}
    impact_levels: dict[str, int] = {failed_service: 0}

    while queue:
        current, level = queue.popleft()

        # Check all services that depend on current
        for successor in adj_list.get(current, set()):
            if successor not in visited:
                visited.add(successor)
                impact_levels[successor] = level + 1
                queue.append((successor, level + 1))

    # Remove the failed service itself from affected list
    affected = visited - {failed_service}

    return BlastRadiusResult(
        failed_service=failed_service,
        affected_services=affected,
        impact_levels=impact_levels,
        total_affected=len(affected),
    )


def compute_pagerank(
    adj_list: dict[str, set[str]],
    damping: float = 0.85,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> dict[str, float]:
    """Compute PageRank scores for services.

    Higher PageRank indicates more critical services that many others depend on.

    Args:
        adj_list: Adjacency list representation of the graph
        damping: Damping factor (typically 0.85)
        max_iterations: Maximum number of iterations
        tolerance: Convergence tolerance

    Returns:
        Dictionary mapping service names to PageRank scores
    """
    if not adj_list:
        return {}

    nodes = list(adj_list.keys())
    n = len(nodes)

    # Initialize PageRank scores
    pagerank: dict[str, float] = dict.fromkeys(nodes, 1.0 / n)

    # Build reverse adjacency list (who points to each node)
    reverse_adj: dict[str, set[str]] = defaultdict(set)
    for node, successors in adj_list.items():
        for successor in successors:
            reverse_adj[successor].add(node)

    # Iterative PageRank calculation
    for _iteration in range(max_iterations):
        new_pagerank: dict[str, float] = {}
        max_diff = 0.0

        for node in nodes:
            # Calculate new PageRank
            rank_sum = 0.0
            for predecessor in reverse_adj[node]:
                # Contribution from each predecessor
                out_degree = len(adj_list[predecessor])
                if out_degree > 0:
                    rank_sum += pagerank[predecessor] / out_degree

            new_rank = (1 - damping) / n + damping * rank_sum
            new_pagerank[node] = new_rank

            # Track convergence
            max_diff = max(max_diff, abs(new_rank - pagerank[node]))

        pagerank = new_pagerank

        # Check for convergence
        if max_diff < tolerance:
            break

    return pagerank


def calculate_service_criticality(
    adj_list: dict[str, set[str]],
    reverse_adj_list: dict[str, set[str]],
    threshold: float = 0.7,
) -> list[CriticalityScore]:
    """Calculate criticality scores for all services.

    Combines multiple metrics:
    - PageRank (importance in dependency graph)
    - In-degree (how many services depend on it)
    - Out-degree (how many services it depends on)

    Args:
        adj_list: Adjacency list (forward dependencies)
        reverse_adj_list: Reverse adjacency list (backward dependencies)
        threshold: Score threshold to mark as critical (0.0 to 1.0)

    Returns:
        List of CriticalityScore objects, sorted by criticality
    """
    if not adj_list:
        return []

    # Calculate PageRank
    pagerank = compute_pagerank(adj_list)

    # Calculate in-degree and out-degree
    max_in_degree = max(len(deps) for deps in reverse_adj_list.values()) or 1
    max_out_degree = max(len(deps) for deps in adj_list.values()) or 1

    scores: list[CriticalityScore] = []

    for service in adj_list.keys():
        in_degree = len(reverse_adj_list.get(service, set()))
        out_degree = len(adj_list.get(service, set()))

        # Normalize metrics
        norm_pagerank = pagerank.get(service, 0.0) * len(adj_list)
        norm_in_degree = in_degree / max_in_degree
        norm_out_degree = out_degree / max_out_degree

        # Calculate criticality score (weighted combination)
        # Higher in-degree and PageRank = more critical
        # High out-degree = less independent, but not necessarily less critical
        criticality = 0.5 * norm_pagerank + 0.4 * norm_in_degree + 0.1 * norm_out_degree

        reasons = []
        if norm_in_degree > 0.7:
            reasons.append(f"High dependency count ({in_degree} services)")
        if norm_pagerank > 0.7:
            reasons.append("Central to dependency graph")
        if out_degree == 0:
            reasons.append("Leaf service (no dependencies)")
        if out_degree > max_out_degree * 0.7:
            reasons.append(f"Depends on many services ({out_degree})")

        scores.append(
            CriticalityScore(
                service=service,
                score=criticality,
                rank=0,  # Will be set after sorting
                is_critical=criticality >= threshold,
                reasons=reasons,
            )
        )

    # Sort by criticality (descending) and assign ranks
    scores.sort(key=lambda x: x.score, reverse=True)
    for idx, score in enumerate(scores, start=1):
        score.rank = idx

    return scores


def compute_betweenness_centrality(adj_list: dict[str, set[str]]) -> dict[str, float]:
    """Compute betweenness centrality to identify bottleneck services.

    Services with high betweenness centrality are bottlenecks that
    many paths flow through.

    Args:
        adj_list: Adjacency list representation of the graph

    Returns:
        Dictionary mapping service names to betweenness scores
    """
    nodes = list(adj_list.keys())
    betweenness: dict[str, float] = dict.fromkeys(nodes, 0.0)

    for source in nodes:
        # Single-source shortest paths (BFS)
        stack: list[str] = []
        predecessors: dict[str, list[str]] = defaultdict(list)
        sigma: dict[str, int] = defaultdict(int)
        sigma[source] = 1
        distance: dict[str, int] = {}
        distance[source] = 0

        queue = deque([source])

        while queue:
            current = queue.popleft()
            stack.append(current)

            for neighbor in adj_list.get(current, set()):
                # First time we see this neighbor?
                if neighbor not in distance:
                    queue.append(neighbor)
                    distance[neighbor] = distance[current] + 1

                # Shortest path to neighbor via current?
                if distance[neighbor] == distance[current] + 1:
                    sigma[neighbor] += sigma[current]
                    predecessors[neighbor].append(current)

        # Accumulate betweenness
        delta: dict[str, float] = defaultdict(float)

        while stack:
            node = stack.pop()
            for predecessor in predecessors[node]:
                delta[predecessor] += sigma[predecessor] / sigma[node] * (1 + delta[node])

            if node != source:
                betweenness[node] += delta[node]

    # Normalize (for directed graphs, divide by (n-1)(n-2))
    n = len(nodes)
    if n > 2:
        normalize_factor = (n - 1) * (n - 2)
        betweenness = {node: score / normalize_factor for node, score in betweenness.items()}

    return betweenness


def topological_sort(adj_list: dict[str, set[str]]) -> list[str] | None:
    """Perform topological sort on the dependency graph.

    Returns a deployment order where dependencies are deployed before
    services that depend on them.

    Args:
        adj_list: Adjacency list representation of the graph

    Returns:
        List of services in topological order, or None if graph has cycles
    """
    # Calculate in-degrees
    in_degree: dict[str, int] = dict.fromkeys(adj_list, 0)

    for node in adj_list:
        for successor in adj_list[node]:
            if successor not in in_degree:
                in_degree[successor] = 0
            in_degree[successor] += 1

    # Find all nodes with in-degree 0
    queue = deque([node for node, degree in in_degree.items() if degree == 0])
    result: list[str] = []

    while queue:
        node = queue.popleft()
        result.append(node)

        # Reduce in-degree for successors
        for successor in adj_list.get(node, set()):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    # If we processed all nodes, return the order
    if len(result) == len(in_degree):
        return result

    # Otherwise, graph has cycles
    return None


def find_critical_path(
    adj_list: dict[str, set[str]],
    edge_weights: dict[tuple[str, str], float],
) -> list[str]:
    """Find the critical path (longest path) through the dependency graph.

    Useful for understanding the slowest dependency chain.

    Args:
        adj_list: Adjacency list representation
        edge_weights: Dictionary mapping (source, target) to weight (e.g., latency)

    Returns:
        List of services in the critical path
    """
    # Try topological sort first
    topo_order = topological_sort(adj_list)
    if topo_order is None:
        # Graph has cycles, cannot find critical path
        return []

    # Calculate longest paths
    dist: dict[str, float] = dict.fromkeys(adj_list, 0.0)
    predecessor: dict[str, str | None] = dict.fromkeys(adj_list)

    # Process nodes in topological order
    for node in topo_order:
        for successor in adj_list.get(node, set()):
            weight = edge_weights.get((node, successor), 1.0)
            if dist[node] + weight > dist[successor]:
                dist[successor] = dist[node] + weight
                predecessor[successor] = node

    # Find the node with maximum distance
    max_node = max(dist, key=dist.get)  # type: ignore

    # Backtrack to find the path
    path: list[str] = []
    current: str | None = max_node

    while current is not None:
        path.append(current)
        current = predecessor[current]

    path.reverse()
    return path
