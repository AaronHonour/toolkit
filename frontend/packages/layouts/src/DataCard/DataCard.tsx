/**
 * DataCard Component
 * Reusable card component for displaying data items
 */

import React from 'react';
import { Badge, type BadgeProps } from '@frontend-toolkit/atoms';

export interface DataCardProps {
  /** Card title */
  title: string;
  /** Subtitle or secondary text */
  subtitle?: string;
  /** Badge to display */
  badge?: {
    label: string;
    variant?: BadgeProps['variant'];
  };
  /** Additional metadata */
  metadata?: Array<{
    label: string;
    value: string | number;
  }>;
  /** Tags or labels */
  tags?: string[];
  /** Card action on click */
  onClick?: () => void;
  /** Additional actions (buttons, menu) */
  actions?: React.ReactNode;
  /** Children content */
  children?: React.ReactNode;
  /** Custom className */
  className?: string;
}

export const DataCard = React.memo<DataCardProps>(({
  title,
  subtitle,
  badge,
  metadata,
  tags,
  onClick,
  actions,
  children,
  className = '',
}) => {
  const isClickable = Boolean(onClick);

  return (
    <div
      className={`
        bg-white rounded-lg border border-neutral-200 p-4
        ${isClickable ? 'hover:shadow-md cursor-pointer' : 'shadow-sm'}
        transition-shadow
        ${className}
      `}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-neutral-900 truncate">{title}</h3>
          {subtitle && (
            <p className="text-xs text-neutral-500 font-mono mt-0.5">{subtitle}</p>
          )}
        </div>
        <div className="ml-2 flex items-center gap-2">
          {badge && (
            <Badge variant={badge.variant || 'secondary'} size="sm">
              {badge.label}
            </Badge>
          )}
          {actions}
        </div>
      </div>

      {/* Content */}
      {children && (
        <div className="text-sm text-neutral-600 mb-3">
          {children}
        </div>
      )}

      {/* Metadata */}
      {metadata && metadata.length > 0 && (
        <div className="flex flex-wrap gap-4 mb-3">
          {metadata.map((item, index) => (
            <div key={index}>
              <span className="text-xs text-neutral-500">{item.label}: </span>
              <span className="text-sm font-medium text-neutral-900">{item.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Tags */}
      {tags && tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-0.5 text-xs bg-neutral-100 text-neutral-700 rounded"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
});

DataCard.displayName = 'DataCard';
