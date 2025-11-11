/**
 * Data Export Service UI
 * Example 5: High-Performance Data Export (10M records in 60s)
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import { Button, Badge, Select, Input } from '@unistax/atoms';
import { AppLayout, StatsBar, DataCard } from '@unistax/layouts';

interface ExportJob {
  id: string;
  format: string;
  compression: string;
  record_count: number;
  status: string;
  progress: number;
  download_url?: string;
}

interface Stats {
  total_exports?: number;
  records_exported?: number;
  avg_export_time?: number;
}

const API_URL = 'http://localhost:8005';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [jobs, setJobs] = useState<ExportJob[]>([]);
  const [format, setFormat] = useState('csv');
  const [compression, setCompression] = useState('lz4');
  const [recordLimit, setRecordLimit] = useState(10000);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, jobsRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/exports?limit=10`)
        ]);
        setStats(await statsRes.json());
        const jobsData = await jobsRes.json();
        setJobs(jobsData.exports || []);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const createExport = async () => {
    setCreating(true);
    try {
      await fetch(`${API_URL}/api/v1/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format, compression, limit: recordLimit })
      });
      const jobsRes = await fetch(`${API_URL}/api/v1/exports?limit=10`);
      const jobsData = await jobsRes.json();
      setJobs(jobsData.exports || []);
    } catch (error) {
      console.error('Export error:', error);
    } finally {
      setCreating(false);
    }
  };

  const statsData = [
    { label: 'Total Exports', value: stats.total_exports?.toLocaleString() || '0' },
    { label: 'Records Exported', value: stats.records_exported?.toLocaleString() || '0' },
    { label: 'Avg Time', value: `${stats.avg_export_time?.toFixed(1) || 0}s`, variant: 'success' as const },
  ];

  const formatOptions = [
    { value: 'csv', label: 'CSV' },
    { value: 'json', label: 'JSON' },
    { value: 'parquet', label: 'Parquet' },
  ];

  const compressionOptions = [
    { value: 'lz4', label: 'LZ4 (8.4x faster)' },
    { value: 'snappy', label: 'Snappy' },
    { value: 'zlib', label: 'Zlib' },
    { value: 'none', label: 'None' },
  ];

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'processing': return 'warning';
      default: return 'secondary';
    }
  };

  return (
    <AppLayout
      title="Data Export Service"
      description="Fast Serialization (10M records/60s)"
      icon="📦"
    >
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      {/* Create Export Form */}
      <div className="bg-white rounded-lg border border-neutral-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Create Export</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <Select
            label="Format"
            options={formatOptions}
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            fullWidth
          />
          <Select
            label="Compression"
            options={compressionOptions}
            value={compression}
            onChange={(e) => setCompression(e.target.value)}
            fullWidth
          />
          <Input
            label="Records"
            type="number"
            value={recordLimit.toString()}
            onChange={(e) => setRecordLimit(parseInt(e.target.value) || 0)}
            fullWidth
          />
          <div className="flex items-end">
            <Button
              onClick={createExport}
              disabled={creating}
              loading={creating}
              fullWidth
            >
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Export History */}
      <div className="bg-white rounded-lg border border-neutral-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Export History</h2>
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="p-4 border border-neutral-200 rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="font-medium text-neutral-900">
                  {job.format.toUpperCase()} • {job.compression}
                </div>
                <div className="text-xs text-neutral-500">
                  {job.record_count.toLocaleString()} records
                </div>
                {job.status === 'processing' && (
                  <div className="mt-2 h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 transition-all duration-300"
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                )}
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <Badge variant={getStatusVariant(job.status) as any}>
                  {job.status}
                </Badge>
                {job.download_url && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open(job.download_url, '_blank')}
                  >
                    Download
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
