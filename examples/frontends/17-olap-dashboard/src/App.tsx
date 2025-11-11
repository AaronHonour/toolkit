/**
 * Real-Time OLAP Dashboard
 *
 * Connects to Example 17: Real-Time OLAP Engine (localhost:8017)
 *
 * Features:
 * - Multi-dimensional analysis (100+ dimensions)
 * - Real-time drill-down/roll-up
 * - Windowed aggregations
 * - < 100ms query latency
 */

import { useState, useEffect } from 'react';
import { Button, Badge } from '@unistax/atoms';
import { AppLayout, StatsBar, DataCard, DataTable, EmptyState } from '@unistax/layouts';

interface Dimension {
  name: string;
  values: string[];
}

interface QueryResult {
  dimensions: Record<string, string>;
  metrics: Record<string, number>;
  count: number;
}

interface Stats {
  events_ingested: number;
  cubes_materialized: number;
  dimensions: number;
  ingestion_rate: number;
}

const API_URL = 'http://localhost:8017';

export function App() {
  const [dimensions, setDimensions] = useState<Dimension[]>([]);
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>([]);
  const [queryResults, setQueryResults] = useState<QueryResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<Stats>({
    events_ingested: 0,
    cubes_materialized: 0,
    dimensions: 0,
    ingestion_rate: 0,
  });
  const [queryLatency, setQueryLatency] = useState<number>(0);

  // Fetch dimensions
  useEffect(() => {
    const fetchDimensions = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/dimensions`);
        const data = await response.json();
        setDimensions(data.dimensions || []);
      } catch (error) {
        console.error('Dimensions error:', error);
      }
    };

    fetchDimensions();
  }, []);

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

  // Execute query
  const executeQuery = async () => {
    if (selectedDimensions.length === 0) return;

    setLoading(true);
    const start = performance.now();

    try {
      const response = await fetch(`${API_URL}/api/v1/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dimensions: selectedDimensions,
          metrics: ['sum', 'avg', 'count'],
        }),
      });
      const data = await response.json();
      const end = performance.now();

      setQueryResults(data.results || []);
      setQueryLatency(end - start);
    } catch (error) {
      console.error('Query error:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDimension = (dim: string) => {
    setSelectedDimensions((prev) =>
      prev.includes(dim) ? prev.filter((d) => d !== dim) : [...prev, dim]
    );
  };

  const statsItems = [
    { label: 'Events Ingested', value: stats.events_ingested.toLocaleString() },
    {
      label: 'Ingestion Rate',
      value: `${stats.ingestion_rate.toLocaleString()}/sec`,
      variant: 'success' as const,
    },
    { label: 'Dimensions', value: stats.dimensions.toString() },
  ];

  if (queryLatency > 0) {
    statsItems.push({
      label: 'Last Query',
      value: `${queryLatency.toFixed(2)}ms`,
      variant: (queryLatency < 100 ? 'success' : 'warning') as const,
    });
  }

  // Prepare table data
  const tableColumns = [
    ...selectedDimensions.map((dim) => ({
      key: `dim_${dim}`,
      header: dim,
      cell: (row: QueryResult) => row.dimensions[dim] || '-',
    })),
    {
      key: 'count',
      header: 'Count',
      cell: (row: QueryResult) => row.count.toLocaleString(),
    },
    {
      key: 'sum',
      header: 'Sum',
      cell: (row: QueryResult) => row.metrics.sum?.toFixed(2) || '-',
    },
    {
      key: 'avg',
      header: 'Avg',
      cell: (row: QueryResult) => row.metrics.avg?.toFixed(2) || '-',
    },
  ];

  return (
    <AppLayout
      title="Real-Time OLAP Engine"
      subtitle="Powered by Example 17: Analytical Processing (1M+ events/sec, < 100ms queries)"
      backendUrl="localhost:8017"
      backendInfo="RingBuffer + LRUCache + LZ4"
    >
      <StatsBar items={statsItems} />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Dimension Selection */}
        <div className="lg:col-span-1">
          <DataCard title="Select Dimensions">
            <div className="space-y-2">
              {dimensions.map((dim) => (
                <label
                  key={dim.name}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedDimensions.includes(dim.name)}
                    onChange={() => toggleDimension(dim.name)}
                    className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-neutral-900">{dim.name}</span>
                </label>
              ))}
            </div>

            <Button
              onClick={executeQuery}
              disabled={selectedDimensions.length === 0 || loading}
              fullWidth
              loading={loading}
              className="mt-4"
            >
              Execute Query
            </Button>
          </DataCard>
        </div>

        {/* Query Results */}
        <div className="lg:col-span-3">
          <DataCard
            title="Query Results"
            action={
              selectedDimensions.length > 0 && (
                <div className="flex gap-2">
                  {selectedDimensions.map((dim) => (
                    <Badge key={dim} variant="primary" size="sm">
                      {dim}
                    </Badge>
                  ))}
                </div>
              )
            }
          >
            {queryResults.length > 0 ? (
              <>
                <DataTable
                  columns={tableColumns}
                  data={queryResults.slice(0, 50)}
                  keyExtractor={(row, idx) => `row-${idx}`}
                />
                {queryResults.length > 50 && (
                  <div className="mt-4 text-sm text-neutral-600 text-center">
                    Showing 50 of {queryResults.length} results
                  </div>
                )}
              </>
            ) : (
              <EmptyState
                icon="chart"
                title="No results yet"
                description="Select dimensions and execute a query"
              />
            )}
          </DataCard>
        </div>
      </div>

      {/* Performance Info */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <DataCard variant="success">
          <div className="text-2xl font-bold text-success-700">1M+</div>
          <div className="text-sm text-success-900 mt-1">Events/sec Ingestion</div>
        </DataCard>
        <DataCard variant="primary">
          <div className="text-2xl font-bold text-primary-700">&lt; 100ms</div>
          <div className="text-sm text-primary-900 mt-1">Query Latency</div>
        </DataCard>
        <DataCard variant="warning">
          <div className="text-2xl font-bold text-amber-700">100+</div>
          <div className="text-sm text-amber-900 mt-1">Dimensions</div>
        </DataCard>
        <DataCard variant="info">
          <div className="text-2xl font-bold text-purple-700">Real-time</div>
          <div className="text-sm text-purple-900 mt-1">Drill-down/Roll-up</div>
        </DataCard>
      </div>
    </AppLayout>
  );
}
