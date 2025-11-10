/**
 * Distributed Cache Dashboard
 * Example 9: Multi-Tier Caching (1M+ req/sec)
 */

import { useState, useEffect } from 'react';
import { Button, Badge, Input } from '@frontend-toolkit/atoms';

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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, keysRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/cache/keys?limit=50`)
        ]);
        setStats(await statsRes.json());
        const keysData = await keysRes.json();
        setEntries(keysData.entries || []);
      } catch (error) {
        console.error('Error:', error);
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
        body: JSON.stringify({ value: newValue })
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

  const filteredEntries = entries.filter(e => e.key.includes(searchKey));

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">⚡ Distributed Cache</h1>
          <p className="text-sm text-neutral-600">Multi-Tier Caching (1M+ req/sec)</p>
        </div>
      </header>

      <div className="bg-primary-50 border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
          <div><span className="font-semibold">Total Requests:</span> <span className="ml-2">{stats.total_requests?.toLocaleString() || 0}</span></div>
          <div><span className="font-semibold">L1 Hits:</span> <span className="ml-2 text-success-700">{stats.l1_hits?.toLocaleString() || 0}</span></div>
          <div><span className="font-semibold">L2 Hits:</span> <span className="ml-2 text-amber-700">{stats.l2_hits?.toLocaleString() || 0}</span></div>
          <div><span className="font-semibold">Hit Rate:</span> <span className="ml-2 text-primary-700">{((stats.hit_rate || 0) * 100).toFixed(1)}%</span></div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-neutral-600">L1 Cache</div>
            <div className="text-2xl font-bold text-success-700">{stats.l1_size || 0}</div>
            <div className="text-xs text-neutral-500">entries</div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-neutral-600">L2 Cache</div>
            <div className="text-2xl font-bold text-amber-700">{stats.l2_size || 0}</div>
            <div className="text-xs text-neutral-500">entries</div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-neutral-600">Misses</div>
            <div className="text-2xl font-bold text-error-700">{stats.misses || 0}</div>
            <div className="text-xs text-neutral-500">cache misses</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Add Cache Entry</h2>
          <div className="flex gap-4">
            <Input value={newKey} onChange={(e) => setNewKey(e.target.value)} placeholder="Key" />
            <Input value={newValue} onChange={(e) => setNewValue(e.target.value)} placeholder="Value" />
            <Button onClick={setCache}>Set</Button>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Cache Entries</h2>
            <Input value={searchKey} onChange={(e) => setSearchKey(e.target.value)} placeholder="Search keys..." className="w-64" />
          </div>
          <div className="space-y-2">
            {filteredEntries.map((entry) => (
              <div key={entry.key} className="p-3 border rounded flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-mono text-sm">{entry.key}</div>
                  <div className="text-xs text-neutral-500">{JSON.stringify(entry.value).slice(0, 100)}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={entry.tier === 'L1' ? 'success' : 'warning'} size="sm">{entry.tier}</Badge>
                  <Button size="sm" variant="danger" onClick={() => deleteCache(entry.key)}>Delete</Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}