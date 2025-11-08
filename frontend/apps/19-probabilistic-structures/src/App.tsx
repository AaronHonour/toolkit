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
    },
  ];

  const currentStructure = structures.find((s) => s.type === activeStructure)!;

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-neutral-900">🎲 Probabilistic Data Structures</h1>
          <p className="text-sm text-neutral-600 mt-1">
            Powered by Example 19: Space-Efficient Algorithms (131K+ ops/sec, 100:1 space
            efficiency)
          </p>
        </div>
      </header>

      {/* Structure Tabs */}
      <div className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-2 overflow-x-auto">
            {structures.map((structure) => (
              <button
                key={structure.type}
                onClick={() => {
                  setActiveStructure(structure.type);
                  setResult(null);
                  setInput('');
                }}
                className={`
                  px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
                  ${
                    activeStructure === structure.type
                      ? 'border-primary-600 text-primary-700'
                      : 'border-transparent text-neutral-600 hover:text-neutral-900 hover:border-neutral-300'
                  }
                `}
              >
                {structure.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Structure Info */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 sticky top-6">
              <h2 className="text-lg font-semibold text-neutral-900 mb-2">
                {currentStructure.name}
              </h2>
              <p className="text-sm text-neutral-600 mb-4">{currentStructure.description}</p>

              <div className="space-y-3">
                <div className="p-3 bg-neutral-50 rounded-lg">
                  <h3 className="text-xs font-semibold text-neutral-700 mb-2">Key Properties</h3>
                  <ul className="space-y-1 text-xs text-neutral-600">
                    {activeStructure === 'bloom' && (
                      <>
                        <li>• No false negatives</li>
                        <li>• Possible false positives</li>
                        <li>• O(1) membership testing</li>
                        <li>• Space-efficient</li>
                      </>
                    )}
                    {activeStructure === 'hll' && (
                      <>
                        <li>• ~2% accuracy</li>
                        <li>• Fixed memory usage</li>
                        <li>• Mergeable sketches</li>
                        <li>• Billions of uniques</li>
                      </>
                    )}
                    {activeStructure === 'cms' && (
                      <>
                        <li>• Frequency estimation</li>
                        <li>• Configurable accuracy</li>
                        <li>• No deletions</li>
                        <li>• Sublinear space</li>
                      </>
                    )}
                    {activeStructure === 'tdigest' && (
                      <>
                        <li>• Percentile queries</li>
                        <li>• Streaming data</li>
                        <li>• Mergeable digests</li>
                        <li>• Accurate quantiles</li>
                      </>
                    )}
                  </ul>
                </div>

                <div className="p-3 bg-primary-50 rounded-lg border border-primary-200">
                  <h3 className="text-xs font-semibold text-primary-900 mb-1">Performance</h3>
                  <div className="text-xs text-primary-700">
                    {activeStructure === 'bloom' && '131K+ ops/sec'}
                    {activeStructure === 'hll' && '100:1 space efficiency'}
                    {activeStructure === 'cms' && '&gt; 99% accuracy'}
                    {activeStructure === 'tdigest' && 'Streaming quantiles'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Operations */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">Operations</h2>

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
            </div>

            {/* Use Cases */}
            <div className="mt-6 bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">Common Use Cases</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activeStructure === 'bloom' && (
                  <>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">Cache Filtering</div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Check if key might be in cache before lookup
                      </div>
                    </div>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">
                        Malicious URL Detection
                      </div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Quick check against known bad URLs
                      </div>
                    </div>
                  </>
                )}
                {activeStructure === 'hll' && (
                  <>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">Unique Visitors</div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Count distinct users with minimal memory
                      </div>
                    </div>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">
                        Distributed Cardinality
                      </div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Merge counts from multiple servers
                      </div>
                    </div>
                  </>
                )}
                {activeStructure === 'cms' && (
                  <>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">Top-K Items</div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Track most frequent items in stream
                      </div>
                    </div>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">Rate Limiting</div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Approximate request counts per user
                      </div>
                    </div>
                  </>
                )}
                {activeStructure === 'tdigest' && (
                  <>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">SLA Monitoring</div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Track P95/P99 latency metrics
                      </div>
                    </div>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-sm font-semibold text-neutral-900">
                        Anomaly Detection
                      </div>
                      <div className="text-xs text-neutral-600 mt-1">
                        Detect outliers in streaming data
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-neutral-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-neutral-600">
            <div>
              <span className="font-semibold">Backend:</span> localhost:8019
            </div>
            <div>
              <span className="font-semibold">Space Efficiency:</span> 100:1 ratio
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
