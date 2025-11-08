/**
 * Recommendation Engine UI - Example 14 (localhost:8014)
 * ML-powered recommendations with < 10ms P99 latency, 100K+ recs/sec
 */
import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';

const API_URL = 'http://localhost:8014';

export function App() {
  const [userId, setUserId] = useState('user_1');
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [latency, setLatency] = useState<number>(0);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/stats`);
        setStats(await response.json());
      } catch (error) {
        console.error('Stats error:', error);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  const getRecommendations = async () => {
    setLoading(true);
    const start = performance.now();
    try {
      const response = await fetch(`${API_URL}/api/v1/recommend?user_id=${userId}&limit=10`);
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setLatency(performance.now() - start);
    } catch (error) {
      console.error('Recommendation error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">🎯 Recommendation Engine</h1>
          <p className="text-sm text-neutral-600">Example 14: ML Recommendations (< 10ms P99, 100K+ recs/sec)</p>
        </div>
      </header>

      {stats && (
        <div className="bg-primary-50 border-b">
          <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
            <div><span className="font-semibold">Total Recommendations:</span> {stats.recommendations_served?.toLocaleString() || 0}</div>
            <div><span className="font-semibold">Rate:</span> {stats.recs_per_sec?.toLocaleString() || 0}/sec</div>
            {latency > 0 && (
              <div><span className="font-semibold">Last Latency:</span> <span className={latency < 10 ? 'text-success-700' : 'text-amber-700'}>{latency.toFixed(2)}ms</span></div>
            )}
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter user ID..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <Button onClick={getRecommendations} disabled={!userId || loading} loading={loading}>
              Get Recommendations
            </Button>
          </div>
        </div>

        {recommendations.length > 0 && (
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">Recommended for {userId}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendations.map((rec) => (
                <div key={rec.item_id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-semibold text-neutral-900">{rec.item_id}</div>
                    <Badge variant="primary" size="sm">{rec.score.toFixed(3)}</Badge>
                  </div>
                  <div className="text-sm text-neutral-600">
                    {rec.reason || 'Based on your preferences'}
                  </div>
                  {rec.features && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {Object.entries(rec.features).slice(0, 3).map(([key, value]: [string, any]) => (
                        <span key={key} className="px-2 py-0.5 text-xs bg-neutral-100 rounded">{key}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 grid grid-cols-4 gap-4">
          <div className="bg-success-50 p-4 rounded-lg border border-success-200">
            <div className="text-2xl font-bold text-success-700">100K+</div>
            <div className="text-sm text-success-900">Recs/sec</div>
          </div>
          <div className="bg-primary-50 p-4 rounded-lg border border-primary-200">
            <div className="text-2xl font-bold text-primary-700">&lt; 10ms</div>
            <div className="text-sm text-primary-900">P99 Latency</div>
          </div>
          <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
            <div className="text-2xl font-bold text-amber-700">326K+</div>
            <div className="text-sm text-amber-900">LRUCache ops/sec</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="text-2xl font-bold text-purple-700">886K+</div>
            <div className="text-sm text-purple-900">fast_hash ops/sec</div>
          </div>
        </div>
      </main>
    </div>
  );
}
