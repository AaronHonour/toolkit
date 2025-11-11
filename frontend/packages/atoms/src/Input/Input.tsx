/**
 * Input Component - Professional Form Control
 *
 * Premium input with refined states, smooth transitions, and accessibility
 * Target: < 1ms render time
 */

import React, { memo, forwardRef, ReactNode, useState } from 'react';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input variant */
  variant?: 'default' | 'error' | 'success' | 'warning';
  /** Input size */
  size?: 'sm' | 'md' | 'lg';
  /** Full width */
  fullWidth?: boolean;
  /** Left icon */
  leftIcon?: ReactNode;
  /** Right icon */
  rightIcon?: ReactNode;
  /** Label text */
  label?: string;
  /** Helper text */
  helperText?: string;
  /** Error state */
  error?: boolean;
  /** Success state */
  success?: boolean;
  /** Warning state */
  warning?: boolean;
}

export const Input = memo(
  forwardRef<HTMLInputElement, InputProps>(
    (
      {
        variant = 'default',
        size = 'md',
        fullWidth = false,
        leftIcon,
        rightIcon,
        label,
        helperText,
        error,
        success,
        warning,
        className = '',
        disabled,
        placeholder,
        ...props
      },
      ref
    ) => {
      const [isFocused, setIsFocused] = useState(false);
      const [hasValue, setHasValue] = useState(!!props.value || !!props.defaultValue);

      // Determine variant based on state
      const finalVariant = error ? 'error' : success ? 'success' : warning ? 'warning' : variant;

      // Base styles
      const containerBaseStyles =
        'relative inline-flex items-center border-2 rounded-xl transition-all duration-normal focus-within:ring-2';

      // Variant styles
      const variantStyles = {
        default:
          'border-neutral-300 dark:border-dark-100 bg-white dark:bg-dark-200 focus-within:border-primary-500 dark:focus-within:border-primary-400 focus-within:ring-primary-500/20',
        error:
          'border-error-500 bg-white dark:bg-dark-200 focus-within:border-error-600 focus-within:ring-error-500/20',
        success:
          'border-success-500 bg-white dark:bg-dark-200 focus-within:border-success-600 focus-within:ring-success-500/20',
        warning:
          'border-warning-500 bg-white dark:bg-dark-200 focus-within:border-warning-600 focus-within:ring-warning-500/20',
      };

      // Size styles
      const sizeStyles = {
        sm: 'text-sm',
        md: 'text-base',
        lg: 'text-lg',
      };

      const inputSizeStyles = {
        sm: 'px-3 py-2',
        md: 'px-4 py-3',
        lg: 'px-5 py-4',
      };

      const labelSizeStyles = {
        sm: 'text-xs',
        md: 'text-sm',
        lg: 'text-base',
      };

      // Disabled styles
      const disabledStyles = disabled
        ? 'opacity-50 cursor-not-allowed bg-neutral-100 dark:bg-dark-100'
        : 'cursor-text';

      // Helper text color
      const helperTextColor = error
        ? 'text-error-600 dark:text-error-400'
        : success
        ? 'text-success-600 dark:text-success-400'
        : warning
        ? 'text-warning-600 dark:text-warning-400'
        : 'text-neutral-600 dark:text-neutral-400';

      const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setHasValue(!!e.target.value);
        props.onChange?.(e);
      };

      return (
        <div className={fullWidth ? 'w-full' : 'w-auto'}>
          <div className="relative">
            {label && (
              <label
                className={`
                  absolute left-4 transition-all duration-normal pointer-events-none
                  ${labelSizeStyles[size]}
                  ${
                    isFocused || hasValue
                      ? '-top-2.5 bg-white dark:bg-dark-200 px-2 text-primary-600 dark:text-primary-400 font-medium'
                      : `top-1/2 -translate-y-1/2 text-neutral-500 dark:text-neutral-400`
                  }
                `.trim()}
              >
                {label}
              </label>
            )}
            <div
              className={`
                ${containerBaseStyles}
                ${variantStyles[finalVariant]}
                ${sizeStyles[size]}
                ${disabledStyles}
                ${fullWidth ? 'w-full' : ''}
                ${className}
              `.trim()}
            >
              {leftIcon && (
                <span className="flex-shrink-0 pl-3 text-neutral-500 dark:text-neutral-400">{leftIcon}</span>
              )}
              <input
                ref={ref}
                disabled={disabled}
                placeholder={isFocused || !label ? placeholder : ''}
                onFocus={(e) => {
                  setIsFocused(true);
                  props.onFocus?.(e);
                }}
                onBlur={(e) => {
                  setIsFocused(false);
                  props.onBlur?.(e);
                }}
                onChange={handleChange}
                className={`
                  ${inputSizeStyles[size]}
                  flex-1 bg-transparent border-0 outline-none
                  placeholder:text-neutral-400 dark:placeholder:text-neutral-500
                  disabled:cursor-not-allowed
                  text-neutral-900 dark:text-white
                `.trim()}
                {...props}
              />
              {rightIcon && (
                <span className="flex-shrink-0 pr-3 text-neutral-500 dark:text-neutral-400">{rightIcon}</span>
              )}
            </div>
          </div>
          {helperText && (
            <p className={`mt-2 text-xs ${helperTextColor} animate-fade-in`}>
              {helperText}
            </p>
          )}
        </div>
      );
    }
  )
);

Input.displayName = 'Input';
