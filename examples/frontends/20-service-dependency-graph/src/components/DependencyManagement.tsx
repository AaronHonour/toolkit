/**
 * DependencyManagement - Manage dependencies between services
 */

import { useState } from 'react';
import { Button, Select, Input, Badge } from '@unistax/atoms';
import { DataTable, Modal, EmptyState } from '@unistax/layouts';
import type { Service, Dependency, CreateDependencyRequest } from '../types';

interface DependencyManagementProps {
  services: Service[];
  dependencies: Dependency[];
  onCreateDependency: (dep: CreateDependencyRequest) => Promise<void>;
}

export function DependencyManagement({
  services,
  dependencies,
  onCreateDependency,
}: DependencyManagementProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [depType, setDepType] = useState('api_call');
  const [weight, setWeight] = useState('1.0');

  const handleCreate = async () => {
    if (!source || !target) return;

    setIsSubmitting(true);
    try {
      await onCreateDependency({
        source,
        target,
        dependency_type: depType,
        weight: parseFloat(weight) || 1.0,
        metadata: {},
      });

      // Reset form
      setSource('');
      setTarget('');
      setDepType('api_call');
      setWeight('1.0');
      setShowCreateModal(false);
    } catch (error) {
      console.error('Failed to create dependency:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
            Dependencies
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">
            Service-to-service dependency relationships
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowCreateModal(true)}
          disabled={services.length < 2}
        >
          Add Dependency
        </Button>
      </div>

      {dependencies.length === 0 ? (
        <EmptyState
          icon="🔗"
          title="No Dependencies"
          description="Add dependencies between services to build the dependency graph."
          actions={
            services.length >= 2 ? [
              <Button key="add" variant="primary" onClick={() => setShowCreateModal(true)}>
                Add Dependency
              </Button>,
            ] : []
          }
        />
      ) : (
        <DataTable
          columns={[
            { key: 'source', header: 'Source', sortable: true },
            {
              key: 'target',
              header: 'Target',
              sortable: true,
              render: (value) => (
                <span className="flex items-center gap-2">
                  <span className="text-neutral-400">→</span>
                  {value as string}
                </span>
              ),
            },
            {
              key: 'dependency_type',
              header: 'Type',
              render: (value) => (
                <Badge variant="primary" size="sm">
                  {(value as string).replace('_', ' ')}
                </Badge>
              ),
            },
            {
              key: 'weight',
              header: 'Weight',
              render: (value) => {
                const w = value as number;
                return (
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-neutral-200 dark:bg-dark-100 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full"
                        style={{ width: `${Math.min(100, w * 50)}%` }}
                      />
                    </div>
                    <span className="text-sm text-neutral-600 dark:text-neutral-400">
                      {w.toFixed(1)}
                    </span>
                  </div>
                );
              },
            },
            {
              key: 'error_rate',
              header: 'Error Rate',
              render: (value) => {
                const rate = value as number;
                return rate > 0 ? (
                  <Badge variant="danger" size="sm">
                    {(rate * 100).toFixed(1)}%
                  </Badge>
                ) : (
                  <Badge variant="success" size="sm">
                    0%
                  </Badge>
                );
              },
            },
          ]}
          data={dependencies}
          rowKey="id"
        />
      )}

      {/* Create Dependency Modal */}
      {showCreateModal && (
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Add New Dependency"
          footer={
            <>
              <Button
                variant="outline"
                onClick={() => setShowCreateModal(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleCreate}
                loading={isSubmitting}
                disabled={!source || !target || source === target}
              >
                Create Dependency
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Source Service"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              options={[
                { value: '', label: 'Select source service...' },
                ...services.map(s => ({ value: s.name, label: s.name })),
              ]}
              required
              fullWidth
            />

            <Select
              label="Target Service"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              options={[
                { value: '', label: 'Select target service...' },
                ...services.filter(s => s.name !== source).map(s => ({ value: s.name, label: s.name })),
              ]}
              required
              fullWidth
            />

            <Select
              label="Dependency Type"
              value={depType}
              onChange={(e) => setDepType(e.target.value)}
              options={[
                { value: 'api_call', label: 'API Call' },
                { value: 'database', label: 'Database' },
                { value: 'message_queue', label: 'Message Queue' },
                { value: 'cache', label: 'Cache' },
                { value: 'storage', label: 'Storage' },
                { value: 'external_service', label: 'External Service' },
              ]}
              fullWidth
            />

            <Input
              label="Weight"
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              min="0"
              step="0.1"
              helperText="Relative importance/frequency (0.0 - 10.0)"
              fullWidth
            />
          </div>
        </Modal>
      )}
    </div>
  );
}
