/**
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
