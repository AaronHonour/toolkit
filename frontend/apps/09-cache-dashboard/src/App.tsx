/**
 * Distributed Cache Dashboard
 * Example 9: Multi-Tier Caching (1M+ req/sec)
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import { Button, Badge, Input } from '@frontend-toolkit/atoms';
import {
  AppLayout,
  StatsBar,
  LoadingState,
  EmptyState,
  DataCard,
  DataTable,
} from '@frontend-toolkit/layouts';
import { useDebounce } from '@frontend-toolkit/performance';

interface CacheEntry {
  key: string;
  value: any;
  tier: 'L1' | 'L2';
  ttl: number;
  size: number;
}

interface Stats {
  total_requests?: number;
  l1_hits?: number;
  l2_hits?: number;
  misses?: number;
  hit_rate?: number;
  l1_size?: number;
  l2_size?: number;
}

const API_URL = 'http://localhost:8008';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [entries, setEntries] = useState<CacheEntry[]>([]);
  const [searchKey, setSearchKey] = useState('');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [loading, setLoading] = useState(true);

  const debouncedSearch = useDebounce(searchKey, 300);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, keysRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/cache/keys?limit=50`),
        ]);
        setStats(await statsRes.json());
        const keysData = await keysRes.json();
        setEntries(keysData.entries || []);
        setLoading(false);
      } catch (error) {
        console.error('Error:', error);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const setCache = async () => {
    if (!newKey || !newValue) return;
    try {
      await fetch(`${API_URL}/api/v1/cache/${newKey}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: newValue }),
      });
      setNewKey('');
      setNewValue('');
    } catch (error) {
      console.error('Set error:', error);
    }
  };

  const deleteCache = async (key: string) => {
    try {
      await fetch(`${API_URL}/api/v1/cache/${key}`, { method: 'DELETE' });
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  const filteredEntries = entries.filter((e) => e.key.includes(debouncedSearch));

  // Convert stats to StatsBar format
  const statsData = [
    {
      label: 'Total Requests',
      value: stats.total_requests?.toLocaleString() || '0',
    },
    {
      label: 'L1 Hits',
      value: stats.l1_hits?.toLocaleString() || '0',
      variant: 'success' as const,
    },
    {
      label: 'L2 Hits',
      value: stats.l2_hits?.toLocaleString() || '0',
      variant: 'warning' as const,
    },
    {
      label: 'Hit Rate',
      value: `${((stats.hit_rate || 0) * 100).toFixed(1)}%`,
      variant: 'primary' as const,
    },
  ];

  // DataTable columns
  const columns = [
    {
      key: 'key' as const,
      label: 'Cache Key',
      render: (entry: CacheEntry) => (
        <div>
          <div className="font-mono text-sm text-neutral-900">{entry.key}</div>
          <div className="text-xs text-neutral-500 line-clamp-1">
            {JSON.stringify(entry.value).slice(0, 100)}
          </div>
        </div>
      ),
    },
    {
      key: 'tier' as const,
      label: 'Tier',
      render: (entry: CacheEntry) => (
        <Badge variant={entry.tier === 'L1' ? 'success' : 'warning'} size="sm">
          {entry.tier}
        </Badge>
      ),
    },
    {
      key: 'size' as const,
      label: 'Size',
      render: (entry: CacheEntry) => (
        <div className="text-sm text-neutral-600">{entry.size} bytes</div>
      ),
    },
    {
      key: 'ttl' as const,
      label: 'TTL',
      render: (entry: CacheEntry) => (
        <div className="text-sm text-neutral-600">{entry.ttl}s</div>
      ),
    },
    {
      key: 'key' as const,
      label: 'Actions',
      render: (entry: CacheEntry) => (
        <Button size="sm" variant="danger" onClick={() => deleteCache(entry.key)}>
          Delete
        </Button>
      ),
    },
  ];

  return (
    <AppLayout
      title="Distributed Cache"
      description="Multi-Tier Caching (1M+ req/sec)"
      icon="⚡"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8008
          </div>
          <div>
            <span className="font-semibold">Architecture:</span> L1 (Memory) + L2 (Redis)
          </div>
        </div>
      }
    >
      {/* Stats Bar */}
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      {/* Main Content */}
      {loading ? (
        <LoadingState message="Loading cache data..." />
      ) : (
        <>
          {/* Cache Tier Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <DataCard
              title="L1 Cache"
              subtitle="In-memory cache"
              badge={{
                label: 'Active',
                variant: 'success',
              }}
              metadata={[
                { label: 'Backend', value: 'localhost:8008' },
                { label: 'Type', value: 'Memory' },
              ]}
            >
              <div className="p-4 bg-success-50 rounded border border-success-200">
                <div className="text-xs text-success-700">Entries</div>
                <div className="text-3xl font-bold text-success-900">{stats.l1_size || 0}</div>
                <div className="text-xs text-success-600">in memory</div>
              </div>
              <div className="mt-3 text-xs text-neutral-600">
                {stats.l1_hits?.toLocaleString() || 0} hits
              </div>
            </DataCard>

            <DataCard
              title="L2 Cache"
              subtitle="Redis cache"
              badge={{
                label: 'Active',
                variant: 'warning',
              }}
              metadata={[
                { label: 'Backend', value: 'Redis' },
                { label: 'Type', value: 'Distributed' },
              ]}
            >
              <div className="p-4 bg-amber-50 rounded border border-amber-200">
                <div className="text-xs text-amber-700">Entries</div>
                <div className="text-3xl font-bold text-amber-900">{stats.l2_size || 0}</div>
                <div className="text-xs text-amber-600">in Redis</div>
              </div>
              <div className="mt-3 text-xs text-neutral-600">
                {stats.l2_hits?.toLocaleString() || 0} hits
              </div>
            </DataCard>

            <DataCard
              title="Cache Misses"
              subtitle="Failed lookups"
              badge={{
                label: stats.misses && stats.misses > 1000 ? 'High' : 'Normal',
                variant: stats.misses && stats.misses > 1000 ? 'danger' : 'secondary',
              }}
            >
              <div className="p-4 bg-error-50 rounded border border-error-200">
                <div className="text-xs text-error-700">Total Misses</div>
                <div className="text-3xl font-bold text-error-900">{stats.misses || 0}</div>
                <div className="text-xs text-error-600">not found</div>
              </div>
              <div className="mt-3 text-xs text-neutral-600">
                Hit rate: {((stats.hit_rate || 0) * 100).toFixed(1)}%
              </div>
            </DataCard>
          </div>

          {/* Add Cache Entry */}
          <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-4">Add Cache Entry</h2>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  placeholder="Cache key (e.g., user:123)"
                  fullWidth
                />
              </div>
              <div className="flex-1">
                <Input
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  placeholder="Cache value (JSON supported)"
                  fullWidth
                />
              </div>
              <Button onClick={setCache} disabled={!newKey || !newValue}>
                Set Cache
              </Button>
            </div>
          </div>

          {/* Cache Entries Table */}
          <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
              <div>
                <h2 className="text-lg font-semibold text-neutral-900">Cache Entries</h2>
                <p className="text-sm text-neutral-600">
                  {filteredEntries.length} of {entries.length} entries
                </p>
              </div>
              <div className="w-full sm:w-64">
                <Input
                  value={searchKey}
                  onChange={(e) => setSearchKey(e.target.value)}
                  placeholder="Search cache keys..."
                  fullWidth
                  leftIcon={
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                  }
                />
              </div>
            </div>
            {loading ? (
              <LoadingState message="Loading cache entries..." />
            ) : filteredEntries.length > 0 ? (
              <DataTable data={filteredEntries} columns={columns} />
            ) : (
              <EmptyState
                icon="⚡"
                title={searchKey ? 'No matching entries' : 'No cache entries'}
                description={
                  searchKey
                    ? 'Try adjusting your search query.'
                    : 'Add cache entries using the form above.'
                }
              />
            )}
          </div>
        </>
      )}
    </AppLayout>
  );
}
