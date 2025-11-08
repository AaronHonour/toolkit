/**
 * Icon Component
 *
 * Performance optimized icon wrapper
 * Target: < 0.5ms render time
 */

import React, { memo } from 'react';

export interface IconProps {
  /** Icon name (from lucide-react or custom) */
  name?: string;
  /** Icon size */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Icon color */
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'neutral' | 'white';
  /** Custom className */
  className?: string;
  /** SVG children (custom icon path) */
  children?: React.ReactNode;
  /** Accessibility label */
  'aria-label'?: string;
}

export const Icon = memo<IconProps>(
  ({
    size = 'md',
    color = 'neutral',
    className = '',
    children,
    'aria-label': ariaLabel,
    ...props
  }) => {
    // Size styles (optimized like backend fast_hash)
    const sizeStyles = {
      xs: 'w-3 h-3',
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
      xl: 'w-8 h-8',
    };

    // Color styles
    const colorStyles = {
      primary: 'text-primary-600',
      secondary: 'text-neutral-600',
      success: 'text-success-600',
      error: 'text-error-600',
      warning: 'text-amber-600',
      neutral: 'text-neutral-500',
      white: 'text-white',
    };

    return (
      <svg
        className={`
          inline-block flex-shrink-0
          ${sizeStyles[size]}
          ${colorStyles[color]}
          ${className}
        `.trim()}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
        aria-label={ariaLabel}
        aria-hidden={!ariaLabel}
        {...props}
      >
        {children}
      </svg>
    );
  }
);

Icon.displayName = 'Icon';

// Common icon paths (pre-optimized for performance)
export const IconPaths = {
  search: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    />
  ),
  check: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  ),
  x: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />,
  chevronDown: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  ),
  chevronUp: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  ),
  chevronLeft: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  ),
  chevronRight: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  ),
  info: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  ),
  alert: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
    />
  ),
  user: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
    />
  ),
  settings: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
    />
  ),
  menu: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 6h16M4 12h16M4 18h16"
    />
  ),
};
