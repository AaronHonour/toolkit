#!/usr/bin/env python3
"""
Upgrade component files with professional, polished implementations
"""

from pathlib import Path

# Professional Enhanced Button Component
BUTTON_COMPONENT = '''/**
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
'''

# Professional Enhanced Input Component
INPUT_COMPONENT = '''/**
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
'''

# Professional Enhanced AppLayout
APPLAYOUT_COMPONENT = '''/**
 * AppLayout Component - Professional Application Shell
 *
 * Sophisticated layout with refined aesthetics and smooth interactions
 */

import React, { useState, useEffect } from 'react';
import { Logo } from '@unistax/atoms';

export interface AppLayoutProps {
  /** Application title shown in header */
  title: string;
  /** Application description/subtitle */
  description?: string;
  /** Icon or emoji for the app */
  icon?: string;
  /** Navigation items */
  navigationItems?: Array<{
    label: string;
    href: string;
    active?: boolean;
  }>;
  /** Show footer */
  showFooter?: boolean;
  /** Footer content (defaults to app info) */
  footerContent?: React.ReactNode;
  /** Main content */
  children: React.ReactNode;
  /** Header actions (buttons, etc.) */
  headerActions?: React.ReactNode;
}

export const AppLayout = React.memo<AppLayoutProps>(({
  title,
  description,
  icon,
  navigationItems,
  showFooter = true,
  footerContent,
  children,
  headerActions,
}) => {
  const [darkMode, setDarkMode] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    // Check system preference
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add('dark');
    }

    // Handle scroll for header elevation
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-dark-300 flex flex-col transition-colors duration-300">
      {/* Header with sophisticated elevation */}
      <header
        className={`
          bg-white/80 dark:bg-dark-200/80 backdrop-blur-xl border-b border-neutral-200 dark:border-dark-100
          sticky top-0 z-50 transition-all duration-300
          ${scrolled ? 'shadow-lg' : 'shadow-sm'}
        `.trim()}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1 min-w-0">
              {/* Unistax Logo with hover effect */}
              <div className="glow-on-hover">
                <Logo size={40} />
              </div>

              <div className="h-8 w-px bg-neutral-300 dark:bg-dark-100" />

              <div className="flex items-center gap-3 flex-1 min-w-0">
                {icon && (
                  <span className="text-3xl animate-scale-in">{icon}</span>
                )}
                <div className="flex-1 min-w-0">
                  <h1 className="text-2xl font-bold text-neutral-900 dark:text-white truncate tracking-tight">
                    {title}
                  </h1>
                  {description && (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-0.5">
                      {description}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="ml-4 flex items-center gap-2">
              {/* Dark mode toggle with smooth animation */}
              <button
                onClick={toggleDarkMode}
                className="p-2.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-dark-100 transition-all duration-normal glow-on-hover"
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <svg className="w-5 h-5 text-primary-400 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-neutral-600 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
              {headerActions}
            </div>
          </div>
        </div>

        {/* Navigation with refined hover states */}
        {navigationItems && navigationItems.length > 0 && (
          <nav className="border-t border-neutral-200 dark:border-dark-100 bg-white/50 dark:bg-dark-200/50 backdrop-blur-sm transition-colors">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex gap-1 overflow-x-auto custom-scrollbar">
                {navigationItems.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    className={`
                      px-4 py-3 text-sm font-medium border-b-2 transition-all duration-normal whitespace-nowrap
                      ${
                        item.active
                          ? 'border-primary-500 text-primary-500 dark:text-primary-400 bg-primary-50/50 dark:bg-primary-950/20'
                          : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:border-neutral-300 dark:hover:border-dark-100 hover:bg-neutral-50 dark:hover:bg-dark-100/50'
                      }
                    `.trim()}
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            </div>
          </nav>
        )}
      </header>

      {/* Main Content with refined spacing */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-fade-in">
            {children}
          </div>
        </div>
      </main>

      {/* Footer with sophisticated styling */}
      {showFooter && (
        <footer className="mt-auto border-t border-neutral-200 dark:border-dark-100 bg-white/80 dark:bg-dark-200/80 backdrop-blur-xl transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {footerContent || (
              <div className="flex items-center justify-between text-sm text-neutral-600 dark:text-neutral-400">
                <div className="flex items-center gap-3">
                  <Logo size={24} />
                  <span className="text-neutral-400 dark:text-neutral-500">•</span>
                  <span className="font-medium">{title}</span>
                </div>
                <div className="text-neutral-500 dark:text-neutral-500 font-medium">
                  Powered by composable architecture
                </div>
              </div>
            )}
          </div>
        </footer>
      )}
    </div>
  );
});

AppLayout.displayName = 'AppLayout';
'''

def main():
    """Upgrade component files."""
    root = Path('c:/Users/aaron/toolkit/frontend')

    print("Upgrading Components to Professional Standards...")
    print("=" * 60)

    # 1. Update Button
    print("\n1. Upgrading Button component...")
    button_file = root / 'packages' / 'atoms' / 'src' / 'Button' / 'Button.tsx'
    with open(button_file, 'w', encoding='utf-8') as f:
        f.write(BUTTON_COMPONENT)
    print(f"   Updated: {button_file}")

    # 2. Update Input
    print("\n2. Upgrading Input component...")
    input_file = root / 'packages' / 'atoms' / 'src' / 'Input' / 'Input.tsx'
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(INPUT_COMPONENT)
    print(f"   Updated: {input_file}")

    # 3. Update AppLayout
    print("\n3. Upgrading AppLayout component...")
    layout_file = root / 'packages' / 'layouts' / 'src' / 'AppLayout' / 'AppLayout.tsx'
    with open(layout_file, 'w', encoding='utf-8') as f:
        f.write(APPLAYOUT_COMPONENT)
    print(f"   Updated: {layout_file}")

    print("\n" + "=" * 60)
    print("Component Upgrade Complete!")
    print("\nEnhancements:")
    print("- Button: Refined states, smooth elevation changes, better hover effects")
    print("- Input: Floating labels, enhanced focus states, better accessibility")
    print("- AppLayout: Sophisticated header with blur effects, scroll-based elevation")

if __name__ == '__main__':
    main()
