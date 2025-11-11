/**
 * Logo Component - Unistax Brand
 * Automatically switches between light and dark variants based on theme
 */

import React from 'react';
import logoLight from './unistax-logo-light.png';
import logoDark from './unistax-logo-dark.png';

export interface LogoProps {
  /** Size in pixels */
  size?: number;
  /** Show wordmark alongside icon */
  showWordmark?: boolean;
  /** Custom className */
  className?: string;
}

export const Logo = React.memo<LogoProps>(({
  size = 40,
  showWordmark = false,
  className = ''
}) => {
  const wordmarkHeight = size * 0.6;

  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {/* Logo that switches based on dark mode */}
      <div className="relative glow-on-hover">
        {/* Light mode logo (colored) */}
        <img
          src={logoLight}
          alt="Unistax"
          width={size}
          height={size}
          className="object-contain dark:hidden"
        />
        {/* Dark mode logo (white) */}
        <img
          src={logoDark}
          alt="Unistax"
          width={size}
          height={size}
          className="object-contain hidden dark:block"
        />
      </div>

      {showWordmark && (
        <div className="flex flex-col">
          <span
            className="font-bold leading-none"
            style={{ fontSize: wordmarkHeight }}
          >
            <span className="text-gradient">Unistax</span>
          </span>
          <span
            className="text-neutral-600 dark:text-neutral-400 text-xs leading-tight"
          >
            Composable Full-Stack
          </span>
        </div>
      )}
    </div>
  );
});

Logo.displayName = 'Logo';
