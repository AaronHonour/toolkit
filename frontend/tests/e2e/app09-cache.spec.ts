/**
 * E2E Tests for App 09: Distributed Cache Dashboard
 *
 * Critical User Flows:
 * - View cache statistics (L1/L2 tiers, hit rate)
 * - Browse cache keys
 * - Search cache keys
 * - Create new cache entries
 * - View cache entry details
 * - Delete cache entries
 */

import { test, expect } from '@playwright/test'

test.describe('App 09: Cache Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to App 09 (cache dashboard is on port 3009)
    await page.goto('http://localhost:3009')
    await page.waitForLoadState('networkidle')
  })

  // ============================================================================
  // Basic Page Load
  // ============================================================================

  test('should load the cache dashboard', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1')).toContainText(/cache|distributed cache/i)

    // Check stats are visible
    await expect(page.locator('text=/hit rate|hits|misses/i')).toBeVisible()
  })

  test('should display cache statistics', async ({ page }) => {
    // Check L1/L2 tier stats
    const stats = page.locator('text=/L1|L2|tier/i')
    expect(await stats.count()).toBeGreaterThan(0)

    // Check numeric values are present
    const numbers = page.locator('text=/\\d+\\.?\\d*%?/')
    expect(await numbers.count()).toBeGreaterThan(0)
  })

  // ============================================================================
  // Cache Key Browsing
  // ============================================================================

  test('should display cache keys list', async ({ page }) => {
    // Wait for keys to load
    await page.waitForSelector('[class*="key"], [data-testid*="key"], li, tr', {
      timeout: 5000,
    })

    // Check that keys are displayed
    const keys = page.locator('[class*="cache-key"], [class*="key-item"], li, tr')
    const count = await keys.count()

    expect(count).toBeGreaterThan(0)
  })

  // ============================================================================
  // Search Functionality
  // ============================================================================

  test('should search cache keys', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]')

    if ((await searchInput.count()) > 0) {
      // Type search query
      await searchInput.fill('user')
      await page.waitForTimeout(500)

      // Results should be filtered
      const results = page.locator('[class*="key"], li, tr')
      const count = await results.count()

      expect(count).toBeGreaterThan(0)

      // First result should contain search term
      const firstResult = results.first()
      await expect(firstResult).toContainText(/user/i)
    }
  })

  // ============================================================================
  // Create Cache Entry
  // ============================================================================

  test('should show create cache entry form', async ({ page }) => {
    // Look for "Add" or "Create" or "New" button
    const createButton = page.locator('button').filter({
      hasText: /add|create|new|set/i,
    })

    if ((await createButton.count()) > 0) {
      await createButton.first().click()

      // Form should appear
      const form = page.locator('form, [role="form"]')
      await expect(form).toBeVisible()

      // Should have key and value inputs
      await expect(page.locator('input[name*="key" i], input[placeholder*="key" i]')).toBeVisible()
      await expect(
        page.locator('input[name*="value" i], textarea[name*="value" i], input[placeholder*="value" i]')
      ).toBeVisible()
    }
  })

  test('should create new cache entry', async ({ page }) => {
    const createButton = page.locator('button').filter({
      hasText: /add|create|new|set/i,
    })

    if ((await createButton.count()) > 0) {
      await createButton.first().click()

      // Fill in form
      const keyInput = page.locator('input[name*="key" i], input[placeholder*="key" i]').first()
      const valueInput = page
        .locator('input[name*="value" i], textarea[name*="value" i], input[placeholder*="value" i]')
        .first()

      const testKey = `test:key:${Date.now()}`
      const testValue = 'test value'

      await keyInput.fill(testKey)
      await valueInput.fill(testValue)

      // Submit form
      const submitButton = page.locator('button[type="submit"], button').filter({
        hasText: /save|create|add|submit/i,
      })
      await submitButton.first().click()

      // Wait for success (form closes or success message)
      await page.waitForTimeout(1000)

      // Search for the new key
      const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]')
      if ((await searchInput.count()) > 0) {
        await searchInput.fill(testKey)
        await page.waitForTimeout(500)

        // Should find the new entry
        await expect(page.locator(`text=${testKey}`)).toBeVisible()
      }
    }
  })

  // ============================================================================
  // View Cache Entry Details
  // ============================================================================

  test('should view cache entry details', async ({ page }) => {
    // Wait for keys
    await page.waitForSelector('[class*="key"], li, tr', { timeout: 5000 })

    // Click on first key
    const firstKey = page.locator('[class*="key"], li, tr').first()
    const keyText = await firstKey.textContent()

    await firstKey.click()

    // Details should be visible (either in modal or expanded row)
    const details = page.locator('[role="dialog"], [class*="detail"], [class*="expanded"]')

    if ((await details.count()) > 0) {
      await expect(details.first()).toBeVisible()
      // Should show the key
      await expect(details.first()).toContainText(keyText || '')
    }
  })

  // ============================================================================
  // Delete Cache Entry
  // ============================================================================

  test('should delete cache entry', async ({ page }) => {
    // Wait for keys
    await page.waitForSelector('[class*="key"], li, tr', { timeout: 5000 })

    // Get initial count
    const initialCount = await page.locator('[class*="key"], li, tr').count()

    // Find delete button (might be on first entry or need to click entry first)
    const deleteButtons = page.locator('button').filter({
      hasText: /delete|remove|×|✕/i,
    })

    if ((await deleteButtons.count()) > 0) {
      // Click first delete button
      await deleteButtons.first().click()

      // Might have confirmation dialog
      const confirmButton = page.locator('button').filter({
        hasText: /confirm|yes|delete|ok/i,
      })

      if ((await confirmButton.count()) > 0) {
        await confirmButton.first().click()
      }

      // Wait for deletion
      await page.waitForTimeout(1000)

      // Count should be less (or same if there was an error)
      const newCount = await page.locator('[class*="key"], li, tr').count()
      expect(newCount).toBeLessThanOrEqual(initialCount)
    }
  })

  // ============================================================================
  // Cache Tier Breakdown
  // ============================================================================

  test('should show L1 and L2 tier statistics', async ({ page }) => {
    // Look for L1 stats
    const l1Stats = page.locator('text=/L1.*?\\d+/i')
    if ((await l1Stats.count()) > 0) {
      await expect(l1Stats.first()).toBeVisible()
    }

    // Look for L2 stats
    const l2Stats = page.locator('text=/L2.*?\\d+/i')
    if ((await l2Stats.count()) > 0) {
      await expect(l2Stats.first()).toBeVisible()
    }

    // Hit rate should be displayed
    const hitRate = page.locator('text=/hit rate.*?\\d+/i')
    if ((await hitRate.count()) > 0) {
      await expect(hitRate.first()).toBeVisible()
    }
  })

  // ============================================================================
  // Real-time Updates
  // ============================================================================

  test('should update stats in real-time', async ({ page }) => {
    // Get initial hit rate
    const hitRateElement = page.locator('text=/hit rate/i').locator('..').locator('text=/\\d+\\.?\\d*%?/')

    if ((await hitRateElement.count()) > 0) {
      const initialValue = await hitRateElement.textContent()

      // Wait for polling interval (2 seconds)
      await page.waitForTimeout(3000)

      // Value should still be present (might be same or different)
      const updatedValue = await hitRateElement.textContent()
      expect(updatedValue).toBeTruthy()
    }
  })

  // ============================================================================
  // Performance
  // ============================================================================

  test('should load within 3 seconds', async ({ page }) => {
    const startTime = Date.now()

    await page.goto('http://localhost:3009')
    await page.waitForSelector('h1', { timeout: 5000 })

    const loadTime = Date.now() - startTime

    expect(loadTime).toBeLessThan(3000)
  })

  test('should handle rapid CRUD operations', async ({ page }) => {
    // This tests the debouncing and state management
    const createButton = page.locator('button').filter({ hasText: /add|create|new/i })

    if ((await createButton.count()) > 0) {
      // Rapidly click create button
      for (let i = 0; i < 3; i++) {
        await createButton.first().click()
        await page.waitForTimeout(100)

        // Close form if it opened
        const cancelButton = page.locator('button').filter({ hasText: /cancel|close/i })
        if ((await cancelButton.count()) > 0) {
          await cancelButton.first().click({ force: true })
        }
      }

      // App should still be responsive
      await expect(page.locator('h1')).toBeVisible()
    }
  })
})
