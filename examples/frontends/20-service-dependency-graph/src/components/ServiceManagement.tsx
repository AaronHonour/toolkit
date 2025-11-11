/**
 * ServiceManagement - Service CRUD interface
 */

import { useState } from 'react';
import { Button, Input, Select, Badge } from '@unistax/atoms';
import { DataTable, Modal, EmptyState } from '@unistax/layouts';
import type { Service, CreateServiceRequest } from '../types';

interface ServiceManagementProps {
  services: Service[];
  onCreateService: (service: CreateServiceRequest) => Promise<void>;
  onDeleteService: (serviceName: string) => Promise<void>;
}

export function ServiceManagement({
  services,
  onCreateService,
  onDeleteService,
}: ServiceManagementProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [serviceType, setServiceType] = useState('api');
  const [endpoints, setEndpoints] = useState('');

  const handleCreate = async () => {
    if (!name) return;

    setIsSubmitting(true);
    try {
      await onCreateService({
        name,
        service_type: serviceType,
        endpoints: endpoints ? endpoints.split(',').map(e => e.trim()) : [],
        metadata: {},
      });

      // Reset form
      setName('');
      setServiceType('api');
      setEndpoints('');
      setShowCreateModal(false);
    } catch (error) {
      console.error('Failed to create service:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (serviceName: string) => {
    if (!confirm(`Are you sure you want to delete service "${serviceName}"?`)) {
      return;
    }

    try {
      await onDeleteService(serviceName);
    } catch (error) {
      console.error('Failed to delete service:', error);
    }
  };

  const getHealthBadgeVariant = (health: number): 'success' | 'warning' | 'danger' => {
    if (health >= 0.9) return 'success';
    if (health >= 0.7) return 'warning';
    return 'danger';
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
            Services
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">
            Manage registered services in the dependency graph
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowCreateModal(true)}
        >
          Add Service
        </Button>
      </div>

      {services.length === 0 ? (
        <EmptyState
          icon="🔍"
          title="No Services"
          description="Get started by adding your first service to the dependency graph."
          actions={[
            <Button key="add" variant="primary" onClick={() => setShowCreateModal(true)}>
              Add Service
            </Button>,
          ]}
        />
      ) : (
        <DataTable
          columns={[
            { key: 'name', header: 'Name', sortable: true },
            {
              key: 'service_type',
              header: 'Type',
              render: (value) => (
                <Badge variant="primary" size="sm">
                  {value as string}
                </Badge>
              ),
            },
            {
              key: 'health_score',
              header: 'Health',
              render: (value) => {
                const health = value as number;
                return (
                  <Badge
                    variant={getHealthBadgeVariant(health)}
                    size="sm"
                  >
                    {Math.round(health * 100)}%
                  </Badge>
                );
              },
            },
            {
              key: 'endpoints',
              header: 'Endpoints',
              render: (value) => (value as string[]).length,
            },
            {
              key: 'actions',
              header: 'Actions',
              render: (_, row) => (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleDelete((row as Service).name)}
                >
                  Delete
                </Button>
              ),
            },
          ]}
          data={services}
          rowKey="id"
        />
      )}

      {/* Create Service Modal */}
      {showCreateModal && (
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Add New Service"
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
                disabled={!name}
              >
                Create Service
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Service Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., user-service"
              required
              fullWidth
            />

            <Select
              label="Service Type"
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              options={[
                { value: 'api', label: 'API' },
                { value: 'gateway', label: 'Gateway' },
                { value: 'database', label: 'Database' },
                { value: 'cache', label: 'Cache' },
                { value: 'queue', label: 'Queue' },
                { value: 'storage', label: 'Storage' },
                { value: 'worker', label: 'Worker' },
                { value: 'external', label: 'External' },
              ]}
              fullWidth
            />

            <Input
              label="Endpoints"
              value={endpoints}
              onChange={(e) => setEndpoints(e.target.value)}
              placeholder="Comma-separated: /users, /orders"
              helperText="Optional: List of service endpoints"
              fullWidth
            />
          </div>
        </Modal>
      )}
    </div>
  );
}
