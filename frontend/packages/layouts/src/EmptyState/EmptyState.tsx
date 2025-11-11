/**
 * EmptyState Component
 * Consistent empty state display across all applications
 */

import React from 'react';
import { Button, type ButtonProps } from '@unistax/atoms';

export interface EmptyStateProps {
  /** Icon to display (can be emoji or SVG element) */
  icon?: React.ReactNode;
  /** Title of the empty state */
  title: string;
  /** Description text */
  description?: string;
  /** Primary action button */
  action?: {
    label: string;
    onClick: () => void;
  } & Pick<ButtonProps, 'variant' | 'leftIcon'>;
  /** Secondary action button */
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState = React.memo<EmptyStateProps>(({
  icon,
  title,
  description,
  action,
  secondaryAction,
}) => {
  const defaultIcon = (
    <svg
      className="mx-auto h-12 w-12 text-neutral-400"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
      />
    </svg>
  );

  return (
    <div className="text-center py-12">
      <div className="mb-4">
        {typeof icon === 'string' ? (
          <div className="text-5xl mb-2">{icon}</div>
        ) : (
          icon || defaultIcon
        )}
      </div>

      <h3 className="text-lg font-semibold text-neutral-900 mb-2">
        {title}
      </h3>

      {description && (
        <p className="text-sm text-neutral-600 mb-6 max-w-md mx-auto">
          {description}
        </p>
      )}

      {(action || secondaryAction) && (
        <div className="flex gap-3 justify-center">
          {action && (
            <Button
              onClick={action.onClick}
              variant={action.variant || 'primary'}
              leftIcon={action.leftIcon}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              onClick={secondaryAction.onClick}
              variant="outline"
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
});

EmptyState.displayName = 'EmptyState';
