/**
 * Design Tokens - Foundation for Atomic Design System
 *
 * Performance-optimized, configurable design tokens
 * Similar to backend toolkit's composable algorithms
 */

export const colors = {
  // Primary palette - Cyan (from "Uni" in logo)
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

  // Secondary palette - Purple/Magenta (from "stax" in logo)
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

  // Accent - Electric Blue (from isometric cubes)
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

  // Neutral palette - Updated for better dark/light mode
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e5e5e5',
    300: '#d4d4d4',
    400: '#a3a3a3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
    950: '#0a0a0a',
  },

  // Dark mode backgrounds (deep navy like the logo images)
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

  // Semantic colors
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    700: '#15803d',
  },
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    700: '#b45309',
  },
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    700: '#b91c1c',
  },
  info: {
    50: '#eff6ff',
    500: '#3b82f6',
    700: '#1d4ed8',
  },
} as const;

export const spacing = {
  px: '1px',
  0: '0',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  32: '8rem',       // 128px
} as const;

export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
    mono: ['Fira Code', 'Monaco', 'Consolas', 'monospace'],
  },
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
    sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
    base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
    lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
    xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
    '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }], // 36px
    '5xl': ['3rem', { lineHeight: '1' }],         // 48px
  },
  fontWeight: {
    thin: '100',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    black: '900',
  },
} as const;

export const borderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  DEFAULT: '0.25rem', // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
} as const;

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  none: 'none',
} as const;

export const animation = {
  duration: {
    fastest: '100ms',
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
    slowest: '1000ms',
  },
  easing: {
    linear: 'linear',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    // Custom easing for performance
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    smooth: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  },
} as const;

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
} as const;

// Performance tokens (matching backend performance characteristics)
export const performance = {
  // Similar to backend RingBuffer capacity
  virtualScrollOverscan: 5,
  virtualScrollItemHeight: 50,

  // Similar to backend LRUCache
  memoizationCacheSize: 100,

  // Similar to backend debounce patterns
  debounceDelay: {
    fast: 150,
    normal: 300,
    slow: 500,
  },

  // Similar to backend throttle
  throttleDelay: {
    fast: 100,
    normal: 250,
    slow: 500,
  },

  // FPS targets (matching backend throughput goals)
  targetFPS: 60,
  maxRenderTime: 16, // ms (60fps = 16.67ms per frame)
} as const;

// Export all tokens as a single object
export const tokens = {
  colors,
  spacing,
  typography,
  borderRadius,
  shadows,
  animation,
  breakpoints,
  zIndex,
  performance,
} as const;

export type Tokens = typeof tokens;
export type ColorScale = keyof typeof colors.primary;
export type Spacing = keyof typeof spacing;
export type FontSize = keyof typeof typography.fontSize;
