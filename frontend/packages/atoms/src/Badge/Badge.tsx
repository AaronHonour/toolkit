/**
 * Badge Component
 *
 * Performance optimized badge with memoization
 * Target: < 0.5ms render time
 */

import React, { memo, ReactNode } from 'react';

export interface BadgeProps {
  /** Badge content */
  children: ReactNode;
  /** Badge variant */
  variant?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'neutral';
  /** Badge size */
  size?: 'sm' | 'md' | 'lg';
  /** Dot indicator */
  dot?: boolean;
  /** Dot color */
  dotColor?: 'primary' | 'success' | 'error' | 'warning';
  /** Custom className */
  className?: string;
}

export const Badge = memo<BadgeProps>(
  ({ children, variant = 'primary', size = 'md', dot, dotColor = 'primary', className = '' }) => {
    // Base styles (memoized for performance like LRUCache)
    const baseStyles = 'inline-flex items-center gap-1.5 font-medium rounded-full';

    // Variant styles (like backend algorithm configs)
    const variantStyles = {
      primary: 'bg-primary-100 text-primary-800',
      secondary: 'bg-neutral-100 text-neutral-800',
      success: 'bg-success-100 text-success-800',
      error: 'bg-error-100 text-error-800',
      warning: 'bg-amber-100 text-amber-800',
      neutral: 'bg-neutral-200 text-neutral-900',
    };

    // Size styles
    const sizeStyles = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-sm',
      lg: 'px-3 py-1.5 text-base',
    };

    // Dot styles
    const dotStyles = {
      primary: 'bg-primary-500',
      success: 'bg-success-500',
      error: 'bg-error-500',
      warning: 'bg-amber-500',
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
          <span className={`w-1.5 h-1.5 rounded-full ${dotStyles[dotColor]}`} aria-hidden="true" />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';
