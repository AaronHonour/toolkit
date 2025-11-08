/**
 * Data Export Service UI
 * Example 5: High-Performance Data Export (10M records in 60s)
 */

import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';

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

const API_URL = 'http://localhost:8004';

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

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">📦 Data Export Service</h1>
          <p className="text-sm text-neutral-600">Fast Serialization (10M records/60s)</p>
        </div>
      </header>

      <div className="bg-primary-50 border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
          <div><span className="font-semibold">Total Exports:</span> <span className="ml-2 text-primary-700">{stats.total_exports?.toLocaleString() || 0}</span></div>
          <div><span className="font-semibold">Records:</span> <span className="ml-2 text-primary-700">{stats.records_exported?.toLocaleString() || 0}</span></div>
          <div><span className="font-semibold">Avg Time:</span> <span className="ml-2 text-success-700">{stats.avg_export_time?.toFixed(1) || 0}s</span></div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Create Export</h2>
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Format</label>
              <select value={format} onChange={(e) => setFormat(e.target.value)} className="w-full px-4 py-2 border rounded-lg">
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
                <option value="parquet">Parquet</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Compression</label>
              <select value={compression} onChange={(e) => setCompression(e.target.value)} className="w-full px-4 py-2 border rounded-lg">
                <option value="lz4">LZ4 (8.4x faster)</option>
                <option value="snappy">Snappy</option>
                <option value="zlib">Zlib</option>
                <option value="none">None</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Records</label>
              <input type="number" value={recordLimit} onChange={(e) => setRecordLimit(parseInt(e.target.value))} className="w-full px-4 py-2 border rounded-lg" />
            </div>
            <div className="flex items-end">
              <Button onClick={createExport} disabled={creating} loading={creating} fullWidth>Export</Button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Export History</h2>
          <div className="space-y-3">
            {jobs.map((job) => (
              <div key={job.id} className="p-4 border rounded-lg flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium">{job.format.toUpperCase()} • {job.compression}</div>
                  <div className="text-xs text-neutral-500">{job.record_count.toLocaleString()} records</div>
                  {job.status === 'processing' && (
                    <div className="mt-2 h-2 bg-neutral-200 rounded-full">
                      <div className="h-full bg-primary-500" style={{ width: `${job.progress}%` }} />
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={job.status === 'completed' ? 'success' : job.status === 'failed' ? 'error' : 'warning'}>{job.status}</Badge>
                  {job.download_url && <Button size="sm" onClick={() => window.open(job.download_url, '_blank')}>Download</Button>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}