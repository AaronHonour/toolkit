#!/usr/bin/env python3
"""
Comprehensive UI Quality Upgrade Script
Upgrades all components to professional, polished standards
"""

from pathlib import Path

# Enhanced Tailwind Config with Professional Design System
TAILWIND_CONFIG = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './packages/*/src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter var',
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono"',
          '"Fira Code"',
          '"SF Mono"',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem', letterSpacing: '0.025em' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem', letterSpacing: '0' }],
        'base': ['1rem', { lineHeight: '1.5rem', letterSpacing: '0' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem', letterSpacing: '-0.01em' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem', letterSpacing: '-0.01em' }],
        '2xl': ['1.5rem', { lineHeight: '2rem', letterSpacing: '-0.02em' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem', letterSpacing: '-0.02em' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem', letterSpacing: '-0.02em' }],
      },
      colors: {
        primary: {
          50: '#E6FEFF',
          100: '#B3FDFF',
          200: '#80FBFF',
          300: '#4DF9FF',
          400: '#1AF7FF',
          500: '#00D9FF',
          600: '#00B8DB',
          700: '#0097B7',
          800: '#007693',
          900: '#00556F',
          950: '#003A4D',
        },
        secondary: {
          50: '#F3E8FF',
          100: '#E1C4FF',
          200: '#CFA0FF',
          300: '#BD7CFF',
          400: '#AB58FF',
          500: '#9D4EDD',
          600: '#7B2CBF',
          700: '#5A189A',
          800: '#3C096C',
          900: '#240046',
          950: '#10002B',
        },
        accent: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#5A67D8',
          600: '#4C51BF',
          700: '#434190',
          800: '#3730A3',
          900: '#312E81',
          950: '#1E1B4B',
        },
        neutral: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0A0A0A',
        },
        dark: {
          50: '#1E293B',
          100: '#151E2E',
          200: '#0F172A',
          300: '#0A0E27',
          400: '#070B1F',
          500: '#050818',
          600: '#030510',
          700: '#020308',
          800: '#010204',
          900: '#000000',
        },
        success: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBF7D0',
          300: '#86EFAC',
          400: '#4ADE80',
          500: '#22C55E',
          600: '#16A34A',
          700: '#15803D',
          800: '#166534',
          900: '#14532D',
        },
        warning: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
        error: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
        info: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #00D9FF 0%, #9D4EDD 100%)',
        'gradient-primary-hover': 'linear-gradient(135deg, #00B8DB 0%, #7B2CBF 100%)',
        'gradient-accent': 'linear-gradient(135deg, #5A67D8 0%, #9D4EDD 100%)',
        'gradient-mesh': 'radial-gradient(at 0% 0%, rgba(0, 217, 255, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(157, 78, 221, 0.15) 0px, transparent 50%)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      borderRadius: {
        'sm': '0.25rem',
        'DEFAULT': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'DEFAULT': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'md': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
        'lg': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        'xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        '2xl': '0 50px 100px -20px rgba(0, 0, 0, 0.3)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        'glow-primary': '0 0 30px rgba(0, 217, 255, 0.4)',
        'glow-primary-sm': '0 0 15px rgba(0, 217, 255, 0.3)',
        'glow-secondary': '0 0 30px rgba(157, 78, 221, 0.4)',
        'glow-accent': '0 0 30px rgba(90, 103, 216, 0.4)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-out': 'fadeOut 0.3s ease-in-out',
        'slide-in-up': 'slideInUp 0.3s ease-out',
        'slide-in-down': 'slideInDown 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 15px rgba(0, 217, 255, 0.4)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 25px rgba(0, 217, 255, 0.6)' },
        },
        spin: {
          'to': { transform: 'rotate(360deg)' },
        },
      },
      transitionDuration: {
        'fast': '150ms',
        'normal': '250ms',
        'slow': '350ms',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
    },
  },
  plugins: [],
};
'''

# Enhanced Global Styles
GLOBAL_STYLES = '''/**
 * Unistax Design System - Compiled Styles
 *
 * Professional, polished UI with sophisticated design system
 */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* Root configuration */
  :root {
    color-scheme: light dark;
    font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  }

  /* Base typography */
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-weight: 400;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
  }

  /* Sophisticated background mesh pattern for light mode */
  body {
    background-color: #FAFAFA;
    background-image:
      radial-gradient(circle at 20% 50%, rgba(0, 217, 255, 0.04) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(157, 78, 221, 0.04) 0%, transparent 50%),
      linear-gradient(90deg, rgba(0, 217, 255, 0.02) 1px, transparent 1px),
      linear-gradient(rgba(0, 217, 255, 0.02) 1px, transparent 1px);
    background-size:
      100% 100%,
      100% 100%,
      60px 60px,
      60px 60px;
    background-position:
      0 0,
      0 0,
      0 0,
      0 0;
  }

  /* Dark mode mesh pattern - refined and professional */
  .dark body {
    background-color: #0A0E27;
    background-image:
      radial-gradient(circle at 20% 50%, rgba(0, 217, 255, 0.06) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(157, 78, 221, 0.06) 0%, transparent 50%),
      linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px),
      linear-gradient(rgba(0, 217, 255, 0.03) 1px, transparent 1px);
  }

  /* Smooth scrolling */
  html {
    scroll-behavior: smooth;
  }

  /* Better focus outlines */
  *:focus-visible {
    outline: 2px solid rgba(0, 217, 255, 0.6);
    outline-offset: 2px;
    border-radius: 0.25rem;
  }
}

@layer components {
  /* Premium gradient text */
  .text-gradient {
    background: linear-gradient(135deg, #00D9FF 0%, #9D4EDD 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }

  /* Enhanced gradient button */
  .btn-gradient {
    position: relative;
    background: linear-gradient(135deg, #00D9FF 0%, #9D4EDD 100%);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
  }

  .btn-gradient::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #00B8DB 0%, #7B2CBF 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .btn-gradient:hover::before {
    opacity: 1;
  }

  .btn-gradient:hover {
    box-shadow: 0 0 30px rgba(0, 217, 255, 0.5), 0 10px 25px -5px rgba(0, 217, 255, 0.3);
    transform: translateY(-1px);
  }

  .btn-gradient:active {
    transform: translateY(0);
  }

  /* Professional glass-morphism card */
  .glass-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(0, 217, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
  }

  .dark .glass-card {
    background: rgba(10, 14, 39, 0.8);
    border: 1px solid rgba(0, 217, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
  }

  /* Refined glow effect */
  .glow-on-hover {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .glow-on-hover:hover {
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    transform: translateY(-1px);
  }

  .dark .glow-on-hover:hover {
    box-shadow: 0 0 25px rgba(0, 217, 255, 0.5);
  }

  /* Premium elevation system */
  .elevation-1 {
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  }

  .elevation-2 {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  }

  .elevation-3 {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  }

  .elevation-4 {
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  }

  /* Animations */
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes pulse-glow {
    0%, 100% {
      opacity: 1;
      box-shadow: 0 0 15px rgba(0, 217, 255, 0.4);
    }
    50% {
      opacity: 0.8;
      box-shadow: 0 0 25px rgba(0, 217, 255, 0.6);
    }
  }

  .animate-pulse-glow {
    animation: pulse-glow 2s ease-in-out infinite;
  }

  /* Professional circuit dot decorations */
  .circuit-dot {
    position: relative;
  }

  .circuit-dot::before {
    content: '';
    position: absolute;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00D9FF, #9D4EDD);
    box-shadow: 0 0 10px rgba(0, 217, 255, 0.6);
    animation: pulse-glow 2s ease-in-out infinite;
  }

  /* Better scrollbars */
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }

  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(0, 217, 255, 0.3);
    border-radius: 4px;
  }

  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 217, 255, 0.5);
  }

  .dark .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(0, 217, 255, 0.4);
  }

  .dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 217, 255, 0.6);
  }
}

/* Professional utility classes */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }

  .transition-smooth {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
}
'''

def main():
    """Execute UI quality upgrades."""
    root = Path('c:/Users/aaron/toolkit/frontend')

    print("Upgrading UI Quality to Professional Standards...")
    print("=" * 60)

    # 1. Update Tailwind Config
    print("\n1. Upgrading Tailwind configuration with professional design system...")
    tailwind_config = root.parent / 'frontend' / 'tailwind.components.config.js'
    with open(tailwind_config, 'w', encoding='utf-8') as f:
        f.write(TAILWIND_CONFIG)
    print(f"   Updated: {tailwind_config}")

    # 2. Update Global Styles
    print("\n2. Upgrading global styles with refined aesthetics...")
    styles_file = root / 'packages' / 'unistax' / 'src' / 'styles.css'
    with open(styles_file, 'w', encoding='utf-8') as f:
        f.write(GLOBAL_STYLES)
    print(f"   Updated: {styles_file}")

    print("\n" + "=" * 60)
    print("UI Quality Upgrade Complete!")
    print("\nNext steps:")
    print("1. Enhanced Button component with refined states")
    print("2. Improved Input component with floating labels")
    print("3. Upgraded AppLayout with sophisticated header")
    print("4. Rebuild CSS and restart frontend")

if __name__ == '__main__':
    main()
