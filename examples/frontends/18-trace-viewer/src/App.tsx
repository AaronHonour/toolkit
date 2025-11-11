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
import { Button, Badge } from '@unistax/atoms';
import { useDebounce } from '@unistax/performance';
import { AppLayout, StatsBar, DataCard, EmptyState } from '@unistax/layouts';

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

  const statsItems = [
    { label: 'Spans Ingested', value: stats.spans_ingested.toLocaleString() },
  ];

  if (trace) {
    statsItems.push(
      { label: 'Span Count', value: trace.span_count.toString() },
      { label: 'Total Duration', value: `${trace.total_duration.toFixed(2)}ms` }
    );
  }

  return (
    <AppLayout
      title="Distributed Tracing"
      subtitle="Powered by Example 18: Microservices Observability (1M+ spans/sec)"
      backendUrl="localhost:8018"
      backendInfo="RingBuffer + LRUCache + ConsistentHashRing"
    >
      <StatsBar items={statsItems} />

      {/* Trace Search */}
      <DataCard className="mb-6">
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
      </DataCard>

      {/* Trace Timeline */}
      {trace && (
        <div className="space-y-6">
          {/* Timeline Visualization */}
          <DataCard title="Trace Timeline">
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
          </DataCard>

          {/* Span Details */}
          {selectedSpan && (
            <DataCard title="Span Details">
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
            </DataCard>
          )}

          {/* Service Summary */}
          <DataCard title="Service Summary">
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
          </DataCard>
        </div>
      )}

      {/* Empty State */}
      {!trace && !loading && (
        <EmptyState
          icon="document"
          title="No trace loaded"
          description="Enter a trace ID to view trace details"
        />
      )}
    </AppLayout>
  );
}
