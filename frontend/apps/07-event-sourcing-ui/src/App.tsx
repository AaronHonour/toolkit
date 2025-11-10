/**
 * Event Sourcing + CQRS
 * Example 7: Event Store (500K+ writes/sec)
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

interface Event {
  id: string;
  type: string;
  aggregate_id: string;
  timestamp: number;
  data: any;
}

interface Stats {
  events_stored?: number;
  write_rate?: number;
  projections_updated?: number;
}

const API_URL = 'http://localhost:8006';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, e] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/events?limit=20`),
        ]);
        setStats(await s.json());
        const eventsData = await e.json();
        setEvents(eventsData.events || []);
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
      label: 'Events Stored',
      value: stats.events_stored?.toLocaleString() || '0',
    },
    {
      label: 'Write Rate',
      value: `${stats.write_rate?.toLocaleString() || 0}/sec`,
      variant: 'success' as const,
    },
    {
      label: 'Projections Updated',
      value: (stats.projections_updated || 0).toString(),
    },
  ];

  // DataTable columns
  const columns = [
    {
      key: 'type' as const,
      label: 'Event Type',
      render: (event: Event) => (
        <div>
          <div className="font-semibold text-sm text-neutral-900">{event.type}</div>
          <div className="text-xs text-neutral-500">ID: {event.id}</div>
        </div>
      ),
    },
    {
      key: 'aggregate_id' as const,
      label: 'Aggregate',
      render: (event: Event) => (
        <div className="font-mono text-sm text-neutral-600">{event.aggregate_id}</div>
      ),
    },
    {
      key: 'timestamp' as const,
      label: 'Timestamp',
      render: (event: Event) => (
        <Badge variant="primary" size="sm">
          {new Date(event.timestamp * 1000).toLocaleTimeString()}
        </Badge>
      ),
    },
  ];

  return (
    <AppLayout
      title="Event Sourcing + CQRS"
      description="Event Store (500K+ writes/sec)"
      icon="📝"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8006
          </div>
          <div>
            <span className="font-semibold">Pattern:</span> Event Sourcing with CQRS
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
        <LoadingState message="Loading event stream..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <DataCard
            title="Event Store"
            subtitle="Append-only event log"
            badge={{
              label: 'Active',
              variant: 'success',
            }}
            metadata={[
              { label: 'Backend', value: 'localhost:8006' },
              { label: 'Protocol', value: 'HTTP/REST' },
            ]}
          >
            <div className="space-y-3">
              <div className="p-3 bg-neutral-50 rounded">
                <div className="text-xs text-neutral-600">Total Events</div>
                <div className="text-xl font-bold text-neutral-900">
                  {stats.events_stored?.toLocaleString() || '0'}
                </div>
              </div>
              <div className="text-xs text-neutral-600">
                All events are immutably stored in append-only log
              </div>
            </div>
          </DataCard>

          <DataCard
            title="Write Performance"
            subtitle="Event ingestion rate"
            badge={{
              label: stats.write_rate && stats.write_rate > 400000 ? 'Excellent' : 'Good',
              variant: stats.write_rate && stats.write_rate > 400000 ? 'success' : 'warning',
            }}
          >
            <div className="space-y-3">
              <div className="p-3 bg-success-50 rounded border border-success-200">
                <div className="text-xs text-success-700">Current Rate</div>
                <div className="text-xl font-bold text-success-900">
                  {stats.write_rate ? `${(stats.write_rate / 1000).toFixed(1)}K` : '0'}
                </div>
                <div className="text-xs text-success-600">events/sec</div>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
                High-throughput event ingestion
              </div>
            </div>
          </DataCard>

          <DataCard
            title="CQRS Projections"
            subtitle="Read model updates"
            badge={{
              label: 'Synced',
              variant: 'primary',
            }}
          >
            <div className="space-y-3">
              <div className="p-3 bg-primary-50 rounded border border-primary-200">
                <div className="text-xs text-primary-700">Projections</div>
                <div className="text-xl font-bold text-primary-900">
                  {stats.projections_updated || 0}
                </div>
                <div className="text-xs text-primary-600">materialized views</div>
              </div>
              <div className="text-xs text-neutral-600">
                Read models automatically updated from event stream
              </div>
            </div>
          </DataCard>
        </div>
      )}

      {/* Event Stream Table */}
      <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-neutral-900">Event Stream</h2>
          <p className="text-sm text-neutral-600">Recent events from the event store</p>
        </div>
        {loading ? (
          <LoadingState message="Loading events..." />
        ) : events.length > 0 ? (
          <DataTable data={events} columns={columns} />
        ) : (
          <EmptyState
            icon="📝"
            title="No events yet"
            description="Events will appear here as they are stored in the event log."
          />
        )}
      </div>
    </AppLayout>
  );
}
