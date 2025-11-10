/**
 * Event Sourcing + CQRS
 * Example 7: Event Store (500K+ writes/sec)
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

interface Event { id: string; type: string; aggregate_id: string; timestamp: number; data: any; }
interface Stats { events_stored?: number; write_rate?: number; projections_updated?: number; }

const API_URL = 'http://localhost:8006';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, e] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/events?limit=20`)
        ]);
        setStats(await s.json());
        const eventsData = await e.json();
        setEvents(eventsData.events || []);
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
          <h1 className="text-2xl font-bold">📝 Event Sourcing + CQRS</h1>
          <p className="text-sm text-neutral-600">Event Store (500K+ writes/sec)</p>
        </div>
      </header>
      <div className="bg-primary-50 border-b"><div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
        <div><span className="font-semibold">Events:</span> <span className="ml-2">{stats.events_stored?.toLocaleString() || 0}</span></div>
        <div><span className="font-semibold">Write Rate:</span> <span className="ml-2 text-success-700">{stats.write_rate?.toLocaleString() || 0}/sec</span></div>
        <div><span className="font-semibold">Projections:</span> <span className="ml-2">{stats.projections_updated || 0}</span></div>
      </div></div>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6"><h2 className="text-lg font-semibold mb-4">Event Stream</h2>
          <div className="space-y-2">{events.map(e => (<div key={e.id} className="p-3 border-b">
            <div className="flex justify-between items-start"><div><div className="font-semibold text-sm">{e.type}</div>
            <div className="text-xs text-neutral-500">Aggregate: {e.aggregate_id}</div></div>
            <Badge variant="primary" size="sm">{new Date(e.timestamp * 1000).toLocaleTimeString()}</Badge></div>
          </div>))}</div>
        </div>
      </main>
    </div>
  );
}