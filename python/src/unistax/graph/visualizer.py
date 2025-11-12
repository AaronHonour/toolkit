"""Graph visualization utilities for exporting to various formats."""

from enum import Enum
from typing import Any

from unistax.graph.structures import ServiceDependencyGraph


class VisualizationFormat(str, Enum):
    """Supported visualization formats."""

    D3_FORCE = "d3_force"  # D3.js force-directed graph
    CYTOSCAPE = "cytoscape"  # Cytoscape.js format
    MERMAID = "mermaid"  # Mermaid diagram
    GRAPHVIZ = "graphviz"  # DOT format


class GraphVisualizer:
    """Converts service dependency graphs to various visualization formats."""

    @staticmethod
    def to_d3_force(graph: ServiceDependencyGraph) -> dict[str, Any]:
        """Convert graph to D3.js force-directed format.

        Returns:
            Dictionary with 'nodes' and 'links' arrays for D3.js
        """
        nodes = []
        for service in graph.get_all_services():
            nodes.append({
                "id": service.name,
                "name": service.name,
                "type": service.service_type.value,
                "health": service.health_score,
                "endpoints": service.endpoints,
                "metadata": service.metadata,
            })

        links = []
        for dep in graph.get_all_dependencies():
            links.append({
                "source": dep.source,
                "target": dep.target,
                "type": dep.dependency_type.value,
                "weight": dep.weight,
                "latency_p99": dep.latency_p99,
                "error_rate": dep.error_rate,
                "request_rate": dep.request_rate,
                "metadata": dep.metadata,
            })

        return {
            "nodes": nodes,
            "links": links,
        }

    @staticmethod
    def to_cytoscape(graph: ServiceDependencyGraph) -> dict[str, list[dict[str, Any]]]:
        """Convert graph to Cytoscape.js format.

        Returns:
            Dictionary with 'elements' array containing nodes and edges
        """
        elements = []

        # Add nodes
        for service in graph.get_all_services():
            elements.append({
                "data": {
                    "id": service.name,
                    "label": service.name,
                    "type": service.service_type.value,
                    "health": service.health_score,
                    "endpoints": service.endpoints,
                    **service.metadata,
                }
            })

        # Add edges
        for dep in graph.get_all_dependencies():
            edge_id = f"{dep.source}-{dep.target}"
            elements.append({
                "data": {
                    "id": edge_id,
                    "source": dep.source,
                    "target": dep.target,
                    "type": dep.dependency_type.value,
                    "weight": dep.weight,
                    "latency_p99": dep.latency_p99,
                    "error_rate": dep.error_rate,
                    "request_rate": dep.request_rate,
                    **dep.metadata,
                }
            })

        return {"elements": elements}

    @staticmethod
    def to_mermaid(graph: ServiceDependencyGraph) -> str:
        """Convert graph to Mermaid diagram format.

        Returns:
            Mermaid diagram string
        """
        lines = ["graph TD"]

        # Add nodes with styling
        for service in graph.get_all_services():
            node_id = service.name.replace("-", "_").replace(" ", "_")
            node_label = service.name

            # Style based on service type
            if service.service_type.value == "database":
                lines.append(f'    {node_id}[("{node_label}")]')
            elif service.service_type.value == "cache":
                lines.append(f'    {node_id}{{"{node_label}"}}')
            elif service.service_type.value == "queue":
                lines.append(f'    {node_id}{{{{"{node_label}"}}}}')
            else:
                lines.append(f'    {node_id}["{node_label}"]')

        # Add edges
        for dep in graph.get_all_dependencies():
            source_id = dep.source.replace("-", "_").replace(" ", "_")
            target_id = dep.target.replace("-", "_").replace(" ", "_")

            # Add label with dependency type
            edge_label = dep.dependency_type.value.replace("_", " ")
            lines.append(f'    {source_id} -->|{edge_label}| {target_id}')

        return "\n".join(lines)

    @staticmethod
    def to_graphviz(graph: ServiceDependencyGraph) -> str:
        """Convert graph to Graphviz DOT format.

        Returns:
            DOT format string
        """
        lines = ["digraph ServiceDependencies {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box, style=rounded];")
        lines.append("")

        # Add nodes with attributes
        for service in graph.get_all_services():
            node_id = f'"{service.name}"'

            # Color based on health
            if service.health_score >= 0.9:
                color = "green"
            elif service.health_score >= 0.7:
                color = "yellow"
            else:
                color = "red"

            # Shape based on type
            shape_map = {
                "database": "cylinder",
                "cache": "component",
                "queue": "folder",
                "api": "box",
                "gateway": "hexagon",
            }
            shape = shape_map.get(service.service_type.value, "box")

            lines.append(
                f'    {node_id} [label="{service.name}", '
                f'color={color}, shape={shape}];'
            )

        lines.append("")

        # Add edges
        for dep in graph.get_all_dependencies():
            source_id = f'"{dep.source}"'
            target_id = f'"{dep.target}"'

            # Edge style based on type
            style_map = {
                "api_call": "solid",
                "database": "bold",
                "message_queue": "dashed",
                "cache": "dotted",
            }
            style = style_map.get(dep.dependency_type.value, "solid")

            # Add edge with attributes
            label = dep.dependency_type.value.replace("_", " ")
            lines.append(
                f'    {source_id} -> {target_id} '
                f'[label="{label}", style={style}];'
            )

        lines.append("}")
        return "\n".join(lines)

    @classmethod
    def export(
        cls,
        graph: ServiceDependencyGraph,
        format: VisualizationFormat,
    ) -> Any:
        """Export graph to specified visualization format.

        Args:
            graph: Service dependency graph to export
            format: Target visualization format

        Returns:
            Formatted graph data (dict for D3/Cytoscape, string for Mermaid/Graphviz)
        """
        if format == VisualizationFormat.D3_FORCE:
            return cls.to_d3_force(graph)
        elif format == VisualizationFormat.CYTOSCAPE:
            return cls.to_cytoscape(graph)
        elif format == VisualizationFormat.MERMAID:
            return cls.to_mermaid(graph)
        elif format == VisualizationFormat.GRAPHVIZ:
            return cls.to_graphviz(graph)
        else:
            raise ValueError(f"Unsupported format: {format}")
