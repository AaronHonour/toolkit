/**
 * Spinner Component
 *
 * Performance optimized loading spinner
 * Target: 60fps animation (< 16ms per frame)
 */

import React, { memo } from 'react';

export interface SpinnerProps {
  /** Spinner size */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Spinner color */
  color?: 'primary' | 'white' | 'neutral';
  /** Custom className */
  className?: string;
  /** Accessibility label */
  label?: string;
}

export const Spinner = memo<SpinnerProps>(
  ({ size = 'md', color = 'primary', className = '', label = 'Loading...' }) => {
    // Size styles (optimized for performance)
    const sizeStyles = {
      xs: 'w-3 h-3',
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
      xl: 'w-12 h-12',
    };

    // Color styles
    const colorStyles = {
      primary: 'text-primary-600',
      white: 'text-white',
      neutral: 'text-neutral-600',
    };

    // Border width based on size
    const borderWidth = {
      xs: 'border',
      sm: 'border-2',
      md: 'border-2',
      lg: 'border-[3px]',
      xl: 'border-4',
    };

    return (
      <div className="inline-flex items-center justify-center" role="status" aria-label={label}>
        <svg
          className={`
            animate-spin
            ${sizeStyles[size]}
            ${colorStyles[color]}
            ${className}
          `.trim()}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <span className="sr-only">{label}</span>
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';
