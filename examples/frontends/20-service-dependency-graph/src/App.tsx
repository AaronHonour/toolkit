/**
 * Service Dependency Graph Dashboard
 * Main application component
 */

import { useState, useEffect } from 'react';
import { AppLayout, StatsBar, Tabs, LoadingState } from '@unistax/layouts';
import { useDebounce } from '@unistax/performance';
import type {
  Service,
  Dependency,
  D3GraphData,
  AnalysisReport,
  ImpactReport,
  CreateServiceRequest,
  CreateDependencyRequest,
  ImpactAnalysisRequest,
  D3Node,
  BlastRadiusResult,
} from './types';

// Components
import { DependencyGraph } from './components/DependencyGraph';
import { ServiceManagement } from './components/ServiceManagement';
import { DependencyManagement } from './components/DependencyManagement';
import { AnalysisPanel } from './components/AnalysisPanel';
import { ImpactAnalysis } from './components/ImpactAnalysis';

const API_URL = '/api/v1';

export function App() {
  // State
  const [services, setServices] = useState<Service[]>([]);
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [graphData, setGraphData] = useState<D3GraphData | null>(null);
  const [analysisReport, setAnalysisReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  // Graph interaction state
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [blastRadius, setBlastRadius] = useState<BlastRadiusResult | null>(null);
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());

  // Debounce analysis to avoid excessive API calls
  const serviceCount = services.length;
  const debouncedServiceCount = useDebounce(serviceCount, 500);

  // Fetch services and dependencies
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [servicesRes, depsRes] = await Promise.all([
          fetch(`${API_URL}/services`),
          fetch(`${API_URL}/dependencies`),
        ]);

        const servicesData = await servicesRes.json();
        const depsData = await depsRes.json();

        setServices(servicesData);
        setDependencies(depsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Fetch graph visualization data
  useEffect(() => {
    if (services.length === 0) {
      setGraphData(null);
      return;
    }

    const fetchGraph = async () => {
      try {
        const response = await fetch(`${API_URL}/visualize?format=d3`);
        const data = await response.json();
        setGraphData(data);
      } catch (error) {
        console.error('Failed to fetch graph data:', error);
      }
    };

    fetchGraph();
  }, [services, dependencies]);

  // Fetch analysis report when services/dependencies change
  useEffect(() => {
    if (debouncedServiceCount === 0) {
      setAnalysisReport(null);
      return;
    }

    const fetchAnalysis = async () => {
      setAnalysisLoading(true);
      try {
        const response = await fetch(`${API_URL}/analysis/graph?analysis_type=full_analysis`);
        const data = await response.json();
        setAnalysisReport(data);
      } catch (error) {
        console.error('Failed to fetch analysis:', error);
      } finally {
        setAnalysisLoading(false);
      }
    };

    fetchAnalysis();
  }, [debouncedServiceCount, dependencies.length]);

  // Handle node click - calculate blast radius
  const handleNodeClick = async (node: D3Node) => {
    setSelectedNode(node.id);

    try {
      const response = await fetch(`${API_URL}/analysis/blast-radius/${node.id}`);
      const data: BlastRadiusResult = await response.json();
      setBlastRadius(data);

      // Highlight affected nodes
      const affected = new Set([
        node.id,
        ...data.affected_services,
      ]);
      setHighlightedNodes(affected);
    } catch (error) {
      console.error('Failed to calculate blast radius:', error);
    }
  };

  // API methods
  const handleCreateService = async (service: CreateServiceRequest) => {
    const response = await fetch(`${API_URL}/services`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(service),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create service');
    }

    const newService = await response.json();
    setServices([...services, newService]);
  };

  const handleDeleteService = async (serviceName: string) => {
    const response = await fetch(`${API_URL}/services/${serviceName}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete service');
    }

    setServices(services.filter(s => s.name !== serviceName));
    setDependencies(dependencies.filter(d => d.source !== serviceName && d.target !== serviceName));

    // Clear selection if deleted
    if (selectedNode === serviceName) {
      setSelectedNode(null);
      setBlastRadius(null);
      setHighlightedNodes(new Set());
    }
  };

  const handleCreateDependency = async (dep: CreateDependencyRequest) => {
    const response = await fetch(`${API_URL}/dependencies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dep),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create dependency');
    }

    const newDep = await response.json();
    setDependencies([...dependencies, newDep]);
  };

  const handleImpactAnalysis = async (request: ImpactAnalysisRequest): Promise<ImpactReport> => {
    const response = await fetch(`${API_URL}/analysis/impact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze impact');
    }

    return response.json();
  };

  // Stats for stats bar
  const stats = [
    {
      label: 'Services',
      value: services.length.toString(),
      trend: services.length > 0 ? 'up' as const : undefined,
      variant: 'primary' as const,
    },
    {
      label: 'Dependencies',
      value: dependencies.length.toString(),
      trend: dependencies.length > 0 ? 'up' as const : undefined,
      variant: 'secondary' as const,
    },
    {
      label: 'Circular Dependencies',
      value: analysisReport?.circular_dependencies.length.toString() || '0',
      trend: (analysisReport?.circular_dependencies.length || 0) > 0 ? 'down' as const : undefined,
      variant: (analysisReport?.circular_dependencies.length || 0) > 0 ? 'danger' as const : 'success' as const,
    },
    {
      label: 'Critical Services',
      value: analysisReport?.critical_services.filter(s => s.is_critical).length.toString() || '0',
      variant: 'warning' as const,
    },
  ];

  if (loading) {
    return <LoadingState message="Loading Service Dependency Graph..." />;
  }

  return (
    <AppLayout
      title="Service Dependency Graph"
      description="Visualize, analyze, and understand service dependencies"
      icon="🕸️"
    >
      {/* Stats Bar */}
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={stats} variant="compact" />
      </div>

      {/* Tabbed Interface */}
      <Tabs>
        {/* Graph View Tab */}
        <div label="Graph View">
          <div className="space-y-6">
            {/* Graph Visualization */}
            {graphData && graphData.nodes.length > 0 ? (
              <div>
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
                    Service Dependency Graph
                  </h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    Click on a service to see its blast radius and impact
                  </p>
                </div>

                <DependencyGraph
                  data={graphData}
                  onNodeClick={handleNodeClick}
                  selectedNode={selectedNode}
                  highlightedNodes={highlightedNodes}
                  width={Math.min(1200, window.innerWidth - 100)}
                  height={600}
                />
              </div>
            ) : (
              <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-12 text-center">
                <div className="text-6xl mb-4">🕸️</div>
                <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
                  No Services Yet
                </h3>
                <p className="text-neutral-600 dark:text-neutral-400 mb-4">
                  Add services and dependencies to visualize your service architecture
                </p>
              </div>
            )}

            {/* Blast Radius Display */}
            {blastRadius && (
              <div className="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-warning-900 dark:text-warning-400 mb-3">
                  ⚠️ Blast Radius: {blastRadius.failed_service}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-2xl font-bold text-warning-700 dark:text-warning-300">
                      {blastRadius.total_affected}
                    </div>
                    <div className="text-sm text-warning-600 dark:text-warning-400">
                      Services Affected
                    </div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-danger-700 dark:text-danger-300">
                      {blastRadius.critical_services.length}
                    </div>
                    <div className="text-sm text-danger-600 dark:text-danger-400">
                      Critically Affected
                    </div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-info-700 dark:text-info-300">
                      {Math.max(...Object.values(blastRadius.impact_levels))}
                    </div>
                    <div className="text-sm text-info-600 dark:text-info-400">
                      Max Impact Depth
                    </div>
                  </div>
                </div>
                {blastRadius.affected_services.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-warning-800 dark:text-warning-300 mb-2">
                      Affected Services:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {blastRadius.affected_services.map(service => (
                        <span
                          key={service}
                          className="px-2 py-1 bg-warning-100 dark:bg-warning-900/40 text-warning-800 dark:text-warning-200 rounded text-xs"
                        >
                          {service} (Level {blastRadius.impact_levels[service]})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Services Tab */}
        <div label="Services">
          <ServiceManagement
            services={services}
            onCreateService={handleCreateService}
            onDeleteService={handleDeleteService}
          />
        </div>

        {/* Dependencies Tab */}
        <div label="Dependencies">
          <DependencyManagement
            services={services}
            dependencies={dependencies}
            onCreateDependency={handleCreateDependency}
          />
        </div>

        {/* Analysis Tab */}
        <div label="Analysis">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
              Dependency Analysis
            </h2>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Comprehensive analysis of service dependencies and health
            </p>
          </div>

          <AnalysisPanel report={analysisReport} loading={analysisLoading} />
        </div>

        {/* Impact Analysis Tab */}
        <div label="Impact">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
              Impact Analysis
            </h2>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Assess the impact of changes, failures, and deployments
            </p>
          </div>

          <ImpactAnalysis
            services={services}
            onAnalyze={handleImpactAnalysis}
          />
        </div>
      </Tabs>
    </AppLayout>
  );
}
