/**
 * ImpactAnalysis - Analyze the impact of changes and failures
 */

import { useState } from 'react';
import { Button, Select, Input, Badge } from '@unistax/atoms';
import { DataCard, EmptyState } from '@unistax/layouts';
import type { Service, ImpactReport, ImpactAnalysisRequest } from '../types';

interface ImpactAnalysisProps {
  services: Service[];
  onAnalyze: (request: ImpactAnalysisRequest) => Promise<ImpactReport>;
}

export function ImpactAnalysis({ services, onAnalyze }: ImpactAnalysisProps) {
  const [selectedService, setSelectedService] = useState('');
  const [changeType, setChangeType] = useState('service_failure');
  const [isBreakingChange, setIsBreakingChange] = useState(false);
  const [downtimeMinutes, setDowntimeMinutes] = useState('5');
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<ImpactReport | null>(null);

  const handleAnalyze = async () => {
    if (!selectedService) return;

    setAnalyzing(true);
    try {
      const result = await onAnalyze({
        service_name: selectedService,
        change_type: changeType,
        failure_probability: 1.0,
        is_breaking_change: isBreakingChange,
        expected_downtime_minutes: parseFloat(downtimeMinutes) || 0,
        degradation_factor: 0.5,
      });
      setReport(result);
    } catch (error) {
      console.error('Failed to analyze impact:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case 'CRITICAL':
        return 'danger';
      case 'HIGH':
        return 'warning';
      case 'MEDIUM':
        return 'info';
      default:
        return 'success';
    }
  };

  return (
    <div className="space-y-6">
      {/* Analysis Form */}
      <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          Impact Analysis Configuration
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <Select
            label="Select Service"
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            options={[
              { value: '', label: 'Choose a service...' },
              ...services.map(s => ({ value: s.name, label: s.name })),
            ]}
            fullWidth
            required
          />

          <Select
            label="Change Type"
            value={changeType}
            onChange={(e) => setChangeType(e.target.value)}
            options={[
              { value: 'service_failure', label: 'Service Failure' },
              { value: 'service_deployment', label: 'Service Deployment' },
              { value: 'breaking_change', label: 'Breaking Change' },
              { value: 'service_degradation', label: 'Service Degradation' },
            ]}
            fullWidth
          />

          {changeType === 'breaking_change' && (
            <div className="md:col-span-2">
              <label className="flex items-center gap-2 text-sm text-neutral-700 dark:text-neutral-300">
                <input
                  type="checkbox"
                  checked={isBreakingChange}
                  onChange={(e) => setIsBreakingChange(e.target.checked)}
                  className="rounded border-neutral-300"
                />
                <span>This is a breaking API change</span>
              </label>
            </div>
          )}

          {(changeType === 'breaking_change' || changeType === 'service_deployment') && (
            <Input
              label="Expected Downtime (minutes)"
              type="number"
              value={downtimeMinutes}
              onChange={(e) => setDowntimeMinutes(e.target.value)}
              min="0"
              step="0.5"
              fullWidth
            />
          )}
        </div>

        <Button
          variant="primary"
          onClick={handleAnalyze}
          loading={analyzing}
          disabled={!selectedService}
        >
          Analyze Impact
        </Button>
      </div>

      {/* Results */}
      {report ? (
        <div className="space-y-6">
          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <DataCard
              title="Risk Level"
              badge={
                <Badge variant={getRiskBadgeVariant(report.risk_level)} size="lg">
                  {report.risk_level}
                </Badge>
              }
            >
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Overall risk assessment for this change
              </p>
            </DataCard>

            <DataCard title="Total Affected">
              <div className="text-3xl font-bold text-primary-500">
                {report.total_affected}
              </div>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Services impacted
              </p>
            </DataCard>

            <DataCard title="Impact Type">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-neutral-600 dark:text-neutral-400">Direct:</span>
                  <Badge variant="danger" size="sm">
                    {report.direct_impact.length}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600 dark:text-neutral-400">Indirect:</span>
                  <Badge variant="warning" size="sm">
                    {report.indirect_impact.length}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600 dark:text-neutral-400">Cascading:</span>
                  <Badge variant="info" size="sm">
                    {report.cascading_impact.length}
                  </Badge>
                </div>
              </div>
            </DataCard>
          </div>

          {/* Direct Impact */}
          {report.direct_impact.length > 0 && (
            <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
                Direct Impact
              </h3>
              <div className="space-y-3">
                {report.direct_impact.map((impact) => (
                  <div
                    key={impact.service}
                    className="flex items-start justify-between gap-4 p-3 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="font-medium text-neutral-900 dark:text-white mb-1">
                        {impact.service}
                      </div>
                      <div className="text-sm text-neutral-600 dark:text-neutral-400">
                        Probability: {(impact.probability * 100).toFixed(0)}%
                        {impact.mitigation && ` • ${impact.mitigation}`}
                      </div>
                    </div>
                    <Badge variant="danger" size="sm">
                      Level {impact.impact_level}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Indirect & Cascading Impact */}
          {(report.indirect_impact.length > 0 || report.cascading_impact.length > 0) && (
            <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
                Indirect & Cascading Impact
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...report.indirect_impact, ...report.cascading_impact].map((impact) => (
                  <div
                    key={impact.service}
                    className="p-3 bg-neutral-50 dark:bg-dark-300 rounded-lg"
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="font-medium text-neutral-900 dark:text-white">
                        {impact.service}
                      </div>
                      <Badge
                        variant={impact.impact_type === 'indirect' ? 'warning' : 'info'}
                        size="sm"
                      >
                        {impact.impact_type}
                      </Badge>
                    </div>
                    <div className="text-xs text-neutral-600 dark:text-neutral-400">
                      {(impact.probability * 100).toFixed(0)}% probability
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Pre-Change Actions */}
          {report.pre_change_actions.length > 0 && (
            <div className="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-warning-900 dark:text-warning-400 mb-3 flex items-center gap-2">
                <span>⚠️</span>
                Pre-Change Actions
              </h3>
              <ul className="space-y-2 text-sm text-warning-800 dark:text-warning-300">
                {report.pre_change_actions.map((action, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span>•</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Monitoring Required */}
          {report.monitoring_required.length > 0 && (
            <div className="bg-info-50 dark:bg-info-900/20 border border-info-200 dark:border-info-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-info-900 dark:text-info-400 mb-3 flex items-center gap-2">
                <span>📊</span>
                Monitoring Required
              </h3>
              <ul className="space-y-2 text-sm text-info-800 dark:text-info-300">
                {report.monitoring_required.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span>•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Rollback Plan */}
          {report.rollback_plan && (
            <div className="bg-neutral-50 dark:bg-dark-300 border border-neutral-200 dark:border-dark-100 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-3 flex items-center gap-2">
                <span>🔄</span>
                Rollback Plan
              </h3>
              <p className="text-sm text-neutral-700 dark:text-neutral-300">
                {report.rollback_plan}
              </p>
            </div>
          )}
        </div>
      ) : !analyzing ? (
        <EmptyState
          icon="🎯"
          title="No Analysis Results"
          description="Select a service and change type above, then click 'Analyze Impact' to see results."
        />
      ) : null}
    </div>
  );
}
