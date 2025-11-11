/**
 * File Processing Service UI
 * Example 3: High-Throughput File Processing (10K+ files/min)
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import { Button, Badge, Select } from '@unistax/atoms';
import { AppLayout, StatsBar, DataCard, LoadingState } from '@unistax/layouts';

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

const API_URL = 'http://localhost:8003';

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

  const statsData = [
    { label: 'Files Processed', value: stats.files_processed?.toLocaleString() || '0' },
    { label: 'Rate', value: `${stats.files_per_minute?.toLocaleString() || 0}/min`, variant: 'success' as const },
    { label: 'Avg Time', value: `${stats.avg_processing_time_ms?.toFixed(1) || 0}ms` },
    { label: 'Workers', value: `${stats.active_workers || 0}/${stats.pool_size || 0}` },
    { label: 'Utilization', value: `${((stats.worker_utilization || 0) * 100).toFixed(0)}%`, variant: 'warning' as const },
  ];

  const getStatusVariant = (status: FileJob['status']) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'processing': return 'warning';
      default: return 'secondary';
    }
  };

  return (
    <AppLayout
      title="File Processing Pipeline"
      description="High-Throughput Processing (10K+ files/min)"
      icon="📁"
    >
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-lg border border-neutral-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Upload File</h2>
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1 w-full">
            <Select
              label="Select Operation"
              options={operations}
              value={selectedOperation}
              onChange={(e) => setSelectedOperation(e.target.value)}
              fullWidth
            />
          </div>
          <div className="flex-1 w-full">
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Choose File
            </label>
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={uploading}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Jobs List */}
      {uploading ? (
        <LoadingState message="Uploading file..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <DataCard
              key={job.id}
              title={job.filename}
              subtitle={`${(job.size / 1024).toFixed(1)} KB`}
              badge={{
                label: job.status,
                variant: getStatusVariant(job.status),
              }}
              metadata={[
                { label: 'Operation', value: job.operation },
                { label: 'Progress', value: `${job.progress}%` },
              ]}
            >
              {job.status === 'processing' && (
                <div className="mt-2 h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              )}
            </DataCard>
          ))}
        </div>
      )}
    </AppLayout>
  );
}
