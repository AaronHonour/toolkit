/**
 * DataCard Component - Professional Card Container
 *
 * Sophisticated card with proper elevation and visual hierarchy
 */

import React from 'react';

export interface DataCardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  headerActions?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'default' | 'elevated' | 'bordered';
}

export const DataCard = React.memo<DataCardProps>(({
  title,
  children,
  className = '',
  headerActions,
  footer,
  variant = 'elevated',
}) => {
  const variantStyles = {
    default: 'bg-white dark:bg-dark-200 border border-neutral-200 dark:border-dark-100',
    elevated: 'bg-white dark:bg-dark-200 shadow-lg border border-neutral-200 dark:border-dark-100 hover:shadow-xl transition-shadow',
    bordered: 'bg-white dark:bg-dark-200 border-2 border-neutral-300 dark:border-dark-100',
  };

  return (
    <div className={`rounded-2xl overflow-hidden ${variantStyles[variant]} ${className}`}>
      {title && (
        <div className="px-6 py-4 border-b border-neutral-200 dark:border-dark-100 bg-neutral-50 dark:bg-dark-100">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white tracking-tight">
              {title}
            </h2>
            {headerActions && (
              <div className="flex items-center gap-2">
                {headerActions}
              </div>
            )}
          </div>
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
      {footer && (
        <div className="px-6 py-4 border-t border-neutral-200 dark:border-dark-100 bg-neutral-50 dark:bg-dark-100">
          {footer}
        </div>
      )}
    </div>
  );
});

DataCard.displayName = 'DataCard';
