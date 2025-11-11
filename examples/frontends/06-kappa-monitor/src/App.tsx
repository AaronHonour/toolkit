/**
 * Kappa Architecture Monitor
 * Example 6: Stream Processing (500K+ events/sec)
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Badge } from '@unistax/atoms';
import {
  AppLayout,
  StatsBar,
  LoadingState,
  EmptyState,
  DataCard,
} from '@unistax/layouts';

interface StreamStats {
  events_processed?: number;
  processing_rate?: number;
  lag?: number;
  views_materialized?: number;
}

const API_URL = 'http://localhost:8006';

export function App() {
  const [stats, setStats] = useState<StreamStats>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/stats`);
        setStats(await res.json());
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
      label: 'Events Processed',
      value: stats.events_processed?.toLocaleString() || '0',
    },
    {
      label: 'Processing Rate',
      value: `${stats.processing_rate?.toLocaleString() || 0}/sec`,
      variant: 'success' as const,
    },
    {
      label: 'Lag',
      value: `${stats.lag || 0}ms`,
      variant: stats.lag && stats.lag > 100 ? ('danger' as const) : ('success' as const),
    },
    {
      label: 'Views Materialized',
      value: (stats.views_materialized || 0).toString(),
    },
  ];

  return (
    <AppLayout
      title="Kappa Architecture"
      description="Pure Stream Processing (500K+ events/sec)"
      icon="🌊"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8005
          </div>
          <div>
            <span className="font-semibold">Architecture:</span> Stream-first processing
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
        <LoadingState message="Connecting to stream processor..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DataCard
            title="Stream Processing Status"
            subtitle="Real-time event processing"
            badge={{
              label: 'Active',
              variant: 'success',
            }}
            metadata={[
              { label: 'Backend', value: 'localhost:8005' },
              { label: 'Protocol', value: 'HTTP/REST' },
            ]}
          >
            <div className="space-y-3">
              <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
                <div className="text-sm font-semibold text-primary-900 mb-2">
                  Event Processing Pipeline
                </div>
                <div className="text-xs text-primary-700">
                  Pure stream processing architecture with materialized views
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
                Processing events in real-time
              </div>
            </div>
          </DataCard>

          <DataCard
            title="Performance Metrics"
            subtitle="System performance overview"
            badge={{
              label: stats.processing_rate && stats.processing_rate > 400000 ? 'Excellent' : 'Good',
              variant: stats.processing_rate && stats.processing_rate > 400000 ? 'success' : 'warning',
            }}
          >
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-neutral-50 rounded">
                  <div className="text-xs text-neutral-600">Throughput</div>
                  <div className="text-lg font-bold text-neutral-900">
                    {stats.processing_rate ? `${(stats.processing_rate / 1000).toFixed(1)}K` : '0'}
                  </div>
                  <div className="text-xs text-neutral-500">events/sec</div>
                </div>
                <div className="p-3 bg-neutral-50 rounded">
                  <div className="text-xs text-neutral-600">Latency</div>
                  <div className="text-lg font-bold text-neutral-900">{stats.lag || 0}</div>
                  <div className="text-xs text-neutral-500">milliseconds</div>
                </div>
              </div>
              <div className="text-xs text-neutral-600">
                {stats.events_processed
                  ? `${stats.events_processed.toLocaleString()} total events processed`
                  : 'No events processed yet'}
              </div>
            </div>
          </DataCard>
        </div>
      )}
    </AppLayout>
  );
}
