/**
 * Lambda Architecture Dashboard
 *
 * Connects to Example 12: Lambda Architecture (localhost:8012)
 *
 * Features:
 * - Batch Layer: 10M+ records/batch
 * - Speed Layer: 100K+ events/sec real-time
 * - Serving Layer: 500K+ queries/sec
 * - < 1s data freshness
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import { Badge, Button } from '@frontend-toolkit/atoms';
import {
  AppLayout,
  StatsBar,
  DataCard,
} from '@frontend-toolkit/layouts';

interface LayerStats {
  batch: {
    records_processed: number;
    last_batch_time: number;
    batch_size: number;
  };
  speed: {
    events_processed: number;
    events_per_sec: number;
    latency_ms: number;
  };
  serving: {
    queries_total: number;
    queries_per_sec: number;
    cache_hit_rate: number;
  };
}

interface QueryResult {
  key: string;
  batch_view: any;
  realtime_view: any;
  merged_view: any;
  freshness_ms: number;
}

const API_URL = 'http://localhost:8012';

export function App() {
  const [stats, setStats] = useState<LayerStats | null>(null);
  const [queryKey, setQueryKey] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Stats error:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  const executeQuery = async () => {
    if (!queryKey) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/query?key=${encodeURIComponent(queryKey)}`);
      const data = await response.json();
      setQueryResult(data);
    } catch (error) {
      console.error('Query error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Convert stats to StatsBar format
  const statsData = stats
    ? [
        {
          label: 'Batch Records',
          value: stats.batch.records_processed.toLocaleString(),
        },
        {
          label: 'Speed Events',
          value: `${stats.speed.events_per_sec.toLocaleString()}/sec`,
          variant: 'success' as const,
        },
        {
          label: 'Query Rate',
          value: `${stats.serving.queries_per_sec.toLocaleString()}/sec`,
        },
        {
          label: 'Cache Hit Rate',
          value: `${(stats.serving.cache_hit_rate * 100).toFixed(1)}%`,
          variant: 'success' as const,
        },
      ]
    : [];

  return (
    <AppLayout
      title="Lambda Architecture"
      description="Batch + Speed + Serving Layers (500K+ queries/sec)"
      icon="⚡"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8012
          </div>
          <div>
            <span className="font-semibold">Powered by:</span> LRUCache serving layer
          </div>
        </div>
      }
    >
      {/* Stats Bar */}
      {stats && (
        <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
          <StatsBar stats={statsData} variant="compact" />
        </div>
      )}

      {/* Layer Status */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Batch Layer */}
          <DataCard
            title="Batch Layer"
            subtitle="High-accuracy batch processing"
            badge={{ label: 'Accurate', variant: 'primary' }}
          >
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-neutral-600">Records Processed</dt>
                <dd className="text-2xl font-bold text-neutral-900">
                  {stats.batch.records_processed.toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-600">Batch Size</dt>
                <dd className="text-lg font-semibold text-neutral-900">
                  {(stats.batch.batch_size / 1_000_000).toFixed(1)}M
                </dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-600">Last Batch</dt>
                <dd className="text-sm text-neutral-900">
                  {new Date(stats.batch.last_batch_time * 1000).toLocaleTimeString()}
                </dd>
              </div>
            </dl>
          </DataCard>

          {/* Speed Layer */}
          <DataCard
            title="Speed Layer"
            subtitle="Real-time stream processing"
            badge={{
              label: 'Real-time',
              variant: 'success',
              dot: true,
              dotColor: 'success',
            }}
          >
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-neutral-600">Events Processed</dt>
                <dd className="text-2xl font-bold text-neutral-900">
                  {stats.speed.events_processed.toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-600">Ingestion Rate</dt>
                <dd className="text-lg font-semibold text-success-700">
                  {stats.speed.events_per_sec.toLocaleString()}/sec
                </dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-600">Latency</dt>
                <dd className="text-sm text-neutral-900">{stats.speed.latency_ms.toFixed(2)}ms</dd>
              </div>
            </dl>
          </DataCard>

          {/* Serving Layer */}
          <DataCard
            title="Serving Layer"
            subtitle="Merged view queries"
            badge={{ label: 'Merged', variant: 'amber' }}
          >
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-neutral-600">Total Queries</dt>
                <dd className="text-2xl font-bold text-neutral-900">
                  {stats.serving.queries_total.toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-600">Query Rate</dt>
                <dd className="text-lg font-semibold text-primary-700">
                  {stats.serving.queries_per_sec.toLocaleString()}/sec
                </dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-600">Cache Hit Rate</dt>
                <dd className="text-sm text-neutral-900">
                  {(stats.serving.cache_hit_rate * 100).toFixed(1)}%
                </dd>
              </div>
            </dl>
          </DataCard>
        </div>
      )}

      {/* Query Interface */}
      <DataCard
        title="Query Data"
        subtitle="Query merged views from batch and speed layers"
        className="mb-6"
      >
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={queryKey}
            onChange={(e) => setQueryKey(e.target.value)}
            placeholder="Enter query key..."
            className="flex-1 px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            onKeyPress={(e) => e.key === 'Enter' && executeQuery()}
          />
          <Button
            onClick={executeQuery}
            disabled={!queryKey || loading}
            loading={loading}
          >
            Query
          </Button>
        </div>

        {queryResult && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-success-50 rounded-lg border border-success-200">
              <span className="text-sm font-medium text-success-900">Data Freshness</span>
              <Badge variant="success">{queryResult.freshness_ms}ms</Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
                <h3 className="text-sm font-semibold text-primary-900 mb-2">Batch View</h3>
                <pre className="text-xs text-primary-700 overflow-auto">
                  {JSON.stringify(queryResult.batch_view, null, 2)}
                </pre>
              </div>
              <div className="p-4 bg-success-50 rounded-lg border border-success-200">
                <h3 className="text-sm font-semibold text-success-900 mb-2">Realtime View</h3>
                <pre className="text-xs text-success-700 overflow-auto">
                  {JSON.stringify(queryResult.realtime_view, null, 2)}
                </pre>
              </div>
              <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                <h3 className="text-sm font-semibold text-amber-900 mb-2">Merged View</h3>
                <pre className="text-xs text-amber-700 overflow-auto">
                  {JSON.stringify(queryResult.merged_view, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </DataCard>

      {/* Architecture Diagram */}
      <DataCard
        title="Lambda Architecture Flow"
        subtitle="Visual representation of the three-layer architecture"
      >
        <div className="flex items-center justify-center">
          <svg className="w-full max-w-4xl" viewBox="0 0 800 400">
            {/* Batch Layer */}
            <g>
              <rect x="50" y="50" width="200" height="100" rx="8" fill="#EFF6FF" stroke="#3B82F6" strokeWidth="2" />
              <text x="150" y="90" textAnchor="middle" className="text-sm font-semibold fill-primary-900">Batch Layer</text>
              <text x="150" y="110" textAnchor="middle" className="text-xs fill-primary-700">10M+ records/batch</text>
              <text x="150" y="130" textAnchor="middle" className="text-xs fill-primary-700">Accurate</text>
            </g>

            {/* Speed Layer */}
            <g>
              <rect x="50" y="250" width="200" height="100" rx="8" fill="#F0FDF4" stroke="#22C55E" strokeWidth="2" />
              <text x="150" y="290" textAnchor="middle" className="text-sm font-semibold fill-success-900">Speed Layer</text>
              <text x="150" y="310" textAnchor="middle" className="text-xs fill-success-700">100K+ events/sec</text>
              <text x="150" y="330" textAnchor="middle" className="text-xs fill-success-700">Real-time</text>
            </g>

            {/* Serving Layer */}
            <g>
              <rect x="550" y="150" width="200" height="100" rx="8" fill="#FEF3C7" stroke="#F59E0B" strokeWidth="2" />
              <text x="650" y="190" textAnchor="middle" className="text-sm font-semibold fill-amber-900">Serving Layer</text>
              <text x="650" y="210" textAnchor="middle" className="text-xs fill-amber-700">500K+ queries/sec</text>
              <text x="650" y="230" textAnchor="middle" className="text-xs fill-amber-700">Merged Views</text>
            </g>

            {/* Arrows */}
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#6B7280" />
              </marker>
            </defs>
            <line x1="250" y1="100" x2="550" y2="180" stroke="#6B7280" strokeWidth="2" markerEnd="url(#arrowhead)" />
            <line x1="250" y1="300" x2="550" y2="220" stroke="#6B7280" strokeWidth="2" markerEnd="url(#arrowhead)" />

            {/* Labels */}
            <text x="350" y="130" textAnchor="middle" className="text-xs fill-neutral-600">Batch View</text>
            <text x="350" y="280" textAnchor="middle" className="text-xs fill-neutral-600">Realtime View</text>
          </svg>
        </div>
      </DataCard>
    </AppLayout>
  );
}
