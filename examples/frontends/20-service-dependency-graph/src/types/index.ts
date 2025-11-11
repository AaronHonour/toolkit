/**
 * TypeScript types for Service Dependency Graph application
 */

export interface Service {
  id: string;
  name: string;
  service_type: string;
  endpoints: string[];
  metadata: Record<string, any>;
  health_score: number;
  created_at: string;
  updated_at: string;
}

export interface Dependency {
  id: string;
  source: string;
  target: string;
  dependency_type: string;
  weight: number;
  latency_p99: number | null;
  error_rate: number;
  request_rate: number;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CircularDependency {
  services: string[];
  cycle_length: number;
  cycle_path: string;
}

export interface CriticalityScore {
  service: string;
  score: number;
  rank: number;
  is_critical: boolean;
  reasons: string[];
}

export interface BlastRadiusResult {
  failed_service: string;
  affected_services: string[];
  impact_levels: Record<string, number>;
  total_affected: number;
  critical_services: string[];
}

export interface AnalysisReport {
  analysis_type: string;
  generated_at: string;
  service_count: number;
  dependency_count: number;
  has_circular_dependencies: boolean;
  circular_dependencies: CircularDependency[];
  critical_services: CriticalityScore[];
  bottlenecks: Record<string, number>;
  deployment_order: string[] | null;
  insights: string[];
  warnings: string[];
  recommendations: string[];
}

export interface ChangeImpact {
  service: string;
  impact_level: number;
  impact_type: string;
  probability: number;
  estimated_downtime_minutes: number | null;
  mitigation: string | null;
}

export interface ImpactReport {
  change_type: string;
  source_service: string;
  generated_at: string;
  total_affected: number;
  direct_impact: ChangeImpact[];
  indirect_impact: ChangeImpact[];
  cascading_impact: ChangeImpact[];
  risk_level: string;
  pre_change_actions: string[];
  monitoring_required: string[];
  rollback_plan: string | null;
}

// D3 Graph data structures
export interface D3Node {
  id: string;
  name: string;
  type: string;
  health: number;
  endpoints: string[];
  metadata: Record<string, any>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface D3Link {
  source: string | D3Node;
  target: string | D3Node;
  type: string;
  weight: number;
  latency_p99: number | null;
  error_rate: number;
  request_rate: number;
  metadata: Record<string, any>;
}

export interface D3GraphData {
  nodes: D3Node[];
  links: D3Link[];
}

// API Request types
export interface CreateServiceRequest {
  name: string;
  service_type: string;
  endpoints: string[];
  metadata: Record<string, any>;
}

export interface CreateDependencyRequest {
  source: string;
  target: string;
  dependency_type: string;
  weight: number;
  metadata: Record<string, any>;
}

export interface ImpactAnalysisRequest {
  service_name: string;
  change_type: string;
  failure_probability: number;
  is_breaking_change: boolean;
  expected_downtime_minutes: number;
  degradation_factor: number;
}
