/**
 * ErrorMessage Component
 * Displays user-facing error messages with consistent styling
 */

import React from 'react';

export interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  variant?: 'inline' | 'banner' | 'toast';
}

export const ErrorMessage = React.memo<ErrorMessageProps>(({
  title = 'Error',
  message,
  onRetry,
  onDismiss,
  variant = 'inline',
}) => {
  const variantStyles = {
    inline: 'border border-error-300 bg-error-50 rounded-lg p-4',
    banner: 'bg-error-500 text-white p-4',
    toast: 'bg-error-600 text-white rounded-lg shadow-lg p-4 max-w-md',
  };

  const textStyles = {
    inline: 'text-error-900',
    banner: 'text-white',
    toast: 'text-white',
  };

  return (
    <div className={variantStyles[variant]} role="alert">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className={`h-5 w-5 ${variant === 'inline' ? 'text-error-400' : 'text-white'}`}
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
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${textStyles[variant]}`}>
            {title}
          </h3>
          <div className={`mt-1 text-sm ${variant === 'inline' ? 'text-error-700' : 'text-white opacity-90'}`}>
            <p>{message}</p>
          </div>
          {(onRetry || onDismiss) && (
            <div className="mt-3 flex gap-3">
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className={`text-sm font-medium ${
                    variant === 'inline'
                      ? 'text-error-700 hover:text-error-800'
                      : 'text-white hover:text-error-100'
                  }`}
                >
                  Try again
                </button>
              )}
              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className={`text-sm font-medium ${
                    variant === 'inline'
                      ? 'text-error-700 hover:text-error-800'
                      : 'text-white hover:text-error-100'
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
