/**
 * Select Component
 * Accessible dropdown select with consistent styling
 */

import React from 'react';

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

export const Select = React.memo<SelectProps>(({
  label,
  error,
  helperText,
  options,
  size = 'md',
  fullWidth = false,
  className = '',
  disabled,
  ...props
}) => {
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-3 text-lg',
  };

  const baseStyles = `
    border rounded-lg
    transition-colors duration-200
    focus:outline-none focus:ring-2
    disabled:opacity-50 disabled:cursor-not-allowed
    appearance-none bg-no-repeat
    ${fullWidth ? 'w-full' : ''}
  `;

  const stateStyles = error
    ? 'border-error-500 focus:border-error-500 focus:ring-error-200'
    : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-200';

  const backgroundStyles = `
    bg-white
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")
    background-position: right 0.5rem center
    background-size: 1.5em 1.5em
    pr-10
  `;

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          {label}
        </label>
      )}
      <select
        className={`${baseStyles} ${stateStyles} ${sizeStyles[size]} ${backgroundStyles} ${className}`}
        disabled={disabled}
        {...props}
      >
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
      {(error || helperText) && (
        <p className={`mt-1 text-sm ${error ? 'text-error-600' : 'text-neutral-600'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';
