/**
 * Time-Series Database Dashboard
 * Example 8: Metrics Storage (1M+ points/sec)
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';
import {
  AppLayout,
  StatsBar,
  LoadingState,
  EmptyState,
  DataCard,
  DataTable,
} from '@frontend-toolkit/layouts';

interface Metric {
  name: string;
  value: number;
  timestamp: number;
  tags: Record<string, string>;
}

interface Stats {
  datapoints_ingested?: number;
  ingestion_rate?: number;
  compression_ratio?: number;
}

const API_URL = 'http://localhost:8007';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, m] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/metrics/recent?limit=20`),
        ]);
        setStats(await s.json());
        const metricsData = await m.json();
        setMetrics(metricsData.metrics || []);
        setLoading(false);
      } catch (error) {
        console.error('Error:', error);
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  // Convert stats to StatsBar format
  const statsData = [
    {
      label: 'Datapoints Ingested',
      value: stats.datapoints_ingested?.toLocaleString() || '0',
    },
    {
      label: 'Ingestion Rate',
      value: `${stats.ingestion_rate?.toLocaleString() || 0}/sec`,
      variant: 'success' as const,
    },
    {
      label: 'Compression Ratio',
      value: `${stats.compression_ratio?.toFixed(1) || 0}:1`,
      variant: 'primary' as const,
    },
  ];

  // DataTable columns
  const columns = [
    {
      key: 'name' as const,
      label: 'Metric Name',
      render: (metric: Metric) => (
        <div>
          <div className="font-semibold text-sm text-neutral-900">{metric.name}</div>
          <div className="text-xs text-neutral-500">
            {Object.entries(metric.tags)
              .map(([k, v]) => `${k}=${v}`)
              .join(', ')}
          </div>
        </div>
      ),
    },
    {
      key: 'value' as const,
      label: 'Value',
      render: (metric: Metric) => (
        <div className="font-bold text-lg text-neutral-900">{metric.value.toFixed(2)}</div>
      ),
    },
    {
      key: 'timestamp' as const,
      label: 'Timestamp',
      render: (metric: Metric) => (
        <Badge variant="primary" size="sm">
          {new Date(metric.timestamp * 1000).toLocaleTimeString()}
        </Badge>
      ),
    },
  ];

  return (
    <AppLayout
      title="Time-Series Database"
      description="Metrics Storage (1M+ points/sec)"
      icon="📈"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8007
          </div>
          <div>
            <span className="font-semibold">Database:</span> Time-Series Optimized Storage
          </div>
        </div>
      }
    >
      {/* Stats Bar */}
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      {/* Main Content */}
      {loading ? (
        <LoadingState message="Loading metrics data..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <DataCard
            title="Data Ingestion"
            subtitle="Real-time metric collection"
            badge={{
              label: 'Active',
              variant: 'success',
            }}
            metadata={[
              { label: 'Backend', value: 'localhost:8007' },
              { label: 'Protocol', value: 'HTTP/REST' },
            ]}
          >
            <div className="space-y-3">
              <div className="p-3 bg-success-50 rounded border border-success-200">
                <div className="text-xs text-success-700">Ingestion Rate</div>
                <div className="text-xl font-bold text-success-900">
                  {stats.ingestion_rate ? `${(stats.ingestion_rate / 1000).toFixed(1)}K` : '0'}
                </div>
                <div className="text-xs text-success-600">datapoints/sec</div>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
                High-throughput metric ingestion
              </div>
            </div>
          </DataCard>

          <DataCard
            title="Storage Efficiency"
            subtitle="Data compression"
            badge={{
              label: stats.compression_ratio && stats.compression_ratio > 5 ? 'Excellent' : 'Good',
              variant: stats.compression_ratio && stats.compression_ratio > 5 ? 'success' : 'warning',
            }}
          >
            <div className="space-y-3">
              <div className="p-3 bg-primary-50 rounded border border-primary-200">
                <div className="text-xs text-primary-700">Compression Ratio</div>
                <div className="text-xl font-bold text-primary-900">
                  {stats.compression_ratio?.toFixed(1) || 0}:1
                </div>
                <div className="text-xs text-primary-600">space savings</div>
              </div>
              <div className="text-xs text-neutral-600">
                Optimized time-series compression algorithms
              </div>
            </div>
          </DataCard>

          <DataCard
            title="Total Datapoints"
            subtitle="Historical metrics"
            badge={{
              label: 'Stored',
              variant: 'primary',
            }}
          >
            <div className="space-y-3">
              <div className="p-3 bg-neutral-50 rounded">
                <div className="text-xs text-neutral-600">Total Ingested</div>
                <div className="text-xl font-bold text-neutral-900">
                  {stats.datapoints_ingested
                    ? stats.datapoints_ingested > 1000000
                      ? `${(stats.datapoints_ingested / 1000000).toFixed(2)}M`
                      : stats.datapoints_ingested.toLocaleString()
                    : '0'}
                </div>
                <div className="text-xs text-neutral-500">datapoints</div>
              </div>
              <div className="text-xs text-neutral-600">
                All metrics stored with high compression
              </div>
            </div>
          </DataCard>
        </div>
      )}

      {/* Metrics Table */}
      <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-neutral-900">Recent Metrics</h2>
          <p className="text-sm text-neutral-600">Latest datapoints from the time-series database</p>
        </div>
        {loading ? (
          <LoadingState message="Loading metrics..." />
        ) : metrics.length > 0 ? (
          <DataTable data={metrics} columns={columns} />
        ) : (
          <EmptyState
            icon="📈"
            title="No metrics yet"
            description="Metrics will appear here as they are ingested into the database."
          />
        )}
      </div>
    </AppLayout>
  );
}
