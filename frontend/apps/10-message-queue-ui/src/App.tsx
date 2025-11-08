/**
 * Message Queue Dashboard
 * Example 10: Message Broker (500K+ msgs/sec)
 */
import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';

interface Queue { name: string; size: number; consumers: number; rate: number; }
interface Stats { messages_total?: number; messages_per_sec?: number; active_queues?: number; }

const API_URL = 'http://localhost:8009';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [queues, setQueues] = useState<Queue[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, q] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/queues`)
        ]);
        setStats(await s.json());
        const queueData = await q.json();
        setQueues(queueData.queues || []);
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
          <h1 className="text-2xl font-bold">📮 Message Queue</h1>
          <p className="text-sm text-neutral-600">Message Broker (500K+ msgs/sec)</p>
        </div>
      </header>
      <div className="bg-primary-50 border-b"><div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
        <div><span className="font-semibold">Messages:</span> <span className="ml-2">{stats.messages_total?.toLocaleString() || 0}</span></div>
        <div><span className="font-semibold">Rate:</span> <span className="ml-2 text-success-700">{stats.messages_per_sec?.toLocaleString() || 0}/sec</span></div>
        <div><span className="font-semibold">Queues:</span> <span className="ml-2">{stats.active_queues || 0}</span></div>
      </div></div>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6"><h2 className="text-lg font-semibold mb-4">Active Queues</h2>
          <div className="space-y-3">{queues.map(q => (<div key={q.name} className="p-4 border rounded-lg">
            <div className="flex justify-between items-center"><div><div className="font-semibold">{q.name}</div>
            <div className="text-xs text-neutral-500">{q.consumers} consumer(s)</div></div>
            <div className="text-right"><Badge variant={q.size > 1000 ? 'warning' : 'success'}>{q.size} msgs</Badge>
            <div className="text-xs text-neutral-500 mt-1">{q.rate.toLocaleString()}/sec</div></div></div>
          </div>))}</div>
        </div>
      </main>
    </div>
  );
}