import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E Test Configuration
 *
 * Testing Strategy:
 * - Test critical user flows across all 19 apps
 * - Run on multiple browsers (Chromium, Firefox, WebKit)
 * - Parallel execution for speed
 * - Screenshot/video on failure for debugging
 */

export default defineConfig({
  // Test directory
  testDir: './tests/e2e',

  // Maximum time one test can run (30 seconds)
  timeout: 30 * 1000,

  // Test execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // Fail CI if test.only is left in
  retries: process.env.CI ? 2 : 0, // Retry failed tests in CI
  workers: process.env.CI ? 1 : undefined, // Limit workers in CI

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ['json', { outputFile: 'playwright-report/results.json' }],
  ],

  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:3001',

    // Collect trace when test fails
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Default timeout for actions
    actionTimeout: 10 * 1000,

    // Default navigation timeout
    navigationTimeout: 15 * 1000,
  },

  // Projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile viewports
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Development server configuration
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3001',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes to start
  },
})
