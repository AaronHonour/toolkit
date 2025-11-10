/**
 * Kappa Architecture Monitor
 * Example 6: Stream Processing (500K+ events/sec)
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

interface StreamStats { events_processed?: number; processing_rate?: number; lag?: number; views_materialized?: number; }

const API_URL = 'http://localhost:8005';

export function App() {
  const [stats, setStats] = useState<StreamStats>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/stats`);
        setStats(await res.json());
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
          <h1 className="text-2xl font-bold">🌊 Kappa Architecture</h1>
          <p className="text-sm text-neutral-600">Pure Stream Processing (500K+ events/sec)</p>
        </div>
      </header>
      <div className="bg-primary-50 border-b"><div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
        <div><span className="font-semibold">Events:</span> <span className="ml-2">{stats.events_processed?.toLocaleString() || 0}</span></div>
        <div><span className="font-semibold">Rate:</span> <span className="ml-2 text-success-700">{stats.processing_rate?.toLocaleString() || 0}/sec</span></div>
        <div><span className="font-semibold">Lag:</span> <span className="ml-2">{stats.lag || 0}ms</span></div>
        <div><span className="font-semibold">Views:</span> <span className="ml-2">{stats.views_materialized || 0}</span></div>
      </div></div>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6 text-center py-12">
          <h2 className="text-lg font-semibold mb-2">Stream Processing Active</h2>
          <p className="text-neutral-600">Real-time event processing pipeline running</p>
        </div>
      </main>
    </div>
  );
}