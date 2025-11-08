/**
 * Input Component
 *
 * Performance optimized input with memoization
 * Target: < 1ms render time
 */

import React, { memo, forwardRef, ReactNode } from 'react';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input variant */
  variant?: 'default' | 'error' | 'success';
  /** Input size */
  size?: 'sm' | 'md' | 'lg';
  /** Full width */
  fullWidth?: boolean;
  /** Left icon */
  leftIcon?: ReactNode;
  /** Right icon */
  rightIcon?: ReactNode;
  /** Helper text */
  helperText?: string;
  /** Error state */
  error?: boolean;
  /** Success state */
  success?: boolean;
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
        helperText,
        error,
        success,
        className = '',
        disabled,
        ...props
      },
      ref
    ) => {
      // Determine variant based on state
      const finalVariant = error ? 'error' : success ? 'success' : variant;

      // Base styles (memoized for performance)
      const baseStyles =
        'inline-flex items-center border rounded-lg transition-all duration-200 focus-within:ring-2';

      // Variant styles (like backend algorithm configs)
      const variantStyles = {
        default:
          'border-neutral-300 bg-white focus-within:border-primary-500 focus-within:ring-primary-500/20',
        error: 'border-error-500 bg-white focus-within:border-error-600 focus-within:ring-error-500/20',
        success:
          'border-success-500 bg-white focus-within:border-success-600 focus-within:ring-success-500/20',
      };

      // Size styles
      const sizeStyles = {
        sm: 'text-sm',
        md: 'text-base',
        lg: 'text-lg',
      };

      const inputSizeStyles = {
        sm: 'px-3 py-1.5',
        md: 'px-4 py-2',
        lg: 'px-4 py-3',
      };

      // Disabled styles
      const disabledStyles = disabled
        ? 'opacity-50 cursor-not-allowed bg-neutral-100'
        : 'cursor-text';

      return (
        <div className={fullWidth ? 'w-full' : 'w-auto'}>
          <div
            className={`
              ${baseStyles}
              ${variantStyles[finalVariant]}
              ${sizeStyles[size]}
              ${disabledStyles}
              ${fullWidth ? 'w-full' : ''}
              ${className}
            `.trim()}
          >
            {leftIcon && (
              <span className="flex-shrink-0 pl-3 text-neutral-500">{leftIcon}</span>
            )}
            <input
              ref={ref}
              disabled={disabled}
              className={`
                ${inputSizeStyles[size]}
                flex-1 bg-transparent border-0 outline-none
                placeholder:text-neutral-400
                disabled:cursor-not-allowed
              `.trim()}
              {...props}
            />
            {rightIcon && (
              <span className="flex-shrink-0 pr-3 text-neutral-500">{rightIcon}</span>
            )}
          </div>
          {helperText && (
            <p
              className={`
                mt-1 text-xs
                ${error ? 'text-error-600' : success ? 'text-success-600' : 'text-neutral-600'}
              `.trim()}
            >
              {helperText}
            </p>
          )}
        </div>
      );
    }
  )
);

Input.displayName = 'Input';
