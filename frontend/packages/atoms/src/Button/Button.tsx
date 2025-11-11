/**
 * Button Atom - Premium UI Component
 *
 * Professional button with refined states, animations, and accessibility
 * - Smooth transitions and micro-interactions
 * - Enhanced focus states
 * - Professional elevation and shadows
 * - < 1ms render time target
 */

import React, { memo, forwardRef } from 'react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button variant
   */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'gradient' | 'success';

  /**
   * Button size
   */
  size?: 'sm' | 'md' | 'lg' | 'xl';

  /**
   * Loading state
   */
  loading?: boolean;

  /**
   * Full width
   */
  fullWidth?: boolean;

  /**
   * Icon before text
   */
  leftIcon?: ReactNode;

  /**
   * Icon after text
   */
  rightIcon?: ReactNode;

  /**
   * Children
   */
  children?: ReactNode;
}

const variantStyles = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 shadow-sm hover:shadow-md active:shadow-sm',
  secondary: 'bg-neutral-600 text-white hover:bg-neutral-700 active:bg-neutral-800 shadow-sm hover:shadow-md active:shadow-sm',
  outline: 'border-2 border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-dark-100 active:bg-primary-100 dark:active:bg-dark-50',
  ghost: 'text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-dark-100 active:bg-primary-100 dark:active:bg-dark-50',
  danger: 'bg-error-500 text-white hover:bg-error-600 active:bg-error-700 shadow-sm hover:shadow-md active:shadow-sm',
  gradient: 'btn-gradient text-white font-semibold shadow-lg relative',
  success: 'bg-success-500 text-white hover:bg-success-600 active:bg-success-700 shadow-sm hover:shadow-md active:shadow-sm',
} as const;

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2.5 text-base',
  lg: 'px-6 py-3 text-lg',
  xl: 'px-8 py-4 text-xl',
} as const;

/**
 * Button component with professional polish
 *
 * Memoized for performance with enhanced visual feedback
 */
export const Button = memo(
  forwardRef<HTMLButtonElement, ButtonProps>(
    (
      {
        variant = 'primary',
        size = 'md',
        loading = false,
        fullWidth = false,
        leftIcon,
        rightIcon,
        disabled,
        className = '',
        children,
        ...props
      },
      ref
    ) => {
      const baseStyles =
        'inline-flex items-center justify-center gap-2 font-medium rounded-xl transition-all duration-normal focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-dark-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none hover:transform hover:-translate-y-0.5 active:translate-y-0';

      const widthStyles = fullWidth ? 'w-full' : '';

      const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyles} ${className}`;

      return (
        <button
          ref={ref}
          className={combinedClassName}
          disabled={disabled || loading}
          {...props}
        >
          {loading && (
            <svg
              className="animate-spin h-4 w-4"
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
          )}
          {!loading && leftIcon && <span className="flex items-center">{leftIcon}</span>}
          {children}
          {!loading && rightIcon && <span className="flex items-center">{rightIcon}</span>}
        </button>
      );
    }
  )
);

Button.displayName = 'Button';
