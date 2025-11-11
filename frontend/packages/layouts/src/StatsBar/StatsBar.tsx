/**
 * StatsBar Component - Professional Metrics Display
 *
 * Redesigned for sophisticated visual hierarchy and polish
 */

import React from 'react';

export interface StatItem {
  label: string;
  value: string | number;
  variant?: 'default' | 'success' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

export interface StatsBarProps {
  stats: StatItem[];
  variant?: 'compact' | 'cards';
  className?: string;
}

const variantColors = {
  default: {
    bg: 'bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950/50 dark:to-primary-900/50',
    border: 'border-primary-200 dark:border-primary-800',
    text: 'text-primary-700 dark:text-primary-300',
    value: 'text-primary-900 dark:text-primary-100',
  },
  success: {
    bg: 'bg-gradient-to-br from-success-50 to-success-100 dark:from-success-950/50 dark:to-success-900/50',
    border: 'border-success-200 dark:border-success-800',
    text: 'text-success-700 dark:text-success-300',
    value: 'text-success-900 dark:text-success-100',
  },
  warning: {
    bg: 'bg-gradient-to-br from-warning-50 to-warning-100 dark:from-warning-950/50 dark:to-warning-900/50',
    border: 'border-warning-200 dark:border-warning-800',
    text: 'text-warning-700 dark:text-warning-300',
    value: 'text-warning-900 dark:text-warning-100',
  },
  error: {
    bg: 'bg-gradient-to-br from-error-50 to-error-100 dark:from-error-950/50 dark:to-error-900/50',
    border: 'border-error-200 dark:border-error-800',
    text: 'text-error-700 dark:text-error-300',
    value: 'text-error-900 dark:text-error-100',
  },
};

export const StatsBar = React.memo<StatsBarProps>(({ stats, variant = 'compact', className = '' }) => {
  if (variant === 'compact') {
    return (
      <div className={`bg-white dark:bg-dark-200 border-b border-neutral-200 dark:border-dark-100 shadow-sm ${className}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {stats.map((stat, index) => {
              const colors = variantColors[stat.variant || 'default'];
              return (
                <div
                  key={index}
                  className={`
                    relative overflow-hidden rounded-xl border-2 ${colors.border} ${colors.bg}
                    p-4 transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5
                  `}
                >
                  <div className="relative z-10">
                    <p className={`text-sm font-medium ${colors.text} mb-1`}>
                      {stat.label}
                    </p>
                    <div className="flex items-baseline gap-2">
                      <p className={`text-3xl font-bold ${colors.value} tracking-tight`}>
                        {stat.value}
                      </p>
                      {stat.trend && stat.trendValue && (
                        <span className={`
                          text-xs font-semibold flex items-center gap-0.5
                          ${stat.trend === 'up' ? 'text-success-600' : stat.trend === 'down' ? 'text-error-600' : 'text-neutral-600'}
                        `}>
                          {stat.trend === 'up' && '↑'}
                          {stat.trend === 'down' && '↓'}
                          {stat.trendValue}
                        </span>
                      )}
                    </div>
                  </div>
                  {/* Decorative gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // Cards variant
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${className}`}>
      {stats.map((stat, index) => {
        const colors = variantColors[stat.variant || 'default'];
        return (
          <div
            key={index}
            className={`
              relative overflow-hidden rounded-2xl border-2 ${colors.border} ${colors.bg}
              p-6 shadow-lg transition-all duration-300 hover:shadow-xl hover:-translate-y-1
            `}
          >
            <div className="relative z-10">
              <p className={`text-sm font-semibold uppercase tracking-wider ${colors.text} mb-2`}>
                {stat.label}
              </p>
              <div className="flex items-baseline gap-3">
                <p className={`text-4xl font-bold ${colors.value} tracking-tight`}>
                  {stat.value}
                </p>
                {stat.trend && stat.trendValue && (
                  <span className={`
                    text-sm font-semibold flex items-center gap-1 px-2 py-1 rounded-lg
                    ${stat.trend === 'up' ? 'bg-success-100 text-success-700' : stat.trend === 'down' ? 'bg-error-100 text-error-700' : 'bg-neutral-100 text-neutral-700'}
                  `}>
                    {stat.trend === 'up' && '↑'}
                    {stat.trend === 'down' && '↓'}
                    {stat.trendValue}
                  </span>
                )}
              </div>
            </div>
            {/* Sophisticated gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none" />
            <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-2xl" />
          </div>
        );
      })}
    </div>
  );
});

StatsBar.displayName = 'StatsBar';
