#!/usr/bin/env python3
"""Update Logo component to use actual PNG image."""

from pathlib import Path

logo_component = '''/**
 * Logo Component - Unistax Brand
 * Uses the official Unistax isometric cube logo
 */

import React from 'react';
import logoImage from './unistax-logo.png';

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
      {/* Official Unistax logo */}
      <img
        src={logoImage}
        alt="Unistax"
        width={size}
        height={size}
        className="object-contain"
      />

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
'''

def main():
    """Update Logo component file."""
    logo_file = Path('c:/Users/aaron/toolkit/frontend/packages/atoms/src/Logo/Logo.tsx')

    print(f"Updating: {logo_file}")

    with open(logo_file, 'w', encoding='utf-8') as f:
        f.write(logo_component)

    print("Logo component updated successfully!")

if __name__ == '__main__':
    main()
