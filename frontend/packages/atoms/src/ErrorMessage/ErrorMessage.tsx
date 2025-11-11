/**
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
