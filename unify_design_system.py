#!/usr/bin/env python3
"""
Unified Design System - Professional Grade
Ensures all components are consistent, polished, and support seamless light/dark mode
"""

from pathlib import Path

# Professional Badge Component with Dark Mode
BADGE_COMPONENT = '''/**
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
'''

# Professional Select Component with Dark Mode
SELECT_COMPONENT = '''/**
 * Select Component - Professional Dropdown
 *
 * Unified design with seamless light/dark mode transitions
 */

import React, { memo, forwardRef } from 'react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  label?: string;
  error?: string;
  helperText?: string;
  options: SelectOption[];
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

export const Select = memo(
  forwardRef<HTMLSelectElement, SelectProps>(
    (
      {
        label,
        error,
        helperText,
        options,
        size = 'md',
        fullWidth = false,
        className = '',
        disabled,
        ...props
      },
      ref
    ) => {
      const sizeStyles = {
        sm: 'px-3 py-2 text-sm',
        md: 'px-4 py-3 text-base',
        lg: 'px-5 py-4 text-lg',
      };

      const baseStyles = `
        border-2 rounded-xl
        transition-all duration-normal
        focus:outline-none focus:ring-2
        disabled:opacity-50 disabled:cursor-not-allowed
        appearance-none
        ${fullWidth ? 'w-full' : ''}
      `;

      const stateStyles = error
        ? 'border-error-500 focus:border-error-600 focus:ring-error-500/20 bg-white dark:bg-dark-200'
        : 'border-neutral-300 dark:border-dark-100 focus:border-primary-500 dark:focus:border-primary-400 focus:ring-primary-500/20 bg-white dark:bg-dark-200';

      const textStyles = 'text-neutral-900 dark:text-white';

      // Custom dropdown arrow
      const chevronDown = `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%2300D9FF' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`;

      return (
        <div className={fullWidth ? 'w-full' : ''}>
          {label && (
            <label className="block text-sm font-semibold text-neutral-900 dark:text-white mb-2">
              {label}
            </label>
          )}
          <div className="relative">
            <select
              ref={ref}
              className={`${baseStyles} ${stateStyles} ${textStyles} ${sizeStyles[size]} pr-10 ${className}`}
              style={{
                backgroundImage: chevronDown,
                backgroundPosition: 'right 0.75rem center',
                backgroundRepeat: 'no-repeat',
                backgroundSize: '1.25em 1.25em',
              }}
              disabled={disabled}
              {...props}
            >
              {options.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                  className="bg-white dark:bg-dark-200 text-neutral-900 dark:text-white"
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          {(error || helperText) && (
            <p
              className={`mt-2 text-xs ${
                error
                  ? 'text-error-600 dark:text-error-400'
                  : 'text-neutral-600 dark:text-neutral-400'
              } animate-fade-in`}
            >
              {error || helperText}
            </p>
          )}
        </div>
      );
    }
  )
);

Select.displayName = 'Select';
'''

# Professional Spinner Component with Brand Colors
SPINNER_COMPONENT = '''/**
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
'''

# Professional ErrorMessage Component
ERRORMESSAGE_COMPONENT = '''/**
 * ErrorMessage Component - Professional Error Display
 *
 * Unified design with seamless light/dark mode transitions
 */

import React, { memo } from 'react';

export interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  variant?: 'inline' | 'banner' | 'toast';
}

export const ErrorMessage = memo<ErrorMessageProps>(({
  title = 'Error',
  message,
  onRetry,
  onDismiss,
  variant = 'inline',
}) => {
  const variantStyles = {
    inline: 'border-2 border-error-300 dark:border-error-800 bg-error-50 dark:bg-error-900/20 rounded-xl p-4 shadow-sm',
    banner: 'bg-error-500 dark:bg-error-600 text-white p-4 border-b-2 border-error-600 dark:border-error-700',
    toast: 'bg-error-600 dark:bg-error-700 text-white rounded-xl shadow-xl p-4 max-w-md border border-error-700 dark:border-error-800',
  };

  const textStyles = {
    inline: 'text-error-900 dark:text-error-100',
    banner: 'text-white',
    toast: 'text-white',
  };

  const iconColor = variant === 'inline'
    ? 'text-error-500 dark:text-error-400'
    : 'text-white';

  return (
    <div className={`${variantStyles[variant]} transition-all duration-normal animate-scale-in`} role="alert">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg
            className={`h-5 w-5 ${iconColor}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`text-sm font-bold ${textStyles[variant]}`}>
            {title}
          </h3>
          <div className={`mt-1 text-sm ${
            variant === 'inline'
              ? 'text-error-800 dark:text-error-200'
              : 'text-white opacity-95'
          }`}>
            <p>{message}</p>
          </div>
          {(onRetry || onDismiss) && (
            <div className="mt-4 flex gap-3">
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className={`px-3 py-1.5 text-sm font-semibold rounded-lg transition-all duration-normal ${
                    variant === 'inline'
                      ? 'bg-error-600 text-white hover:bg-error-700 dark:bg-error-700 dark:hover:bg-error-800'
                      : 'bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm'
                  }`}
                >
                  Try again
                </button>
              )}
              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className={`px-3 py-1.5 text-sm font-semibold rounded-lg transition-all duration-normal ${
                    variant === 'inline'
                      ? 'text-error-700 dark:text-error-300 hover:bg-error-100 dark:hover:bg-error-900/40'
                      : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm'
                  }`}
                >
                  Dismiss
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

ErrorMessage.displayName = 'ErrorMessage';
'''

def main():
    """Unify all components with professional design system."""
    root = Path('c:/Users/aaron/toolkit/frontend')

    print("Unifying Design System - Professional Grade...")
    print("=" * 60)

    components = [
        ('Badge', 'packages/atoms/src/Badge/Badge.tsx', BADGE_COMPONENT),
        ('Select', 'packages/atoms/src/Select/Select.tsx', SELECT_COMPONENT),
        ('Spinner', 'packages/atoms/src/Spinner/Spinner.tsx', SPINNER_COMPONENT),
        ('ErrorMessage', 'packages/atoms/src/ErrorMessage/ErrorMessage.tsx', ERRORMESSAGE_COMPONENT),
    ]

    for name, path, content in components:
        file_path = root / path
        print(f"\nUpgrading {name} component...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   Updated: {file_path}")

    print("\n" + "=" * 60)
    print("Design System Unified!")
    print("\nEnhancements Applied:")
    print("- Badge: Rounded-xl borders, dark mode with transparency, animated dot")
    print("- Select: Rounded-xl, brand-colored chevron, proper dark mode")
    print("- Spinner: Brand colors (primary/secondary), dark mode support")
    print("- ErrorMessage: Rounded-xl, proper buttons, seamless dark mode")
    print("\nAll components now:")
    print("  Professional rounded-xl borders")
    print("  Seamless light/dark mode transitions")
    print("  Unified color system with brand integration")
    print("  Consistent spacing and typography")
    print("  Smooth animations and transitions")

if __name__ == '__main__':
    main()
