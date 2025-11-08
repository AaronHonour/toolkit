/**
 * File Processing UI - Example 3: File Processing (10K+ files/min)
 * High-throughput file pipeline
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

const API_URL = 'http://localhost:8002';

export function App() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/stats`);
        const data = await response.json();
        setStats(data);
        setLoading(false);
      } catch (error) {
        console.error('Stats error:', error);
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">File Processing</h1>
          <p className="text-sm text-neutral-600">Example 3: File Processing (10K+ files/min)</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="mt-2 text-sm text-neutral-600">Loading...</p>
          </div>
        ) : stats ? (
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">System Statistics</h2>
            <pre className="text-xs bg-neutral-50 p-4 rounded overflow-auto">
              {JSON.stringify(stats, null, 2)}
            </pre>
          </div>
        ) : (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <p className="text-sm text-amber-900">
              Unable to connect to backend at {API_URL}. Make sure the backend service is running.
            </p>
          </div>
        )}
      </main>

      <footer className="mt-12 border-t bg-white">
        <div className="max-w-7xl mx-auto px-4 py-6 text-sm text-neutral-600">
          <span className="font-semibold">Backend:</span> localhost:8002
        </div>
      </footer>
    </div>
  );
}
