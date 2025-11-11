/**
 * Real-Time Analytics Dashboard
 * Example 2: Event Processing (1M+ events/sec)
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Badge } from '@unistax/atoms';
import { AppLayout, StatsBar, DataCard } from '@unistax/layouts';

interface Event { event_type: string; user_id: string; timestamp: number; properties: any; }
interface Stats { events_ingested?: number; events_per_sec?: number; unique_users?: number; }

const API_URL = 'http://localhost:8002';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [events, setEvents] = useState<Event[]>([]);
  const [eventTypes, setEventTypes] = useState<{type: string; count: number}[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, e, t] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/events/recent?limit=20`),
          fetch(`${API_URL}/api/v1/analytics/events/count?group_by=event_type`)
        ]);
        setStats(await s.json());
        const eventsData = await e.json();
        setEvents(eventsData.events || []);
        const typesData = await t.json();
        setEventTypes(typesData.event_types || []);
      } catch (error) { console.error('Error:', error); }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const statsData = [
    { label: 'Events Ingested', value: stats.events_ingested?.toLocaleString() || '0' },
    { label: 'Rate', value: `${stats.events_per_sec?.toLocaleString() || 0}/sec`, variant: 'success' as const },
    { label: 'Unique Users', value: stats.unique_users?.toLocaleString() || '0' },
  ];

  return (
    <AppLayout
      title="Real-Time Analytics"
      description="Live Event Processing (1M+ events/sec)"
      icon="📊"
    >
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-neutral-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Event Types</h2>
          <div className="space-y-2">
            {eventTypes.map(t => (
              <div key={t.type} className="flex justify-between items-center p-2 bg-neutral-50 rounded">
                <span className="font-medium">{t.type}</span>
                <Badge variant="primary">{t.count.toLocaleString()}</Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-neutral-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Events</h2>
          <div className="space-y-2">
            {events.slice(0, 10).map((e, i) => (
              <div key={i} className="text-xs p-2 border-b border-neutral-100">
                <div className="font-semibold text-neutral-900">{e.event_type}</div>
                <div className="text-neutral-500">User: {e.user_id}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
