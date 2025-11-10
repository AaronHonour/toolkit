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
import { Button, Badge } from '@frontend-toolkit/atoms';

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

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">📊 Real-Time OLAP Engine</h1>
          <p className="text-sm text-neutral-600 mt-1">
            Powered by Example 17: Analytical Processing (1M+ events/sec, &lt; 100ms queries)
          </p>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="bg-primary-50 border-b border-primary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex gap-6">
              <div>
                <span className="font-semibold text-primary-900">Events Ingested:</span>
                <span className="ml-2 text-primary-700">
                  {stats.events_ingested.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="font-semibold text-primary-900">Ingestion Rate:</span>
                <span className="ml-2 text-success-700">
                  {stats.ingestion_rate.toLocaleString()}/sec
                </span>
              </div>
              <div>
                <span className="font-semibold text-primary-900">Dimensions:</span>
                <span className="ml-2 text-primary-700">{stats.dimensions}</span>
              </div>
              {queryLatency > 0 && (
                <div>
                  <span className="font-semibold text-primary-900">Last Query:</span>
                  <span
                    className={`ml-2 ${queryLatency < 100 ? 'text-success-700' : 'text-amber-700'}`}
                  >
                    {queryLatency.toFixed(2)}ms
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Dimension Selection */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">Select Dimensions</h2>
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
            </div>
          </div>

          {/* Query Results */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-neutral-900">Query Results</h2>
                {selectedDimensions.length > 0 && (
                  <div className="flex gap-2">
                    {selectedDimensions.map((dim) => (
                      <Badge key={dim} variant="primary" size="sm">
                        {dim}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              {queryResults.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-neutral-200">
                    <thead className="bg-neutral-50">
                      <tr>
                        {selectedDimensions.map((dim) => (
                          <th
                            key={dim}
                            className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wider"
                          >
                            {dim}
                          </th>
                        ))}
                        <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wider">
                          Count
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wider">
                          Sum
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wider">
                          Avg
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-neutral-200">
                      {queryResults.slice(0, 50).map((result, idx) => (
                        <tr key={idx} className="hover:bg-neutral-50">
                          {selectedDimensions.map((dim) => (
                            <td key={dim} className="px-4 py-3 text-sm text-neutral-900">
                              {result.dimensions[dim] || '-'}
                            </td>
                          ))}
                          <td className="px-4 py-3 text-sm font-medium text-neutral-900">
                            {result.count.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-sm text-neutral-700">
                            {result.metrics.sum?.toFixed(2) || '-'}
                          </td>
                          <td className="px-4 py-3 text-sm text-neutral-700">
                            {result.metrics.avg?.toFixed(2) || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {queryResults.length > 50 && (
                    <div className="mt-4 text-sm text-neutral-600 text-center">
                      Showing 50 of {queryResults.length} results
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <svg
                    className="mx-auto h-12 w-12 text-neutral-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-neutral-900">
                    No results yet
                  </h3>
                  <p className="mt-1 text-sm text-neutral-500">
                    Select dimensions and execute a query
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Performance Info */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">OLAP Engine Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-success-50 rounded-lg border border-success-200">
              <div className="text-2xl font-bold text-success-700">1M+</div>
              <div className="text-sm text-success-900 mt-1">Events/sec Ingestion</div>
            </div>
            <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
              <div className="text-2xl font-bold text-primary-700">&lt; 100ms</div>
              <div className="text-sm text-primary-900 mt-1">Query Latency</div>
            </div>
            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
              <div className="text-2xl font-bold text-amber-700">100+</div>
              <div className="text-sm text-amber-900 mt-1">Dimensions</div>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="text-2xl font-bold text-purple-700">Real-time</div>
              <div className="text-sm text-purple-900 mt-1">Drill-down/Roll-up</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-neutral-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-neutral-600">
            <div>
              <span className="font-semibold">Backend:</span> localhost:8017
            </div>
            <div>
              <span className="font-semibold">Powered by:</span> RingBuffer + LRUCache + LZ4
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
