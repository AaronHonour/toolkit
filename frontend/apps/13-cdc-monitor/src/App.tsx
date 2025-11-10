/**
 * CDC Pipeline Monitor - Example 13 (localhost:8013)
 * Change Data Capture with 100K+ changes/sec, < 50ms latency
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';

const API_URL = 'http://localhost:8013';

export function App() {
  const [stats, setStats] = useState<any>(null);
  const [changes, setChanges] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, changesRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/changes?limit=20`)
        ]);
        setStats(await statsRes.json());
        const changesData = await changesRes.json();
        setChanges(changesData.changes || []);
      } catch (error) {
        console.error('Error:', error);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">📊 CDC Pipeline Monitor</h1>
          <p className="text-sm text-neutral-600">Example 13: Change Data Capture (100K+ changes/sec)</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {stats && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border">
              <div className="text-2xl font-bold text-primary-700">{stats.changes_captured?.toLocaleString() || 0}</div>
              <div className="text-sm text-neutral-600">Changes Captured</div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="text-2xl font-bold text-success-700">{stats.changes_per_sec?.toLocaleString() || 0}/sec</div>
              <div className="text-sm text-neutral-600">Capture Rate</div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="text-2xl font-bold text-amber-700">{stats.latency_ms?.toFixed(1) || 0}ms</div>
              <div className="text-sm text-neutral-600">End-to-End Latency</div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="text-2xl font-bold text-purple-700">{((stats.dedup_rate || 0) * 100).toFixed(1)}%</div>
              <div className="text-sm text-neutral-600">Dedup Rate</div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Changes</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200">
              <thead className="bg-neutral-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase">Operation</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase">Table</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase">Key</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-700 uppercase">Timestamp</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-neutral-200">
                {changes.map((change, idx) => (
                  <tr key={idx}>
                    <td className="px-4 py-3">
                      <Badge variant={change.operation === 'INSERT' ? 'success' : change.operation === 'UPDATE' ? 'warning' : 'error'}>
                        {change.operation}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-900">{change.table}</td>
                    <td className="px-4 py-3 text-sm font-mono text-neutral-700">{change.key}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600">{new Date(change.timestamp * 1000).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
