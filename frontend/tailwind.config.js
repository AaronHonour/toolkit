import { tokens } from './packages/design-tokens/src/tokens.ts';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './packages/*/src/**/*.{js,ts,jsx,tsx}',
    './apps/*/src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: tokens.colors,
      spacing: tokens.spacing,
      fontFamily: tokens.typography.fontFamily,
      fontSize: tokens.typography.fontSize,
      fontWeight: tokens.typography.fontWeight,
      borderRadius: tokens.borderRadius,
      boxShadow: tokens.shadows,
      screens: tokens.breakpoints,
      zIndex: tokens.zIndex,
      transitionDuration: tokens.animation.duration,
      transitionTimingFunction: tokens.animation.easing,
    },
  },
  plugins: [],
};
