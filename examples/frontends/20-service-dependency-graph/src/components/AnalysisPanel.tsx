/**
 * AnalysisPanel - Display analysis results (circular deps, criticality, bottlenecks)
 */

import { Badge } from '@unistax/atoms';
import { DataTable, EmptyState, DataCard } from '@unistax/layouts';
import type { AnalysisReport } from '../types';

interface AnalysisPanelProps {
  report: AnalysisReport | null;
  loading: boolean;
}

export function AnalysisPanel({ report, loading }: AnalysisPanelProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-neutral-600 dark:text-neutral-400">
          Analyzing dependency graph...
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <EmptyState
        icon="📊"
        title="No Analysis Available"
        description="Analysis will appear once services and dependencies are added."
      />
    );
  }

  const topCritical = report.critical_services.slice(0, 10);
  const topBottlenecks = Object.entries(report.bottlenecks)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  return (
    <div className="space-y-6">
      {/* Insights and Warnings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Insights */}
        <DataCard
          title="Insights"
          badge={
            <Badge variant="info" size="sm" withDot>
              {report.insights.length}
            </Badge>
          }
        >
          {report.insights.length > 0 ? (
            <ul className="space-y-2 text-sm text-neutral-700 dark:text-neutral-300">
              {report.insights.map((insight, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-primary-500">💡</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              No insights available
            </p>
          )}
        </DataCard>

        {/* Warnings */}
        <DataCard
          title="Warnings"
          badge={
            <Badge variant="warning" size="sm" withDot>
              {report.warnings.length}
            </Badge>
          }
        >
          {report.warnings.length > 0 ? (
            <ul className="space-y-2 text-sm text-neutral-700 dark:text-neutral-300">
              {report.warnings.map((warning, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-warning-500">⚠️</span>
                  <span>{warning}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-success-600 dark:text-success-400">
              ✓ No warnings - system looks healthy!
            </p>
          )}
        </DataCard>
      </div>

      {/* Circular Dependencies */}
      <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
            Circular Dependencies
          </h3>
          <Badge
            variant={report.circular_dependencies.length > 0 ? 'danger' : 'success'}
            size="sm"
          >
            {report.circular_dependencies.length}
          </Badge>
        </div>

        {report.circular_dependencies.length > 0 ? (
          <div className="space-y-3">
            {report.circular_dependencies.map((circular, idx) => (
              <div
                key={idx}
                className="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg p-4"
              >
                <div className="flex items-start gap-3">
                  <span className="text-danger-500 text-lg">🔄</span>
                  <div className="flex-1">
                    <div className="font-medium text-danger-700 dark:text-danger-400 mb-1">
                      Cycle of {circular.cycle_length} service{circular.cycle_length !== 1 ? 's' : ''}
                    </div>
                    <div className="text-sm text-danger-600 dark:text-danger-300 font-mono">
                      {circular.cycle_path}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-success-600 dark:text-success-400">
            ✓ No circular dependencies detected
          </p>
        )}
      </div>

      {/* Critical Services */}
      <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          Critical Services
        </h3>

        {topCritical.length > 0 ? (
          <DataTable
            columns={[
              {
                key: 'rank',
                header: 'Rank',
                render: (value) => (
                  <Badge variant="primary" size="sm">
                    #{value}
                  </Badge>
                ),
              },
              { key: 'service', header: 'Service', sortable: true },
              {
                key: 'score',
                header: 'Score',
                render: (value) => {
                  const score = value as number;
                  return (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-neutral-200 dark:bg-dark-100 rounded-full h-2">
                        <div
                          className="bg-primary-500 h-2 rounded-full"
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-neutral-600 dark:text-neutral-400 w-12">
                        {(score * 100).toFixed(0)}%
                      </span>
                    </div>
                  );
                },
              },
              {
                key: 'is_critical',
                header: 'Critical',
                render: (value) =>
                  value ? (
                    <Badge variant="danger" size="sm">
                      Yes
                    </Badge>
                  ) : (
                    <Badge variant="success" size="sm">
                      No
                    </Badge>
                  ),
              },
              {
                key: 'reasons',
                header: 'Reasons',
                render: (value) => {
                  const reasons = value as string[];
                  return reasons.length > 0 ? (
                    <ul className="text-xs text-neutral-600 dark:text-neutral-400 space-y-1">
                      {reasons.map((reason, idx) => (
                        <li key={idx}>• {reason}</li>
                      ))}
                    </ul>
                  ) : null;
                },
              },
            ]}
            data={topCritical}
            rowKey="service"
            compact
          />
        ) : (
          <EmptyState
            icon="📊"
            title="No Data"
            description="No services to analyze"
          />
        )}
      </div>

      {/* Bottlenecks */}
      <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          Bottleneck Services
        </h3>

        {topBottlenecks.length > 0 ? (
          <div className="space-y-3">
            {topBottlenecks.map(([service, score], idx) => (
              <div
                key={service}
                className="flex items-center gap-4 p-3 bg-neutral-50 dark:bg-dark-300 rounded-lg"
              >
                <Badge variant="warning" size="sm">
                  #{idx + 1}
                </Badge>
                <div className="flex-1">
                  <div className="font-medium text-neutral-900 dark:text-white mb-1">
                    {service}
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-neutral-200 dark:bg-dark-100 rounded-full h-2">
                      <div
                        className="bg-warning-500 h-2 rounded-full"
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-neutral-600 dark:text-neutral-400 w-12">
                      {(score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            No bottlenecks identified
          </p>
        )}
      </div>

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <div className="bg-info-50 dark:bg-info-900/20 border border-info-200 dark:border-info-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-info-900 dark:text-info-400 mb-3 flex items-center gap-2">
            <span>💡</span>
            Recommendations
          </h3>
          <ul className="space-y-2 text-sm text-info-800 dark:text-info-300">
            {report.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-info-500">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Deployment Order */}
      {report.deployment_order && (
        <div className="bg-white dark:bg-dark-200 rounded-lg shadow-sm border border-neutral-200 dark:border-dark-100 p-6">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-3">
            Safe Deployment Order
          </h3>
          <div className="flex flex-wrap gap-2">
            {report.deployment_order.map((service, idx) => (
              <div key={service} className="flex items-center gap-2">
                <Badge variant="primary" size="sm">
                  {idx + 1}
                </Badge>
                <span className="text-sm text-neutral-700 dark:text-neutral-300">
                  {service}
                </span>
                {idx < report.deployment_order!.length - 1 && (
                  <span className="text-neutral-400">→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
