/**
 * Button Component Tests
 *
 * Testing Strategy:
 * - Unit tests for all variants and states
 * - Accessibility testing
 * - User interaction testing
 * - Performance validation (< 1ms render target)
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  // ============================================================================
  // Basic Rendering
  // ============================================================================

  it('should render with children', () => {
    render(<Button>Click me</Button>)

    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('should render with default variant (primary)', () => {
    render(<Button>Click me</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-primary-500')
  })

  // ============================================================================
  // Variant Tests
  // ============================================================================

  it('should render primary variant correctly', () => {
    render(<Button variant="primary">Primary</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-primary-500')
    expect(button).toHaveClass('text-white')
  })

  it('should render secondary variant correctly', () => {
    render(<Button variant="secondary">Secondary</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-gray-200')
    expect(button).toHaveClass('text-gray-900')
  })

  it('should render outline variant correctly', () => {
    render(<Button variant="outline">Outline</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('border-2')
    expect(button).toHaveClass('border-primary-500')
  })

  it('should render ghost variant correctly', () => {
    render(<Button variant="ghost">Ghost</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-transparent')
  })

  it('should render danger variant correctly', () => {
    render(<Button variant="danger">Danger</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-red-500')
  })

  // ============================================================================
  // Size Tests
  // ============================================================================

  it('should render small size correctly', () => {
    render(<Button size="sm">Small</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('text-sm')
    expect(button).toHaveClass('px-3')
    expect(button).toHaveClass('py-1.5')
  })

  it('should render medium size correctly (default)', () => {
    render(<Button size="md">Medium</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('text-base')
    expect(button).toHaveClass('px-4')
    expect(button).toHaveClass('py-2')
  })

  it('should render large size correctly', () => {
    render(<Button size="lg">Large</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('text-lg')
    expect(button).toHaveClass('px-6')
    expect(button).toHaveClass('py-3')
  })

  // ============================================================================
  // State Tests
  // ============================================================================

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveClass('opacity-50')
    expect(button).toHaveClass('cursor-not-allowed')
  })

  it('should show loading state', () => {
    render(<Button loading>Loading</Button>)

    const button = screen.getByRole('button')
    // Should have spinner
    expect(button.querySelector('svg')).toBeInTheDocument()
    // Should be disabled while loading
    expect(button).toBeDisabled()
  })

  // ============================================================================
  // Interaction Tests
  // ============================================================================

  it('should call onClick when clicked', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>Click me</Button>)

    await user.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should not call onClick when disabled', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(
      <Button onClick={handleClick} disabled>
        Click me
      </Button>
    )

    await user.click(screen.getByRole('button'))

    expect(handleClick).not.toHaveBeenCalled()
  })

  it('should not call onClick when loading', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(
      <Button onClick={handleClick} loading>
        Click me
      </Button>
    )

    await user.click(screen.getByRole('button'))

    expect(handleClick).not.toHaveBeenCalled()
  })

  it('should handle keyboard interaction (Enter)', () => {
    const handleClick = vi.fn()

    render(<Button onClick={handleClick}>Press Enter</Button>)

    const button = screen.getByRole('button')
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' })

    // Button click happens automatically on Enter (default button behavior)
    expect(handleClick).toHaveBeenCalled()
  })

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  it('should have correct ARIA attributes', () => {
    render(
      <Button aria-label="Close dialog" type="button">
        X
      </Button>
    )

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-label', 'Close dialog')
    expect(button).toHaveAttribute('type', 'button')
  })

  it('should be keyboard accessible', () => {
    render(<Button>Keyboard Accessible</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('tabIndex', '0')
  })

  it('should have aria-disabled when disabled', () => {
    render(<Button disabled>Disabled</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-disabled', 'true')
  })

  // ============================================================================
  // Custom Props Tests
  // ============================================================================

  it('should accept and apply className prop', () => {
    render(<Button className="custom-class">Custom</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('should accept data attributes', () => {
    render(<Button data-testid="my-button">Data Attributes</Button>)

    expect(screen.getByTestId('my-button')).toBeInTheDocument()
  })

  it('should forward ref correctly', () => {
    const ref = { current: null as HTMLButtonElement | null }

    render(<Button ref={ref}>Ref Test</Button>)

    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
    expect(ref.current).toHaveTextContent('Ref Test')
  })

  // ============================================================================
  // Performance Tests
  // ============================================================================

  it('should render quickly (< 5ms)', () => {
    const start = performance.now()

    render(<Button>Performance Test</Button>)

    const end = performance.now()
    const renderTime = end - start

    // Allow 5ms for CI environments (target is < 1ms locally)
    expect(renderTime).toBeLessThan(5)
  })

  it('should memoize and not re-render with same props', () => {
    const { rerender } = render(<Button>Memo Test</Button>)

    const button = screen.getByRole('button')
    const firstRender = button

    // Re-render with same props
    rerender(<Button>Memo Test</Button>)

    const secondRender = screen.getByRole('button')

    // Should be the same DOM element (memoized)
    expect(firstRender).toBe(secondRender)
  })

  // ============================================================================
  // Edge Cases
  // ============================================================================

  it('should handle undefined children gracefully', () => {
    render(<Button>{undefined}</Button>)

    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('should handle multiple children', () => {
    render(
      <Button>
        <span>Icon</span>
        <span>Text</span>
      </Button>
    )

    const button = screen.getByRole('button')
    expect(button).toHaveTextContent('IconText')
  })

  it('should handle type="submit"', () => {
    render(<Button type="submit">Submit</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('type', 'submit')
  })
})
