/**
 * LoadingState Component
 * Consistent loading indicators across all applications
 */

import React from 'react';
import { Spinner, type SpinnerProps } from '@unistax/atoms';

export interface LoadingStateProps {
  /** Size of the loading indicator */
  size?: SpinnerProps['size'];
  /** Loading message */
  message?: string;
  /** Variant style */
  variant?: 'overlay' | 'inline' | 'fullscreen';
}

export const LoadingState = React.memo<LoadingStateProps>(({
  size = 'lg',
  message = 'Loading...',
  variant = 'inline',
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Spinner size={size} />
      {message && (
        <p className="text-sm text-neutral-600 font-medium">
          {message}
        </p>
      )}
    </div>
  );

  if (variant === 'fullscreen') {
    return (
      <div className="fixed inset-0 bg-neutral-50 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  if (variant === 'overlay') {
    return (
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10">
        {content}
      </div>
    );
  }

  // inline variant
  return (
    <div className="flex items-center justify-center py-12">
      {content}
    </div>
  );
});

LoadingState.displayName = 'LoadingState';
