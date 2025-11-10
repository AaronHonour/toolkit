/**
 * Message Queue Dashboard
 * Example 10: Message Broker (500K+ msgs/sec)
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';
import {
  AppLayout,
  StatsBar,
  LoadingState,
  EmptyState,
  DataCard,
  DataTable,
} from '@frontend-toolkit/layouts';

interface Queue {
  name: string;
  size: number;
  consumers: number;
  rate: number;
}

interface Stats {
  messages_total?: number;
  messages_per_sec?: number;
  active_queues?: number;
}

const API_URL = 'http://localhost:8009';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [queues, setQueues] = useState<Queue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, q] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/queues`),
        ]);
        setStats(await s.json());
        const queueData = await q.json();
        setQueues(queueData.queues || []);
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

  // Convert stats to StatsBar format
  const statsData = [
    {
      label: 'Total Messages',
      value: stats.messages_total?.toLocaleString() || '0',
    },
    {
      label: 'Messages/sec',
      value: stats.messages_per_sec?.toLocaleString() || '0',
      variant: 'success' as const,
    },
    {
      label: 'Active Queues',
      value: (stats.active_queues || 0).toString(),
      variant: 'primary' as const,
    },
  ];

  // DataTable columns
  const columns = [
    {
      key: 'name' as const,
      label: 'Queue Name',
      render: (queue: Queue) => (
        <div>
          <div className="font-semibold text-sm text-neutral-900">{queue.name}</div>
          <div className="text-xs text-neutral-500">{queue.consumers} consumer(s)</div>
        </div>
      ),
    },
    {
      key: 'size' as const,
      label: 'Queue Size',
      render: (queue: Queue) => (
        <Badge variant={queue.size > 1000 ? 'warning' : queue.size > 100 ? 'primary' : 'success'}>
          {queue.size.toLocaleString()} msgs
        </Badge>
      ),
    },
    {
      key: 'rate' as const,
      label: 'Processing Rate',
      render: (queue: Queue) => (
        <div className="text-sm font-semibold text-success-700">{queue.rate.toLocaleString()}/sec</div>
      ),
    },
    {
      key: 'consumers' as const,
      label: 'Consumers',
      render: (queue: Queue) => (
        <div className="text-sm text-neutral-600">{queue.consumers}</div>
      ),
    },
  ];

  return (
    <AppLayout
      title="Message Queue"
      description="Message Broker (500K+ msgs/sec)"
      icon="📮"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8009
          </div>
          <div>
            <span className="font-semibold">Broker:</span> High-performance message queue
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
        <LoadingState message="Loading queue data..." />
      ) : (
        <>
          {/* Queue Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <DataCard
              title="Message Throughput"
              subtitle="Current processing rate"
              badge={{
                label: stats.messages_per_sec && stats.messages_per_sec > 400000 ? 'High' : 'Normal',
                variant:
                  stats.messages_per_sec && stats.messages_per_sec > 400000 ? 'success' : 'primary',
              }}
              metadata={[
                { label: 'Backend', value: 'localhost:8009' },
                { label: 'Protocol', value: 'HTTP/REST' },
              ]}
            >
              <div className="space-y-3">
                <div className="p-4 bg-success-50 rounded border border-success-200">
                  <div className="text-xs text-success-700">Processing Rate</div>
                  <div className="text-3xl font-bold text-success-900">
                    {stats.messages_per_sec
                      ? `${(stats.messages_per_sec / 1000).toFixed(1)}K`
                      : '0'}
                  </div>
                  <div className="text-xs text-success-600">messages/sec</div>
                </div>
                <div className="flex items-center gap-2 text-sm text-neutral-600">
                  <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
                  High-throughput message processing
                </div>
              </div>
            </DataCard>

            <DataCard
              title="Total Messages"
              subtitle="Lifetime message count"
              badge={{
                label: 'Processed',
                variant: 'primary',
              }}
            >
              <div className="space-y-3">
                <div className="p-4 bg-primary-50 rounded border border-primary-200">
                  <div className="text-xs text-primary-700">Messages</div>
                  <div className="text-3xl font-bold text-primary-900">
                    {stats.messages_total
                      ? stats.messages_total > 1000000
                        ? `${(stats.messages_total / 1000000).toFixed(2)}M`
                        : stats.messages_total.toLocaleString()
                      : '0'}
                  </div>
                  <div className="text-xs text-primary-600">total processed</div>
                </div>
                <div className="text-xs text-neutral-600">
                  All messages successfully delivered to consumers
                </div>
              </div>
            </DataCard>

            <DataCard
              title="Active Queues"
              subtitle="Queue management"
              badge={{
                label: stats.active_queues && stats.active_queues > 0 ? 'Active' : 'Idle',
                variant: stats.active_queues && stats.active_queues > 0 ? 'success' : 'secondary',
              }}
            >
              <div className="space-y-3">
                <div className="p-4 bg-neutral-50 rounded">
                  <div className="text-xs text-neutral-600">Active Queues</div>
                  <div className="text-3xl font-bold text-neutral-900">
                    {stats.active_queues || 0}
                  </div>
                  <div className="text-xs text-neutral-500">queues running</div>
                </div>
                <div className="text-xs text-neutral-600">
                  {queues.length} queue(s) with {queues.reduce((sum, q) => sum + q.consumers, 0)}{' '}
                  consumer(s)
                </div>
              </div>
            </DataCard>
          </div>

          {/* Queues Table */}
          <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-neutral-900">Active Queues</h2>
              <p className="text-sm text-neutral-600">
                Real-time view of all message queues and their status
              </p>
            </div>
            {loading ? (
              <LoadingState message="Loading queues..." />
            ) : queues.length > 0 ? (
              <div className="space-y-4">
                <DataTable data={queues} columns={columns} />
                <div className="mt-4 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                  <div className="text-sm text-neutral-700">
                    <span className="font-semibold">Queue Health:</span>{' '}
                    {queues.filter((q) => q.size < 1000).length} / {queues.length} queues are
                    healthy (size &lt; 1000)
                  </div>
                  <div className="text-xs text-neutral-600 mt-1">
                    Total pending messages:{' '}
                    {queues.reduce((sum, q) => sum + q.size, 0).toLocaleString()}
                  </div>
                </div>
              </div>
            ) : (
              <EmptyState
                icon="📮"
                title="No active queues"
                description="Message queues will appear here when they become active."
              />
            )}
          </div>
        </>
      )}
    </AppLayout>
  );
}
