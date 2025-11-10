/**
 * File Processing Service UI
 * Example 3: High-Throughput File Processing (10K+ files/min)
 *
 * Features:
 * - File upload interface
 * - Processing pipeline visualization
 * - Worker pool monitoring
 * - Progress tracking
 */

import { useState, useEffect } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';

interface FileJob {
  id: string;
  filename: string;
  size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  operation: string;
  created_at: number;
}

interface Stats {
  files_processed?: number;
  files_per_minute?: number;
  avg_processing_time_ms?: number;
  worker_utilization?: number;
  pool_size?: number;
  active_workers?: number;
}

const API_URL = 'http://localhost:8002';

export function App() {
  const [stats, setStats] = useState<Stats>({});
  const [jobs, setJobs] = useState<FileJob[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedOperation, setSelectedOperation] = useState('resize_image');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, jobsRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/stats`),
          fetch(`${API_URL}/api/v1/files?limit=20`)
        ]);
        setStats(await statsRes.json());
        const jobsData = await jobsRes.json();
        setJobs(jobsData.files || []);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', files[0]);
    formData.append('operation', selectedOperation);

    try {
      await fetch(`${API_URL}/api/v1/files`, {
        method: 'POST',
        body: formData
      });
      // Refresh jobs list
      const jobsRes = await fetch(`${API_URL}/api/v1/files?limit=20`);
      const jobsData = await jobsRes.json();
      setJobs(jobsData.files || []);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const operations = [
    { value: 'resize_image', label: 'Resize Image' },
    { value: 'extract_text', label: 'Extract Text (PDF)' },
    { value: 'transcode_video', label: 'Transcode Video' },
    { value: 'parse_csv', label: 'Parse CSV' }
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">📁 File Processing Pipeline</h1>
          <p className="text-sm text-neutral-600">High-Throughput Processing (10K+ files/min)</p>
        </div>
      </header>

      {/* Stats */}
      <div className="bg-primary-50 border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 text-sm">
          <div>
            <span className="font-semibold">Files Processed:</span>
            <span className="ml-2 text-primary-700">{stats.files_processed?.toLocaleString() || 0}</span>
          </div>
          <div>
            <span className="font-semibold">Rate:</span>
            <span className="ml-2 text-success-700">{stats.files_per_minute?.toLocaleString() || 0}/min</span>
          </div>
          <div>
            <span className="font-semibold">Avg Time:</span>
            <span className="ml-2 text-primary-700">{stats.avg_processing_time_ms?.toFixed(1) || 0}ms</span>
          </div>
          <div>
            <span className="font-semibold">Workers:</span>
            <span className="ml-2 text-primary-700">{stats.active_workers || 0}/{stats.pool_size || 0}</span>
          </div>
          <div>
            <span className="font-semibold">Utilization:</span>
            <span className="ml-2 text-amber-700">{((stats.worker_utilization || 0) * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Upload Section */}
        <div className="bg-white rounded-lg border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Upload File</h2>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Select Operation
              </label>
              <select
                value={selectedOperation}
                onChange={(e) => setSelectedOperation(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {operations.map(op => (
                  <option key={op.value} value={op.value}>{op.label}</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Choose File
              </label>
              <input
                type="file"
                onChange={handleFileUpload}
                disabled={uploading}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <Button disabled={uploading} loading={uploading}>
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
          </div>
        </div>

        {/* Jobs List */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Processing Queue</h2>
          <div className="space-y-3">
            {jobs.length > 0 ? (
              jobs.map((job) => (
                <div key={job.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-medium text-neutral-900">{job.filename}</div>
                      <div className="text-xs text-neutral-500">
                        {(job.size / 1024).toFixed(1)} KB • {job.operation}
                      </div>
                    </div>
                    <Badge
                      variant={
                        job.status === 'completed' ? 'success' :
                        job.status === 'failed' ? 'error' :
                        job.status === 'processing' ? 'warning' : 'secondary'
                      }
                    >
                      {job.status}
                    </Badge>
                  </div>
                  {job.status === 'processing' && (
                    <div className="mt-2">
                      <div className="flex items-center justify-between text-xs text-neutral-600 mb-1">
                        <span>Progress</span>
                        <span>{job.progress}%</span>
                      </div>
                      <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500 transition-all duration-300"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-neutral-500">
                No files in queue. Upload a file to get started.
              </div>
            )}
          </div>
        </div>

        {/* Pipeline Visualization */}
        <div className="mt-6 bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Processing Pipeline</h2>
          <div className="flex items-center justify-between">
            {['Validation', 'Preprocessing', 'Processing', 'Postprocessing', 'Storage'].map((stage, idx, arr) => (
              <div key={stage} className="flex items-center flex-1">
                <div className="text-center flex-1">
                  <div className="w-12 h-12 mx-auto bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-semibold">
                    {idx + 1}
                  </div>
                  <div className="text-xs mt-2 text-neutral-700">{stage}</div>
                </div>
                {idx < arr.length - 1 && (
                  <svg className="w-8 h-8 text-neutral-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
