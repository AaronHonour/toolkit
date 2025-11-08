/**
 * Real-Time Analytics Dashboard  
 * Example 2: Event Processing (1M+ events/sec)
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

interface Event { event_type: string; user_id: string; timestamp: number; properties: any; }
interface Stats { events_ingested?: number; events_per_sec?: number; unique_users?: number; }

const API_URL = 'http://localhost:8001';

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

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">📊 Real-Time Analytics</h1>
          <p className="text-sm text-neutral-600">Live Event Processing (1M+ events/sec)</p>
        </div>
      </header>
      <div className="bg-primary-50 border-b"><div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
        <div><span className="font-semibold">Events Ingested:</span> <span className="ml-2 text-primary-700">{stats.events_ingested?.toLocaleString() || 0}</span></div>
        <div><span className="font-semibold">Rate:</span> <span className="ml-2 text-success-700">{stats.events_per_sec?.toLocaleString() || 0}/sec</span></div>
        <div><span className="font-semibold">Users:</span> <span className="ml-2 text-primary-700">{stats.unique_users?.toLocaleString() || 0}</span></div>
      </div></div>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg border p-6"><h2 className="text-lg font-semibold mb-4">Event Types</h2>
            <div className="space-y-2">{eventTypes.map(t => (<div key={t.type} className="flex justify-between items-center p-2 bg-neutral-50 rounded">
              <span>{t.type}</span><Badge variant="primary">{t.count.toLocaleString()}</Badge></div>))}</div>
          </div>
          <div className="bg-white rounded-lg border p-6"><h2 className="text-lg font-semibold mb-4">Recent Events</h2>
            <div className="space-y-2">{events.slice(0, 10).map((e, i) => (<div key={i} className="text-xs p-2 border-b">
              <div className="font-semibold">{e.event_type}</div><div className="text-neutral-500">User: {e.user_id}</div></div>))}</div>
          </div>
        </div>
      </main>
    </div>
  );
}