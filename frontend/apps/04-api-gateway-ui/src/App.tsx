/**
 * API Gateway Dashboard
 * Example 4: Service Routing (50K+ req/sec)
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

interface Service { name: string; url: string; healthy: boolean; latency: number; requests: number; }
interface Stats { total_requests?: number; avg_latency?: number; circuit_breaks?: number; }

const API_URL = 'http://localhost:8003';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [services, setServices] = useState<Service[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, svc] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/services`)
        ]);
        setStats(await s.json());
        const svcData = await svc.json();
        setServices(svcData.services || []);
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
          <h1 className="text-2xl font-bold">🚪 API Gateway</h1>
          <p className="text-sm text-neutral-600">Service Routing (50K+ req/sec)</p>
        </div>
      </header>
      <div className="bg-primary-50 border-b"><div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
        <div><span className="font-semibold">Requests:</span> <span className="ml-2">{stats.total_requests?.toLocaleString() || 0}</span></div>
        <div><span className="font-semibold">Avg Latency:</span> <span className="ml-2 text-success-700">{stats.avg_latency?.toFixed(2) || 0}ms</span></div>
        <div><span className="font-semibold">Circuit Breaks:</span> <span className="ml-2 text-error-700">{stats.circuit_breaks || 0}</span></div>
      </div></div>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6"><h2 className="text-lg font-semibold mb-4">Registered Services</h2>
          <div className="space-y-3">{services.map(s => (<div key={s.name} className="p-4 border rounded-lg flex justify-between items-center">
            <div><div className="font-semibold">{s.name}</div><div className="text-xs text-neutral-500">{s.url}</div></div>
            <div className="flex items-center gap-3">
              <div className="text-sm">{s.requests.toLocaleString()} req</div>
              <div className="text-sm">{s.latency.toFixed(1)}ms</div>
              <Badge variant={s.healthy ? 'success' : 'error'}>{s.healthy ? 'Healthy' : 'Down'}</Badge>
            </div></div>))}</div>
        </div>
      </main>
    </div>
  );
}