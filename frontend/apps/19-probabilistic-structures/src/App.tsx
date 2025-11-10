/**
 * Probabilistic Data Structures UI
 *
 * Connects to Example 19: Probabilistic Structures Service (localhost:8019)
 *
 * Features:
 * - Bloom Filter: Set membership testing
 * - HyperLogLog: Cardinality estimation
 * - Count-Min Sketch: Frequency estimation
 * - T-Digest: Percentile approximation
 */

import { useState } from 'react';
import { Button, Badge } from '@frontend-toolkit/atoms';
import { AppLayout, DataCard, Tabs } from '@frontend-toolkit/layouts';

const API_URL = 'http://localhost:8019';

type StructureType = 'bloom' | 'hll' | 'cms' | 'tdigest';

export function App() {
  const [activeStructure, setActiveStructure] = useState<StructureType>('bloom');
  const [input, setInput] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Bloom Filter Operations
  const bloomAdd = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/v1/bloom/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: input }),
      });
      setResult({ type: 'success', message: `Added "${input}" to Bloom filter` });
    } catch (error) {
      setResult({ type: 'error', message: 'Error adding to Bloom filter' });
    } finally {
      setLoading(false);
    }
  };

  const bloomCheck = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/v1/bloom/check?item=${encodeURIComponent(input)}`
      );
      const data = await response.json();
      setResult({
        type: 'result',
        message: data.probably_exists
          ? `"${input}" probably exists (with false positive rate)`
          : `"${input}" definitely does not exist`,
        exists: data.probably_exists,
      });
    } catch (error) {
      setResult({ type: 'error', message: 'Error checking Bloom filter' });
    } finally {
      setLoading(false);
    }
  };

  // HyperLogLog Operations
  const hllAdd = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/v1/hll/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: input }),
      });
      setResult({ type: 'success', message: `Added "${input}" to HyperLogLog` });
    } catch (error) {
      setResult({ type: 'error', message: 'Error adding to HyperLogLog' });
    } finally {
      setLoading(false);
    }
  };

  const hllCount = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/hll/count`);
      const data = await response.json();
      setResult({
        type: 'result',
        message: `Estimated cardinality: ${data.cardinality.toLocaleString()}`,
        cardinality: data.cardinality,
      });
    } catch (error) {
      setResult({ type: 'error', message: 'Error counting HyperLogLog' });
    } finally {
      setLoading(false);
    }
  };

  // Count-Min Sketch Operations
  const cmsAdd = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/v1/cms/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: input }),
      });
      setResult({ type: 'success', message: `Incremented count for "${input}"` });
    } catch (error) {
      setResult({ type: 'error', message: 'Error adding to Count-Min Sketch' });
    } finally {
      setLoading(false);
    }
  };

  const cmsEstimate = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/v1/cms/estimate?item=${encodeURIComponent(input)}`
      );
      const data = await response.json();
      setResult({
        type: 'result',
        message: `Estimated frequency of "${input}": ${data.frequency.toLocaleString()}`,
        frequency: data.frequency,
      });
    } catch (error) {
      setResult({ type: 'error', message: 'Error estimating frequency' });
    } finally {
      setLoading(false);
    }
  };

  // T-Digest Operations
  const tdigestAdd = async () => {
    const value = parseFloat(input);
    if (isNaN(value)) {
      setResult({ type: 'error', message: 'Please enter a valid number' });
      return;
    }

    setLoading(true);
    try {
      await fetch(`${API_URL}/api/v1/tdigest/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value }),
      });
      setResult({ type: 'success', message: `Added value ${value} to T-Digest` });
    } catch (error) {
      setResult({ type: 'error', message: 'Error adding to T-Digest' });
    } finally {
      setLoading(false);
    }
  };

  const tdigestQuantile = async () => {
    const quantile = parseFloat(input);
    if (isNaN(quantile) || quantile < 0 || quantile > 1) {
      setResult({ type: 'error', message: 'Please enter a quantile between 0 and 1' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/tdigest/quantile?q=${quantile}`);
      const data = await response.json();
      setResult({
        type: 'result',
        message: `P${(quantile * 100).toFixed(0)} ≈ ${data.value.toFixed(2)}`,
        value: data.value,
      });
    } catch (error) {
      setResult({ type: 'error', message: 'Error estimating quantile' });
    } finally {
      setLoading(false);
    }
  };

  const structures = [
    {
      type: 'bloom' as StructureType,
      name: 'Bloom Filter',
      description: 'Set membership testing with false positives',
      operations: [
        { label: 'Add Item', action: bloomAdd },
        { label: 'Check Membership', action: bloomCheck },
      ],
      placeholder: 'Enter item to test...',
      properties: [
        'No false negatives',
        'Possible false positives',
        'O(1) membership testing',
        'Space-efficient',
      ],
      performance: '131K+ ops/sec',
      useCases: [
        { title: 'Cache Filtering', description: 'Check if key might be in cache before lookup' },
        {
          title: 'Malicious URL Detection',
          description: 'Quick check against known bad URLs',
        },
      ],
    },
    {
      type: 'hll' as StructureType,
      name: 'HyperLogLog',
      description: 'Cardinality estimation for unique counts',
      operations: [
        { label: 'Add Item', action: hllAdd },
        { label: 'Get Cardinality', action: hllCount },
      ],
      placeholder: 'Enter item to count...',
      properties: [
        '~2% accuracy',
        'Fixed memory usage',
        'Mergeable sketches',
        'Billions of uniques',
      ],
      performance: '100:1 space efficiency',
      useCases: [
        { title: 'Unique Visitors', description: 'Count distinct users with minimal memory' },
        {
          title: 'Distributed Cardinality',
          description: 'Merge counts from multiple servers',
        },
      ],
    },
    {
      type: 'cms' as StructureType,
      name: 'Count-Min Sketch',
      description: 'Frequency estimation for item counts',
      operations: [
        { label: 'Increment Count', action: cmsAdd },
        { label: 'Estimate Frequency', action: cmsEstimate },
      ],
      placeholder: 'Enter item to count...',
      properties: [
        'Frequency estimation',
        'Configurable accuracy',
        'No deletions',
        'Sublinear space',
      ],
      performance: '> 99% accuracy',
      useCases: [
        { title: 'Top-K Items', description: 'Track most frequent items in stream' },
        { title: 'Rate Limiting', description: 'Approximate request counts per user' },
      ],
    },
    {
      type: 'tdigest' as StructureType,
      name: 'T-Digest',
      description: 'Percentile approximation for streaming data',
      operations: [
        { label: 'Add Value', action: tdigestAdd },
        { label: 'Get Quantile', action: tdigestQuantile },
      ],
      placeholder: 'Enter number (0-1 for quantile)...',
      properties: [
        'Percentile queries',
        'Streaming data',
        'Mergeable digests',
        'Accurate quantiles',
      ],
      performance: 'Streaming quantiles',
      useCases: [
        { title: 'SLA Monitoring', description: 'Track P95/P99 latency metrics' },
        { title: 'Anomaly Detection', description: 'Detect outliers in streaming data' },
      ],
    },
  ];

  const currentStructure = structures.find((s) => s.type === activeStructure)!;

  const tabs = structures.map((s) => ({
    id: s.type,
    label: s.name,
  }));

  return (
    <AppLayout
      title="Probabilistic Data Structures"
      subtitle="Powered by Example 19: Space-Efficient Algorithms (131K+ ops/sec, 100:1 space efficiency)"
      backendUrl="localhost:8019"
      backendInfo="Space Efficiency: 100:1 ratio"
    >
      <Tabs
        tabs={tabs}
        activeTab={activeStructure}
        onChange={(tabId) => {
          setActiveStructure(tabId as StructureType);
          setResult(null);
          setInput('');
        }}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Structure Info */}
        <div className="lg:col-span-1">
          <DataCard title={currentStructure.name} className="sticky top-6">
            <p className="text-sm text-neutral-600 mb-4">{currentStructure.description}</p>

            <div className="space-y-3">
              <div className="p-3 bg-neutral-50 rounded-lg">
                <h3 className="text-xs font-semibold text-neutral-700 mb-2">Key Properties</h3>
                <ul className="space-y-1 text-xs text-neutral-600">
                  {currentStructure.properties.map((prop, idx) => (
                    <li key={idx}>• {prop}</li>
                  ))}
                </ul>
              </div>

              <DataCard variant="primary">
                <h3 className="text-xs font-semibold text-primary-900 mb-1">Performance</h3>
                <div className="text-xs text-primary-700">{currentStructure.performance}</div>
              </DataCard>
            </div>
          </DataCard>
        </div>

        {/* Operations */}
        <div className="lg:col-span-2">
          <DataCard title="Operations">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Input</label>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={currentStructure.placeholder}
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="flex gap-3">
                {currentStructure.operations.map((op) => (
                  <Button
                    key={op.label}
                    onClick={op.action}
                    disabled={!input || loading}
                    loading={loading}
                  >
                    {op.label}
                  </Button>
                ))}
              </div>

              {/* Result Display */}
              {result && (
                <div
                  className={`
                    p-4 rounded-lg border
                    ${result.type === 'success' ? 'bg-success-50 border-success-200' : ''}
                    ${result.type === 'error' ? 'bg-error-50 border-error-200' : ''}
                    ${result.type === 'result' ? 'bg-primary-50 border-primary-200' : ''}
                  `}
                >
                  <div
                    className={`
                      text-sm font-medium
                      ${result.type === 'success' ? 'text-success-900' : ''}
                      ${result.type === 'error' ? 'text-error-900' : ''}
                      ${result.type === 'result' ? 'text-primary-900' : ''}
                    `}
                  >
                    {result.message}
                  </div>

                  {result.type === 'result' && (
                    <div className="mt-3 pt-3 border-t border-primary-200">
                      {result.exists !== undefined && (
                        <Badge variant={result.exists ? 'success' : 'secondary'}>
                          {result.exists ? 'Probably Exists' : 'Does Not Exist'}
                        </Badge>
                      )}
                      {result.cardinality !== undefined && (
                        <div className="text-2xl font-bold text-primary-700">
                          {result.cardinality.toLocaleString()}
                        </div>
                      )}
                      {result.frequency !== undefined && (
                        <div className="text-2xl font-bold text-primary-700">
                          {result.frequency.toLocaleString()}
                        </div>
                      )}
                      {result.value !== undefined && (
                        <div className="text-2xl font-bold text-primary-700">
                          {result.value.toFixed(4)}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </DataCard>

          {/* Use Cases */}
          <DataCard title="Common Use Cases" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentStructure.useCases.map((useCase, idx) => (
                <div key={idx} className="p-3 bg-neutral-50 rounded-lg">
                  <div className="text-sm font-semibold text-neutral-900">{useCase.title}</div>
                  <div className="text-xs text-neutral-600 mt-1">{useCase.description}</div>
                </div>
              ))}
            </div>
          </DataCard>
        </div>
      </div>
    </AppLayout>
  );
}
