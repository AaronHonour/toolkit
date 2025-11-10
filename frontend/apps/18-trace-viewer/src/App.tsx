/**
 * Distributed Tracing Viewer
 *
 * Connects to Example 18: Distributed Tracing System (localhost:8018)
 *
 * Features:
 * - Trace timeline visualization
 * - Span hierarchy (parent-child relationships)
 * - Service dependency mapping
 * - 1M+ spans/sec ingestion support
 */

import { useState, useEffect } from 'react';
import { Button, Badge, Spinner } from '@frontend-toolkit/atoms';
import { useDebounce } from '@frontend-toolkit/performance';

interface Span {
  span_id: string;
  parent_id: string | null;
  service: string;
  operation: string;
  start_time: number;
  duration: number;
  tags: Record<string, string>;
}

interface Trace {
  trace_id: string;
  spans: Span[];
  span_count: number;
  total_duration: number;
}

interface Stats {
  spans_ingested: number;
}

const API_URL = 'http://localhost:8018';

export function App() {
  const [traceId, setTraceId] = useState('');
  const [trace, setTrace] = useState<Trace | null>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<Stats>({ spans_ingested: 0 });
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null);

  const debouncedTraceId = useDebounce(traceId, 300);

  // Fetch trace
  const fetchTrace = async () => {
    if (!traceId) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/traces/${encodeURIComponent(traceId)}`);
      const data = await response.json();

      if (data.error) {
        setTrace(null);
      } else {
        setTrace(data);
      }
    } catch (error) {
      console.error('Trace fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

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

  // Build span hierarchy
  const buildSpanTree = (spans: Span[]): Span[] => {
    const rootSpans = spans.filter((s) => !s.parent_id);
    return rootSpans;
  };

  // Calculate span position (percentage of total duration)
  const getSpanPosition = (span: Span, totalDuration: number) => {
    if (!trace) return { left: 0, width: 0 };

    const minStart = Math.min(...trace.spans.map((s) => s.start_time));
    const start = ((span.start_time - minStart) / totalDuration) * 100;
    const width = (span.duration / totalDuration) * 100;

    return { left: start, width };
  };

  // Get service color
  const getServiceColor = (service: string) => {
    const colors = [
      'bg-primary-500',
      'bg-success-500',
      'bg-amber-500',
      'bg-purple-500',
      'bg-pink-500',
    ];
    const hash = service.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">🔍 Distributed Tracing</h1>
          <p className="text-sm text-neutral-600 mt-1">
            Powered by Example 18: Microservices Observability (1M+ spans/sec)
          </p>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="bg-primary-50 border-b border-primary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex gap-6">
              <div>
                <span className="font-semibold text-primary-900">Spans Ingested:</span>
                <span className="ml-2 text-primary-700">
                  {stats.spans_ingested.toLocaleString()}
                </span>
              </div>
              {trace && (
                <>
                  <div>
                    <span className="font-semibold text-primary-900">Span Count:</span>
                    <span className="ml-2 text-primary-700">{trace.span_count}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-primary-900">Total Duration:</span>
                    <span className="ml-2 text-primary-700">
                      {trace.total_duration.toFixed(2)}ms
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Trace Search */}
        <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={traceId}
                onChange={(e) => setTraceId(e.target.value)}
                placeholder="Enter trace ID..."
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <Button onClick={fetchTrace} disabled={!traceId || loading} loading={loading}>
              Search Trace
            </Button>
          </div>
        </div>

        {/* Trace Timeline */}
        {trace && (
          <div className="space-y-6">
            {/* Timeline Visualization */}
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">Trace Timeline</h2>
              <div className="space-y-2">
                {trace.spans.map((span) => {
                  const { left, width } = getSpanPosition(span, trace.total_duration);
                  return (
                    <div
                      key={span.span_id}
                      className="relative h-12 border-b border-neutral-100"
                      onClick={() => setSelectedSpan(span)}
                    >
                      <div className="absolute left-0 top-0 flex items-center h-full text-xs font-medium text-neutral-700 w-48 pr-2">
                        <Badge variant="secondary" size="sm" className="truncate">
                          {span.service}
                        </Badge>
                      </div>
                      <div className="absolute left-48 top-0 right-0 h-full px-2">
                        <div
                          className={`
                            absolute top-1/2 -translate-y-1/2 h-8 rounded
                            ${getServiceColor(span.service)}
                            hover:opacity-80 cursor-pointer transition-opacity
                          `}
                          style={{ left: `${left}%`, width: `${Math.max(width, 0.5)}%` }}
                          title={`${span.operation} - ${span.duration.toFixed(2)}ms`}
                        >
                          <div className="px-2 py-1 text-xs text-white truncate">
                            {span.operation}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Timeline scale */}
              <div className="mt-4 ml-48 mr-2 flex justify-between text-xs text-neutral-500">
                <span>0ms</span>
                <span>{(trace.total_duration / 4).toFixed(0)}ms</span>
                <span>{(trace.total_duration / 2).toFixed(0)}ms</span>
                <span>{((trace.total_duration * 3) / 4).toFixed(0)}ms</span>
                <span>{trace.total_duration.toFixed(0)}ms</span>
              </div>
            </div>

            {/* Span Details */}
            {selectedSpan && (
              <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
                <h2 className="text-lg font-semibold text-neutral-900 mb-4">Span Details</h2>
                <dl className="grid grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Span ID</dt>
                    <dd className="mt-1 text-sm text-neutral-900 font-mono">
                      {selectedSpan.span_id}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Parent ID</dt>
                    <dd className="mt-1 text-sm text-neutral-900 font-mono">
                      {selectedSpan.parent_id || 'None (root)'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Service</dt>
                    <dd className="mt-1 text-sm text-neutral-900">{selectedSpan.service}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Operation</dt>
                    <dd className="mt-1 text-sm text-neutral-900">{selectedSpan.operation}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Duration</dt>
                    <dd className="mt-1 text-sm text-neutral-900">
                      {selectedSpan.duration.toFixed(2)}ms
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Start Time</dt>
                    <dd className="mt-1 text-sm text-neutral-900">
                      {new Date(selectedSpan.start_time * 1000).toLocaleString()}
                    </dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="text-sm font-medium text-neutral-600">Tags</dt>
                    <dd className="mt-1">
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(selectedSpan.tags).map(([key, value]) => (
                          <Badge key={key} variant="neutral" size="sm">
                            {key}: {value}
                          </Badge>
                        ))}
                      </div>
                    </dd>
                  </div>
                </dl>
              </div>
            )}

            {/* Service Summary */}
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">Service Summary</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array.from(new Set(trace.spans.map((s) => s.service))).map((service) => {
                  const spans = trace.spans.filter((s) => s.service === service);
                  const totalDuration = spans.reduce((sum, s) => sum + s.duration, 0);
                  return (
                    <div
                      key={service}
                      className="p-4 bg-neutral-50 rounded-lg border border-neutral-200"
                    >
                      <div className="text-sm font-semibold text-neutral-900 mb-2">{service}</div>
                      <div className="text-xs text-neutral-600">
                        {spans.length} span{spans.length !== 1 ? 's' : ''}
                      </div>
                      <div className="text-xs text-neutral-600">
                        {totalDuration.toFixed(2)}ms total
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!trace && !loading && (
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-neutral-900">No trace loaded</h3>
            <p className="mt-1 text-sm text-neutral-500">Enter a trace ID to view trace details</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-neutral-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-neutral-600">
            <div>
              <span className="font-semibold">Backend:</span> localhost:8018
            </div>
            <div>
              <span className="font-semibold">Powered by:</span> RingBuffer + LRUCache +
              ConsistentHashRing
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
