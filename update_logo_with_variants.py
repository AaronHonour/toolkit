#!/usr/bin/env python3
"""Update Logo component to use light/dark variants properly."""

from pathlib import Path

LOGO_COMPONENT = '''/**
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
'''

def main():
    """Update Logo component."""
    root = Path('c:/Users/aaron/toolkit/frontend')

    print("Updating Logo Component with Light/Dark Variants...")
    print("=" * 60)

    logo_file = root / 'packages' / 'atoms' / 'src' / 'Logo' / 'Logo.tsx'
    with open(logo_file, 'w', encoding='utf-8') as f:
        f.write(LOGO_COMPONENT)

    print(f"Updated: {logo_file}")
    print("\n" + "=" * 60)
    print("Logo Component Updated!")
    print("\nChanges:")
    print("- Removed gradient background wrapper")
    print("- Light mode: Shows colored logo (unistax-logo-light.png)")
    print("- Dark mode: Shows white logo (unistax-logo-dark.png)")
    print("- Automatic theme detection via dark: Tailwind classes")
    print("- Maintained glow-on-hover effect")

if __name__ == '__main__':
    main()
