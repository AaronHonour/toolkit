/**
 * Badge Component - Professional Status Indicator
 *
 * Unified design with seamless light/dark mode transitions
 * Target: < 0.5ms render time
 */

import React, { memo, ReactNode } from 'react';

export interface BadgeProps {
  /** Badge content */
  children: ReactNode;
  /** Badge variant */
  variant?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info' | 'neutral';
  /** Badge size */
  size?: 'sm' | 'md' | 'lg';
  /** Dot indicator */
  dot?: boolean;
  /** Dot color */
  dotColor?: 'primary' | 'success' | 'error' | 'warning' | 'info';
  /** Custom className */
  className?: string;
}

export const Badge = memo<BadgeProps>(
  ({ children, variant = 'primary', size = 'md', dot, dotColor = 'primary', className = '' }) => {
    const baseStyles = 'inline-flex items-center gap-1.5 font-semibold rounded-xl transition-all duration-normal';

    // Professional variant styles with seamless dark mode
    const variantStyles = {
      primary: 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300 border border-primary-200 dark:border-primary-800',
      secondary: 'bg-secondary-100 text-secondary-800 dark:bg-secondary-900/30 dark:text-secondary-300 border border-secondary-200 dark:border-secondary-800',
      success: 'bg-success-100 text-success-800 dark:bg-success-900/30 dark:text-success-300 border border-success-200 dark:border-success-800',
      error: 'bg-error-100 text-error-800 dark:bg-error-900/30 dark:text-error-300 border border-error-200 dark:border-error-800',
      warning: 'bg-warning-100 text-warning-800 dark:bg-warning-900/30 dark:text-warning-300 border border-warning-200 dark:border-warning-800',
      info: 'bg-info-100 text-info-800 dark:bg-info-900/30 dark:text-info-300 border border-info-200 dark:border-info-800',
      neutral: 'bg-neutral-200 text-neutral-900 dark:bg-neutral-700 dark:text-neutral-100 border border-neutral-300 dark:border-neutral-600',
    };

    // Size styles
    const sizeStyles = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-3 py-1 text-sm',
      lg: 'px-4 py-1.5 text-base',
    };

    // Dot styles
    const dotStyles = {
      primary: 'bg-primary-500 dark:bg-primary-400',
      success: 'bg-success-500 dark:bg-success-400',
      error: 'bg-error-500 dark:bg-error-400',
      warning: 'bg-warning-500 dark:bg-warning-400',
      info: 'bg-info-500 dark:bg-info-400',
    };

    return (
      <span
        className={`
          ${baseStyles}
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `.trim()}
      >
        {dot && (
          <span className={`w-2 h-2 rounded-full ${dotStyles[dotColor]} animate-pulse-glow`} aria-hidden="true" />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';
