/**
 * CDC Pipeline Monitor - Example 13 (localhost:8013)
 * Change Data Capture with 100K+ changes/sec, < 50ms latency
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Badge } from '@unistax/atoms';
import {
  AppLayout,
  StatsBar,
  DataTable,
} from '@unistax/layouts';

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

  // Convert stats to StatsBar format
  const statsData = stats
    ? [
        {
          label: 'Changes Captured',
          value: stats.changes_captured?.toLocaleString() || '0',
        },
        {
          label: 'Capture Rate',
          value: `${stats.changes_per_sec?.toLocaleString() || 0}/sec`,
          variant: 'success' as const,
        },
        {
          label: 'End-to-End Latency',
          value: `${stats.latency_ms?.toFixed(1) || 0}ms`,
          variant: stats.latency_ms && stats.latency_ms < 50 ? ('success' as const) : ('warning' as const),
        },
        {
          label: 'Dedup Rate',
          value: `${((stats.dedup_rate || 0) * 100).toFixed(1)}%`,
        },
      ]
    : [];

  // Configure table columns
  const columns = [
    {
      key: 'operation',
      header: 'Operation',
      render: (value: string) => (
        <Badge variant={value === 'INSERT' ? 'success' : value === 'UPDATE' ? 'warning' : 'error'}>
          {value}
        </Badge>
      ),
    },
    {
      key: 'table',
      header: 'Table',
    },
    {
      key: 'key',
      header: 'Key',
      className: 'font-mono',
    },
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (value: number) => new Date(value * 1000).toLocaleTimeString(),
    },
  ];

  return (
    <AppLayout
      title="CDC Pipeline Monitor"
      description="Change Data Capture (100K+ changes/sec)"
      icon="📊"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8013
          </div>
          <div>
            <span className="font-semibold">Latency:</span> {'<'} 50ms end-to-end
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

      {/* Recent Changes Table */}
      <DataTable
        title="Recent Changes"
        subtitle="Real-time change data capture events"
        columns={columns}
        data={changes}
        emptyMessage="No changes captured yet"
      />
    </AppLayout>
  );
}
