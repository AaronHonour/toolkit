/**
 * Spinner Component - Professional Loading Indicator
 *
 * Unified design with brand colors and dark mode support
 * Target: 60fps animation (< 16ms per frame)
 */

import React, { memo } from 'react';

export interface SpinnerProps {
  /** Spinner size */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Spinner color */
  color?: 'primary' | 'secondary' | 'white' | 'neutral';
  /** Custom className */
  className?: string;
  /** Accessibility label */
  label?: string;
}

export const Spinner = memo<SpinnerProps>(
  ({ size = 'md', color = 'primary', className = '', label = 'Loading...' }) => {
    const sizeStyles = {
      xs: 'w-3 h-3',
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
      xl: 'w-12 h-12',
    };

    // Brand-aligned color styles with dark mode
    const colorStyles = {
      primary: 'text-primary-600 dark:text-primary-400',
      secondary: 'text-secondary-600 dark:text-secondary-400',
      white: 'text-white',
      neutral: 'text-neutral-600 dark:text-neutral-400',
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
