/**
 * Time-Series Database Dashboard
 * Example 8: Metrics Storage (1M+ points/sec)
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

interface Metric { name: string; value: number; timestamp: number; tags: Record<string, string>; }
interface Stats { datapoints_ingested?: number; ingestion_rate?: number; compression_ratio?: number; }

const API_URL = 'http://localhost:8007';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [metrics, setMetrics] = useState<Metric[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, m] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/metrics/recent?limit=20`)
        ]);
        setStats(await s.json());
        const metricsData = await m.json();
        setMetrics(metricsData.metrics || []);
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
          <h1 className="text-2xl font-bold">📈 Time-Series Database</h1>
          <p className="text-sm text-neutral-600">Metrics Storage (1M+ points/sec)</p>
        </div>
      </header>
      <div className="bg-primary-50 border-b"><div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
        <div><span className="font-semibold">Datapoints:</span> <span className="ml-2">{stats.datapoints_ingested?.toLocaleString() || 0}</span></div>
        <div><span className="font-semibold">Rate:</span> <span className="ml-2 text-success-700">{stats.ingestion_rate?.toLocaleString() || 0}/sec</span></div>
        <div><span className="font-semibold">Compression:</span> <span className="ml-2">{stats.compression_ratio?.toFixed(1) || 0}:1</span></div>
      </div></div>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6"><h2 className="text-lg font-semibold mb-4">Recent Metrics</h2>
          <div className="space-y-2">{metrics.map((m, i) => (<div key={i} className="p-3 border-b flex justify-between">
            <div><div className="font-semibold text-sm">{m.name}</div>
            <div className="text-xs text-neutral-500">{Object.entries(m.tags).map(([k,v]) => `${k}=${v}`).join(', ')}</div></div>
            <div className="text-right"><div className="font-bold">{m.value.toFixed(2)}</div>
            <div className="text-xs text-neutral-500">{new Date(m.timestamp * 1000).toLocaleTimeString()}</div></div>
          </div>))}</div>
        </div>
      </main>
    </div>
  );
}