/**
 * StatsBar Component
 * Consistent statistics display bar for dashboards
 */

import React from 'react';

export interface Stat {
  label: string;
  value: string | number;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  variant?: 'default' | 'success' | 'warning' | 'error';
}

export interface StatsBarProps {
  stats: Stat[];
  variant?: 'compact' | 'expanded';
}

export const StatsBar = React.memo<StatsBarProps>(({
  stats,
  variant = 'compact',
}) => {
  const getVariantColor = (statVariant?: Stat['variant']) => {
    switch (statVariant) {
      case 'success':
        return 'text-success-700';
      case 'warning':
        return 'text-warning-700';
      case 'error':
        return 'text-error-700';
      default:
        return 'text-primary-700';
    }
  };

  const getTrendColor = (direction: 'up' | 'down') => {
    return direction === 'up' ? 'text-success-600' : 'text-error-600';
  };

  if (variant === 'expanded') {
    return (
      <div className="bg-white border border-neutral-200 rounded-lg shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-neutral-200">
          {stats.map((stat, index) => (
            <div key={index} className="p-6">
              <div className="text-sm font-medium text-neutral-600 mb-1">
                {stat.label}
              </div>
              <div className="flex items-baseline gap-2">
                <div className={`text-2xl font-bold ${getVariantColor(stat.variant)}`}>
                  {stat.value}
                </div>
                {stat.trend && (
                  <div className={`text-sm font-medium ${getTrendColor(stat.trend.direction)}`}>
                    {stat.trend.direction === 'up' ? '↑' : '↓'} {Math.abs(stat.trend.value)}%
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // compact variant
  return (
    <div className="bg-primary-50 border-b border-primary-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex flex-wrap gap-6 text-sm">
          {stats.map((stat, index) => (
            <div key={index} className="flex items-center gap-2">
              <span className="font-semibold text-primary-900">{stat.label}:</span>
              <span className={getVariantColor(stat.variant)}>{stat.value}</span>
              {stat.trend && (
                <span className={`text-xs ${getTrendColor(stat.trend.direction)}`}>
                  {stat.trend.direction === 'up' ? '↑' : '↓'} {Math.abs(stat.trend.value)}%
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

StatsBar.displayName = 'StatsBar';
