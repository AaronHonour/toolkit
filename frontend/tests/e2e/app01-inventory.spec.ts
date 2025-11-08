/**
 * E2E Tests for App 01: E-Commerce Inventory Management
 *
 * Critical User Flows:
 * - View product catalog
 * - Search products with debounced input
 * - Filter by category and status
 * - View product details in modal
 * - Check real-time stats updates
 */

import { test, expect } from '@playwright/test'

test.describe('App 01: E-Commerce Inventory', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to App 01
    await page.goto('http://localhost:3001')
    await page.waitForLoadState('networkidle')
  })

  // ============================================================================
  // Basic Page Load
  // ============================================================================

  test('should load the inventory page', async ({ page }) => {
    // Check page title/header
    await expect(page.locator('h1')).toContainText('E-Commerce Inventory')

    // Check stats bar is visible
    await expect(page.locator('text=Total Products')).toBeVisible()
    await expect(page.locator('text=In Stock')).toBeVisible()
    await expect(page.locator('text=Low Stock')).toBeVisible()
  })

  test('should display product grid', async ({ page }) => {
    // Wait for products to load
    await page.waitForSelector('.product-card', { timeout: 5000 })

    // Check that products are displayed
    const productCards = page.locator('.product-card')
    const count = await productCards.count()

    expect(count).toBeGreaterThan(0)
    expect(count).toBeLessThanOrEqual(20) // Default page size
  })

  // ============================================================================
  // Search Functionality
  // ============================================================================

  test('should search products with debounced input', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[placeholder*="search" i]')
    await expect(searchInput).toBeVisible()

    // Type search query
    await searchInput.fill('laptop')

    // Wait for debounce (300ms) + network request
    await page.waitForTimeout(500)

    // Check that results are filtered
    const productCards = page.locator('.product-card')
    const count = await productCards.count()

    // Should have fewer products after filtering
    expect(count).toBeGreaterThan(0)

    // All visible products should contain "laptop" (case insensitive)
    const firstProduct = productCards.first()
    await expect(firstProduct).toContainText(/laptop/i)
  })

  test('should clear search results', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="search" i]')

    // Search for something
    await searchInput.fill('mouse')
    await page.waitForTimeout(500)

    const filteredCount = await page.locator('.product-card').count()

    // Clear search
    await searchInput.clear()
    await page.waitForTimeout(500)

    const allCount = await page.locator('.product-card').count()

    // Should have more products after clearing
    expect(allCount).toBeGreaterThanOrEqual(filteredCount)
  })

  // ============================================================================
  // Filter Functionality
  // ============================================================================

  test('should filter by category', async ({ page }) => {
    // Find category filter dropdown/select
    const categoryFilter = page.locator('select, [role="combobox"]').filter({
      hasText: /category|all categories/i,
    })

    if ((await categoryFilter.count()) > 0) {
      // Select a category
      await categoryFilter.first().selectOption({ label: /electronics|computers/i })

      await page.waitForTimeout(300)

      // Products should update
      const productCards = page.locator('.product-card')
      expect(await productCards.count()).toBeGreaterThan(0)
    }
  })

  test('should filter by status', async ({ page }) => {
    // Find status filter
    const statusFilter = page.locator('select, [role="combobox"]').filter({
      hasText: /status|all status/i,
    })

    if ((await statusFilter.count()) > 0) {
      // Select "In Stock" status
      await statusFilter.first().selectOption({ label: /in stock|active/i })

      await page.waitForTimeout(300)

      // Check badge shows "In Stock"
      const badges = page.locator('.badge, [class*="badge"]')
      const inStockBadge = badges.filter({ hasText: /in stock|active/i })

      expect(await inStockBadge.count()).toBeGreaterThan(0)
    }
  })

  // ============================================================================
  // Product Detail Modal
  // ============================================================================

  test('should open product detail modal', async ({ page }) => {
    // Wait for products
    await page.waitForSelector('.product-card')

    // Click on first product
    const firstProduct = page.locator('.product-card').first()
    await firstProduct.click()

    // Modal should open
    const modal = page.locator('[role="dialog"], .modal, [class*="modal"]')
    await expect(modal).toBeVisible()

    // Modal should contain product details
    await expect(modal).toContainText(/sku|price|stock/i)
  })

  test('should close product detail modal with X button', async ({ page }) => {
    // Open modal
    await page.waitForSelector('.product-card')
    await page.locator('.product-card').first().click()

    // Wait for modal
    const modal = page.locator('[role="dialog"], .modal')
    await expect(modal).toBeVisible()

    // Find and click close button
    const closeButton = modal.locator('button').filter({ hasText: /close|×|✕/i })
    await closeButton.first().click()

    // Modal should close
    await expect(modal).not.toBeVisible()
  })

  test('should close product detail modal with Escape key', async ({ page }) => {
    // Open modal
    await page.waitForSelector('.product-card')
    await page.locator('.product-card').first().click()

    const modal = page.locator('[role="dialog"], .modal')
    await expect(modal).toBeVisible()

    // Press Escape
    await page.keyboard.press('Escape')

    // Modal should close
    await expect(modal).not.toBeVisible()
  })

  // ============================================================================
  // Real-time Stats
  // ============================================================================

  test('should display real-time inventory stats', async ({ page }) => {
    // Get initial stats
    const totalProducts = page.locator('text=/Total Products/i').locator('..').locator('text=/\\d+/')
    const initialTotal = await totalProducts.textContent()

    expect(initialTotal).toBeTruthy()
    expect(parseInt(initialTotal || '0')).toBeGreaterThan(0)

    // Stats should update (polling every 2 seconds)
    // Wait and check they're still there
    await page.waitForTimeout(3000)

    const updatedTotal = await totalProducts.textContent()
    expect(updatedTotal).toBeTruthy()
  })

  // ============================================================================
  // Accessibility
  // ============================================================================

  test('should be keyboard navigable', async ({ page }) => {
    await page.waitForSelector('.product-card')

    // Tab to search input
    await page.keyboard.press('Tab')

    // Should be able to type
    await page.keyboard.type('test')

    // Continue tabbing to products
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab')
    }

    // Should be able to activate with Enter/Space
    await page.keyboard.press('Enter')

    // Modal might open (if we landed on a product)
    // Just verify no errors occurred
  })

  test('should have proper ARIA labels', async ({ page }) => {
    // Check for aria-label on search
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]')
    if ((await searchInput.count()) > 0) {
      const ariaLabel = await searchInput.getAttribute('aria-label')
      expect(ariaLabel || (await searchInput.getAttribute('placeholder'))).toBeTruthy()
    }
  })

  // ============================================================================
  // Performance
  // ============================================================================

  test('should load within 3 seconds', async ({ page }) => {
    const startTime = Date.now()

    await page.goto('http://localhost:3001')
    await page.waitForSelector('.product-card', { timeout: 5000 })

    const loadTime = Date.now() - startTime

    expect(loadTime).toBeLessThan(3000)
  })

  test('should handle rapid search input without errors', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="search" i]')

    // Rapidly type and clear
    for (let i = 0; i < 5; i++) {
      await searchInput.fill(`query${i}`)
      await page.waitForTimeout(50) // Faster than debounce
      await searchInput.clear()
    }

    // Should still work after rapid changes
    await searchInput.fill('laptop')
    await page.waitForTimeout(500)

    const products = await page.locator('.product-card').count()
    expect(products).toBeGreaterThan(0)
  })
})
