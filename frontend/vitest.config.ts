/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'tests/',
        '**/__tests__/**',
        '**/test/**',
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 85,
        statements: 90,
      },
    },
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    // Mock browser APIs
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,
    // Performance
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },
    // Timeouts
    testTimeout: 10000,
    hookTimeout: 10000,
  },
  resolve: {
    alias: {
      '@atoms': path.resolve(__dirname, './packages/atoms/src'),
      '@performance': path.resolve(__dirname, './packages/performance/src'),
      '@design-tokens': path.resolve(__dirname, './packages/design-tokens/src'),
    },
  },
})
