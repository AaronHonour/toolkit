/**
 * API Gateway Dashboard
 * Example 4: Service Routing (50K+ req/sec)
 *
 * REFACTORED: Now uses unified design system components
 */
import { useState, useEffect } from 'react';
import { Badge } from '@frontend-toolkit/atoms';
import { AppLayout, StatsBar, DataCard } from '@frontend-toolkit/layouts';

interface Service { name: string; url: string; healthy: boolean; latency: number; requests: number; }
interface Stats { total_requests?: number; avg_latency?: number; circuit_breaks?: number; }

const API_URL = 'http://localhost:8003';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [services, setServices] = useState<Service[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, svc] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/services`)
        ]);
        setStats(await s.json());
        const svcData = await svc.json();
        setServices(svcData.services || []);
      } catch (error) { console.error('Error:', error); }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const statsData = [
    { label: 'Total Requests', value: stats.total_requests?.toLocaleString() || '0' },
    { label: 'Avg Latency', value: `${stats.avg_latency?.toFixed(2) || 0}ms`, variant: 'success' as const },
    { label: 'Circuit Breaks', value: stats.circuit_breaks || '0', variant: (stats.circuit_breaks || 0) > 0 ? 'error' as const : 'default' as const },
  ];

  return (
    <AppLayout
      title="API Gateway"
      description="Service Routing (50K+ req/sec)"
      icon="🚪"
    >
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      <div className="bg-white rounded-lg border border-neutral-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Registered Services</h2>
        <div className="space-y-3">
          {services.map(s => (
            <div key={s.name} className="p-4 border border-neutral-200 rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-neutral-900">{s.name}</div>
                <div className="text-xs text-neutral-500 font-mono truncate">{s.url}</div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <div className="text-sm text-neutral-600">{s.requests.toLocaleString()} req</div>
                <div className="text-sm text-neutral-600">{s.latency.toFixed(1)}ms</div>
                <Badge variant={s.healthy ? 'success' : 'error'}>
                  {s.healthy ? 'Healthy' : 'Down'}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
