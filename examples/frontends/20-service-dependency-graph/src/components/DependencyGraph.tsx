/**
 * DependencyGraph - D3.js force-directed graph visualization component
 */

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import type { D3GraphData, D3Node, D3Link } from '../types';
import { Badge } from '@unistax/atoms';

interface DependencyGraphProps {
  data: D3GraphData;
  onNodeClick?: (node: D3Node) => void;
  selectedNode?: string | null;
  highlightedNodes?: Set<string>;
  width?: number;
  height?: number;
}

export function DependencyGraph({
  data,
  onNodeClick,
  selectedNode,
  highlightedNodes = new Set(),
  width = 800,
  height = 600,
}: DependencyGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<D3Node | null>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    // Clear previous render
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);

    // Create container group
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Color scale for node types
    const colorScale: Record<string, string> = {
      api: '#00D9FF',        // Cyan primary
      gateway: '#9D4EDD',    // Purple secondary
      database: '#10B981',   // Green
      cache: '#F59E0B',      // Amber
      queue: '#EC4899',      // Pink
      storage: '#8B5CF6',    // Violet
      external: '#6B7280',   // Gray
      worker: '#3B82F6',     // Blue
    };

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes as d3.SimulationNodeDatum[])
      .force('link', d3.forceLink(data.links)
        .id((d: any) => d.id)
        .distance(150)
        .strength(1)
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Create arrow markers for directed edges
    const defs = svg.append('defs');

    Object.keys(colorScale).forEach(type => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', colorScale[type] || '#6B7280');
    });

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', (d: any) => {
        const sourceNode = data.nodes.find(n => n.id === (typeof d.source === 'string' ? d.source : d.source.id));
        return colorScale[sourceNode?.type || 'api'] || '#6B7280';
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.max(1, d.weight * 2))
      .attr('marker-end', (d: any) => {
        const sourceNode = data.nodes.find(n => n.id === (typeof d.source === 'string' ? d.source : d.source.id));
        return `url(#arrow-${sourceNode?.type || 'api'})`;
      });

    // Draw nodes
    const node = g.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag<any, D3Node>()
        .on('start', (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      );

    // Add circles for nodes
    node.append('circle')
      .attr('r', (d: D3Node) => {
        if (selectedNode === d.id) return 24;
        if (highlightedNodes.has(d.id)) return 20;
        return 16;
      })
      .attr('fill', (d: D3Node) => colorScale[d.type] || '#6B7280')
      .attr('stroke', (d: D3Node) => {
        if (selectedNode === d.id) return '#000';
        if (highlightedNodes.has(d.id)) return '#FFA500';
        return '#fff';
      })
      .attr('stroke-width', (d: D3Node) => {
        if (selectedNode === d.id) return 3;
        if (highlightedNodes.has(d.id)) return 2.5;
        return 2;
      })
      .attr('opacity', (d: D3Node) => d.health);

    // Add text labels
    node.append('text')
      .text((d: D3Node) => d.name)
      .attr('x', 0)
      .attr('y', 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('font-weight', (d: D3Node) => selectedNode === d.id ? 'bold' : 'normal')
      .attr('fill', '#1F2937');

    // Add health indicator
    node.append('text')
      .text((d: D3Node) => `${Math.round(d.health * 100)}%`)
      .attr('x', 0)
      .attr('y', 5)
      .attr('text-anchor', 'middle')
      .attr('font-size', '9px')
      .attr('fill', '#fff');

    // Node interactions
    node.on('click', (event, d: D3Node) => {
      event.stopPropagation();
      onNodeClick?.(d);
    });

    node.on('mouseenter', (event, d: D3Node) => {
      setHoveredNode(d);
    });

    node.on('mouseleave', () => {
      setHoveredNode(null);
    });

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [data, selectedNode, highlightedNodes, width, height, onNodeClick]);

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-neutral-200 dark:border-dark-100 rounded-lg bg-white dark:bg-dark-200"
      />

      {/* Tooltip for hovered node */}
      {hoveredNode && (
        <div className="absolute top-4 right-4 bg-white dark:bg-dark-300 border border-neutral-200 dark:border-dark-100 rounded-lg shadow-lg p-4 max-w-sm">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h4 className="font-semibold text-neutral-900 dark:text-white">
              {hoveredNode.name}
            </h4>
            <Badge variant="primary" size="sm">
              {hoveredNode.type}
            </Badge>
          </div>
          <div className="space-y-1 text-sm text-neutral-600 dark:text-neutral-400">
            <div>Health: {Math.round(hoveredNode.health * 100)}%</div>
            {hoveredNode.endpoints.length > 0 && (
              <div>Endpoints: {hoveredNode.endpoints.length}</div>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white dark:bg-dark-300 border border-neutral-200 dark:border-dark-100 rounded-lg shadow-sm p-3">
        <div className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
          Service Types
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {Object.entries({
            api: 'API',
            gateway: 'Gateway',
            database: 'Database',
            cache: 'Cache',
            queue: 'Queue',
            worker: 'Worker',
          }).map(([type, label]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: {
                  api: '#00D9FF',
                  gateway: '#9D4EDD',
                  database: '#10B981',
                  cache: '#F59E0B',
                  queue: '#EC4899',
                  worker: '#3B82F6',
                }[type] }}
              />
              <span className="text-neutral-600 dark:text-neutral-400">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
