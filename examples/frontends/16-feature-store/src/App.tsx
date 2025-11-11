/**
 * Feature Store UI
 *
 * Connects to Example 16: Feature Store (localhost:8016)
 *
 * Features:
 * - Real-time feature lookup (< 1ms P99)
 * - Feature versioning and history
 * - Batch retrieval
 * - Performance monitoring (500K+ lookups/sec)
 */

import { useState, useEffect } from 'react';
import { Button } from '@unistax/atoms';
import { useDebounce } from '@unistax/performance';
import { AppLayout, StatsBar, DataCard } from '@unistax/layouts';

interface Feature {
  feature_id: string;
  value: any;
  version: number;
  timestamp: number;
}

interface FeatureGroup {
  name: string;
  features: string[];
}

const API_URL = 'http://localhost:8016';

export function App() {
  const [featureId, setFeatureId] = useState('');
  const [entityId, setEntityId] = useState('');
  const [feature, setFeature] = useState<Feature | null>(null);
  const [featureGroups, setFeatureGroups] = useState<FeatureGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ lookups: 0, cache_hits: 0, cache_hit_rate: 0 });
  const [latency, setLatency] = useState<number>(0);

  const debouncedFeatureId = useDebounce(featureId, 300);

  // Fetch feature
  const fetchFeature = async () => {
    if (!featureId || !entityId) return;

    setLoading(true);
    const start = performance.now();

    try {
      const response = await fetch(
        `${API_URL}/api/v1/features/${featureId}?entity_id=${encodeURIComponent(entityId)}`
      );
      const data = await response.json();
      const end = performance.now();

      setFeature(data);
      setLatency(end - start);
    } catch (error) {
      console.error('Feature lookup error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Stats error:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch feature groups
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/feature-groups`);
        const data = await response.json();
        setFeatureGroups(data.groups || []);
      } catch (error) {
        console.error('Feature groups error:', error);
      }
    };

    fetchGroups();
  }, []);

  const statsItems = [
    { label: 'Lookups', value: stats.lookups.toLocaleString() },
    {
      label: 'Cache Hit Rate',
      value: `${(stats.cache_hit_rate * 100).toFixed(1)}%`,
    },
  ];

  if (latency > 0) {
    statsItems.push({
      label: 'Last Latency',
      value: `${latency.toFixed(2)}ms`,
      variant: latency < 1 ? 'success' : latency < 5 ? 'warning' : 'error',
    } as any);
  }

  return (
    <AppLayout
      title="Feature Store"
      subtitle="Powered by Example 16: ML Feature Serving (500K+ lookups/sec, < 1ms P99)"
      backendUrl="localhost:8016"
      backendInfo="LRUCache (326K+ ops/sec)"
    >
      <StatsBar items={statsItems} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Feature Lookup */}
        <div className="lg:col-span-2">
          <DataCard title="Feature Lookup">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Feature ID
                </label>
                <input
                  type="text"
                  value={featureId}
                  onChange={(e) => setFeatureId(e.target.value)}
                  placeholder="e.g., user_age, product_price"
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Entity ID
                </label>
                <input
                  type="text"
                  value={entityId}
                  onChange={(e) => setEntityId(e.target.value)}
                  placeholder="e.g., user_123, product_456"
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <Button
                onClick={fetchFeature}
                disabled={!featureId || !entityId || loading}
                fullWidth
                loading={loading}
              >
                Lookup Feature
              </Button>
            </div>

            {/* Feature Result */}
            {feature && (
              <div className="mt-6 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                <h3 className="text-sm font-semibold text-neutral-900 mb-3">Result</h3>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-sm text-neutral-600">Feature ID:</dt>
                    <dd className="text-sm font-medium text-neutral-900">{feature.feature_id}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-neutral-600">Value:</dt>
                    <dd className="text-sm font-medium text-primary-700">
                      {JSON.stringify(feature.value)}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-neutral-600">Version:</dt>
                    <dd className="text-sm font-medium text-neutral-900">{feature.version}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-neutral-600">Timestamp:</dt>
                    <dd className="text-sm font-medium text-neutral-900">
                      {new Date(feature.timestamp * 1000).toLocaleString()}
                    </dd>
                  </div>
                </dl>
              </div>
            )}
          </DataCard>
        </div>

        {/* Feature Groups */}
        <div>
          <DataCard title="Feature Groups">
            <div className="space-y-3">
              {featureGroups.map((group) => (
                <div
                  key={group.name}
                  className="p-3 bg-neutral-50 rounded-lg border border-neutral-200"
                >
                  <h3 className="text-sm font-semibold text-neutral-900 mb-2">{group.name}</h3>
                  <div className="flex flex-wrap gap-1">
                    {group.features.slice(0, 5).map((f) => (
                      <span
                        key={f}
                        className="px-2 py-0.5 text-xs bg-primary-100 text-primary-800 rounded-full"
                      >
                        {f}
                      </span>
                    ))}
                    {group.features.length > 5 && (
                      <span className="px-2 py-0.5 text-xs bg-neutral-200 text-neutral-700 rounded-full">
                        +{group.features.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </DataCard>
        </div>
      </div>

      {/* Performance Info */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <DataCard variant="success">
          <div className="text-2xl font-bold text-success-700">500K+</div>
          <div className="text-sm text-success-900 mt-1">Lookups/sec</div>
        </DataCard>
        <DataCard variant="primary">
          <div className="text-2xl font-bold text-primary-700">&lt; 1ms</div>
          <div className="text-sm text-primary-900 mt-1">P99 Latency</div>
        </DataCard>
        <DataCard variant="warning">
          <div className="text-2xl font-bold text-amber-700">10M+</div>
          <div className="text-sm text-amber-900 mt-1">Features</div>
        </DataCard>
        <DataCard variant="info">
          <div className="text-2xl font-bold text-purple-700">&gt; 95%</div>
          <div className="text-sm text-purple-900 mt-1">Cache Hit Rate</div>
        </DataCard>
      </div>
    </AppLayout>
  );
}
