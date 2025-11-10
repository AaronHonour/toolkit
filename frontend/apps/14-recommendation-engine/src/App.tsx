/**
 * Recommendation Engine UI - Example 14 (localhost:8014)
 * ML-powered recommendations with < 10ms P99 latency, 100K+ recs/sec
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';
import {
  AppLayout,
  StatsBar,
  DataCard,
  EmptyState,
} from '@frontend-toolkit/layouts';

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

  // Convert stats to StatsBar format
  const statsData = stats
    ? [
        {
          label: 'Total Recommendations',
          value: stats.recommendations_served?.toLocaleString() || '0',
        },
        {
          label: 'Rate',
          value: `${stats.recs_per_sec?.toLocaleString() || 0}/sec`,
          variant: 'success' as const,
        },
        ...(latency > 0
          ? [
              {
                label: 'Last Latency',
                value: `${latency.toFixed(2)}ms`,
                variant: (latency < 10 ? 'success' : 'warning') as const,
              },
            ]
          : []),
      ]
    : [];

  return (
    <AppLayout
      title="Recommendation Engine"
      description="ML Recommendations (< 10ms P99, 100K+ recs/sec)"
      icon="🎯"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8014
          </div>
          <div>
            <span className="font-semibold">Powered by:</span> LRUCache + fast_hash
          </div>
        </div>
      }
    >
      {/* Stats Bar */}
      {stats && (
        <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
          <StatsBar stats={statsData} variant="compact" />
        </div>
      )}

      {/* Query Interface */}
      <DataCard
        title="Get Recommendations"
        subtitle="Enter a user ID to get personalized recommendations"
        className="mb-6"
      >
        <div className="flex gap-4">
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter user ID..."
            className="flex-1 px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            onKeyPress={(e) => e.key === 'Enter' && getRecommendations()}
          />
          <Button onClick={getRecommendations} disabled={!userId || loading} loading={loading}>
            Get Recommendations
          </Button>
        </div>
      </DataCard>

      {/* Recommendations Grid */}
      {recommendations.length > 0 ? (
        <DataCard
          title={`Recommended for ${userId}`}
          subtitle={`${recommendations.length} personalized recommendations`}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((rec) => (
              <div
                key={rec.item_id}
                className="p-4 border border-neutral-200 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="font-semibold text-neutral-900">{rec.item_id}</div>
                  <Badge variant="primary" size="sm">
                    {rec.score.toFixed(3)}
                  </Badge>
                </div>
                <div className="text-sm text-neutral-600">
                  {rec.reason || 'Based on your preferences'}
                </div>
                {rec.features && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {Object.entries(rec.features)
                      .slice(0, 3)
                      .map(([key, value]: [string, any]) => (
                        <span
                          key={key}
                          className="px-2 py-0.5 text-xs bg-neutral-100 rounded"
                        >
                          {key}
                        </span>
                      ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </DataCard>
      ) : (
        !loading && (
          <EmptyState
            icon={
              <svg
                className="mx-auto h-12 w-12 text-neutral-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            }
            title="No recommendations yet"
            message="Enter a user ID and click 'Get Recommendations' to see personalized results"
          />
        )
      )}

      {/* Performance Info */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
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
    </AppLayout>
  );
}
