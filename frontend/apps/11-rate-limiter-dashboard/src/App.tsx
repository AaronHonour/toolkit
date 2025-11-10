/**
 * Rate Limiter Dashboard
 *
 * Connects to Example 11: Distributed Rate Limiter (localhost:8011)
 *
 * Features:
 * - Token bucket visualization
 * - Sliding window counters
 * - Multi-tenant rate limiting
 * - 1M+ checks/sec performance
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';
import {
  AppLayout,
  StatsBar,
  EmptyState,
  DataCard,
} from '@frontend-toolkit/layouts';

interface RateLimitStatus {
  allowed: boolean;
  tokens_remaining: number;
  tokens_capacity: number;
  reset_time: number;
}

interface Stats {
  checks_total: number;
  checks_allowed: number;
  checks_rejected: number;
  checks_per_sec: number;
}

const API_URL = 'http://localhost:8011';

export function App() {
  const [clientId, setClientId] = useState('client_1');
  const [rateLimit, setRateLimit] = useState({ capacity: 100, refill_rate: 10 });
  const [status, setStatus] = useState<RateLimitStatus | null>(null);
  const [stats, setStats] = useState<Stats>({
    checks_total: 0,
    checks_allowed: 0,
    checks_rejected: 0,
    checks_per_sec: 0,
  });
  const [loading, setLoading] = useState(false);
  const [autoTest, setAutoTest] = useState(false);

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
    const interval = setInterval(fetchStats, 1000);
    return () => clearInterval(interval);
  }, []);

  // Auto-test mode
  useEffect(() => {
    if (!autoTest) return;

    const interval = setInterval(() => {
      checkRateLimit();
    }, 100); // 10 requests/sec

    return () => clearInterval(interval);
  }, [autoTest, clientId]);

  const checkRateLimit = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: clientId,
          capacity: rateLimit.capacity,
          refill_rate: rateLimit.refill_rate,
        }),
      });
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Rate limit check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const tokensPercentage = status
    ? (status.tokens_remaining / status.tokens_capacity) * 100
    : 0;

  // Convert stats to StatsBar format
  const statsData = [
    {
      label: 'Total Checks',
      value: stats.checks_total.toLocaleString(),
    },
    {
      label: 'Allowed',
      value: stats.checks_allowed.toLocaleString(),
      variant: 'success' as const,
    },
    {
      label: 'Rejected',
      value: stats.checks_rejected.toLocaleString(),
      variant: 'danger' as const,
    },
    {
      label: 'Rate',
      value: `${stats.checks_per_sec.toLocaleString()}/sec`,
    },
  ];

  return (
    <AppLayout
      title="Distributed Rate Limiter"
      description="Token Bucket + Sliding Window (1M+ checks/sec)"
      icon="🚦"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8011
          </div>
          <div>
            <span className="font-semibold">Powered by:</span> LRUCache + ConsistentHashRing
          </div>
        </div>
      }
    >
      {/* Stats Bar */}
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Configuration */}
        <div>
          <DataCard
            title="Configuration"
            subtitle="Rate limiting parameters"
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Client ID
                </label>
                <input
                  type="text"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Token Capacity: {rateLimit.capacity}
                </label>
                <input
                  type="range"
                  min="10"
                  max="1000"
                  value={rateLimit.capacity}
                  onChange={(e) =>
                    setRateLimit({ ...rateLimit, capacity: parseInt(e.target.value) })
                  }
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Refill Rate: {rateLimit.refill_rate}/sec
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={rateLimit.refill_rate}
                  onChange={(e) =>
                    setRateLimit({ ...rateLimit, refill_rate: parseInt(e.target.value) })
                  }
                  className="w-full"
                />
              </div>

              <Button onClick={checkRateLimit} disabled={loading} fullWidth>
                Check Rate Limit
              </Button>

              <Button
                onClick={() => setAutoTest(!autoTest)}
                variant={autoTest ? 'danger' : 'secondary'}
                fullWidth
              >
                {autoTest ? 'Stop Auto-Test' : 'Start Auto-Test'}
              </Button>
            </div>
          </DataCard>
        </div>

        {/* Token Bucket Visualization */}
        <div className="lg:col-span-2">
          <DataCard
            title="Token Bucket Status"
            subtitle="Real-time token availability"
          >
            {status ? (
              <div className="space-y-6">
                {/* Status Badge */}
                <div className="flex items-center justify-between">
                  <Badge
                    variant={status.allowed ? 'success' : 'error'}
                    size="lg"
                    dot
                    dotColor={status.allowed ? 'success' : 'error'}
                  >
                    {status.allowed ? 'Request Allowed' : 'Request Rejected'}
                  </Badge>
                  <div className="text-sm text-neutral-600">
                    {status.tokens_remaining} / {status.tokens_capacity} tokens
                  </div>
                </div>

                {/* Token Bucket Visual */}
                <div className="relative">
                  <div className="h-64 bg-neutral-100 rounded-lg overflow-hidden relative">
                    {/* Bucket outline */}
                    <div className="absolute inset-0 border-4 border-neutral-300 rounded-lg" />

                    {/* Token level */}
                    <div
                      className={`absolute bottom-0 left-0 right-0 transition-all duration-300 ${
                        tokensPercentage > 66
                          ? 'bg-success-500'
                          : tokensPercentage > 33
                            ? 'bg-amber-500'
                            : 'bg-error-500'
                      }`}
                      style={{ height: `${tokensPercentage}%` }}
                    />

                    {/* Tokens count overlay */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-4xl font-bold text-neutral-900">
                          {status.tokens_remaining}
                        </div>
                        <div className="text-sm text-neutral-600 mt-1">
                          tokens remaining
                        </div>
                      </div>
                    </div>

                    {/* Refill indicator */}
                    <div className="absolute bottom-4 left-0 right-0 flex items-center justify-center">
                      <div className="px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-medium text-neutral-700 shadow-sm">
                        Refilling at {rateLimit.refill_rate}/sec
                      </div>
                    </div>
                  </div>

                  {/* Scale markers */}
                  <div className="absolute left-0 top-0 bottom-0 -ml-12 flex flex-col justify-between text-xs text-neutral-500">
                    <span>{status.tokens_capacity}</span>
                    <span>{Math.floor(status.tokens_capacity / 2)}</span>
                    <span>0</span>
                  </div>
                </div>

                {/* Details */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-neutral-200">
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Capacity</dt>
                    <dd className="mt-1 text-xl font-semibold text-neutral-900">
                      {status.tokens_capacity}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Refill Rate</dt>
                    <dd className="mt-1 text-xl font-semibold text-neutral-900">
                      {rateLimit.refill_rate}/sec
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Utilization</dt>
                    <dd className="mt-1 text-xl font-semibold text-neutral-900">
                      {tokensPercentage.toFixed(1)}%
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-neutral-600">Reset In</dt>
                    <dd className="mt-1 text-xl font-semibold text-neutral-900">
                      {status.reset_time.toFixed(1)}s
                    </dd>
                  </div>
                </div>
              </div>
            ) : (
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
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                }
                title="No status yet"
                message='Click "Check Rate Limit" to test'
              />
            )}
          </DataCard>
        </div>
      </div>

      {/* Performance Info */}
      <DataCard
        title="Rate Limiter Performance"
        subtitle="System capabilities and algorithms"
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 bg-success-50 rounded-lg border border-success-200">
            <div className="text-2xl font-bold text-success-700">1M+</div>
            <div className="text-sm text-success-900 mt-1">Checks/sec</div>
          </div>
          <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
            <div className="text-2xl font-bold text-primary-700">Token Bucket</div>
            <div className="text-sm text-primary-900 mt-1">Algorithm</div>
          </div>
          <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
            <div className="text-2xl font-bold text-amber-700">Multi-tenant</div>
            <div className="text-sm text-amber-900 mt-1">ConsistentHashRing</div>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div className="text-2xl font-bold text-purple-700">326K+</div>
            <div className="text-sm text-purple-900 mt-1">LRUCache ops/sec</div>
          </div>
        </div>
      </DataCard>
    </AppLayout>
  );
}
