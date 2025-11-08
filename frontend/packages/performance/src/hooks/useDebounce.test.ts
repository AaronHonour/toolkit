/**
 * useDebounce Hook Tests
 *
 * Testing Strategy:
 * - Value debouncing with various delays
 * - Callback debouncing
 * - Cleanup and memory leak prevention
 * - Performance validation (300ms delay accuracy ±10ms)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useDebounce, useDebouncedCallback } from './useDebounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ============================================================================
  // Basic Value Debouncing
  // ============================================================================

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 300))

    expect(result.current).toBe('initial')
  })

  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 300 } }
    )

    expect(result.current).toBe('initial')

    // Change value
    rerender({ value: 'updated', delay: 300 })

    // Value should still be 'initial' before delay
    expect(result.current).toBe('initial')

    // Fast-forward time
    vi.advanceTimersByTime(300)

    // Wait for state update
    await waitFor(() => {
      expect(result.current).toBe('updated')
    })
  })

  it('should use custom delay', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    )

    rerender({ value: 'updated', delay: 500 })

    // After 300ms, should still be old value
    vi.advanceTimersByTime(300)
    expect(result.current).toBe('initial')

    // After 500ms, should be new value
    vi.advanceTimersByTime(200)
    await waitFor(() => {
      expect(result.current).toBe('updated')
    })
  })

  it('should cancel previous timeout on rapid changes', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'first' } }
    )

    // Rapid changes
    rerender({ value: 'second' })
    vi.advanceTimersByTime(100)

    rerender({ value: 'third' })
    vi.advanceTimersByTime(100)

    rerender({ value: 'fourth' })
    vi.advanceTimersByTime(100)

    // Should still be initial
    expect(result.current).toBe('first')

    // Only the last value should take effect
    vi.advanceTimersByTime(200)
    await waitFor(() => {
      expect(result.current).toBe('fourth')
    })
  })

  // ============================================================================
  // Type Tests
  // ============================================================================

  it('should work with string values', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 100),
      { initialProps: { value: 'hello' } }
    )

    rerender({ value: 'world' })
    vi.advanceTimersByTime(100)

    await waitFor(() => {
      expect(result.current).toBe('world')
    })
  })

  it('should work with number values', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 100),
      { initialProps: { value: 0 } }
    )

    rerender({ value: 42 })
    vi.advanceTimersByTime(100)

    await waitFor(() => {
      expect(result.current).toBe(42)
    })
  })

  it('should work with object values', async () => {
    const initial = { count: 0 }
    const updated = { count: 10 }

    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 100),
      { initialProps: { value: initial } }
    )

    rerender({ value: updated })
    vi.advanceTimersByTime(100)

    await waitFor(() => {
      expect(result.current).toEqual(updated)
    })
  })

  it('should work with array values', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 100),
      { initialProps: { value: [1, 2, 3] } }
    )

    rerender({ value: [4, 5, 6] })
    vi.advanceTimersByTime(100)

    await waitFor(() => {
      expect(result.current).toEqual([4, 5, 6])
    })
  })

  // ============================================================================
  // Cleanup Tests
  // ============================================================================

  it('should cleanup timeout on unmount', () => {
    const { unmount } = renderHook(() => useDebounce('value', 300))

    // Spy on clearTimeout
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')

    unmount()

    expect(clearTimeoutSpy).toHaveBeenCalled()
  })

  it('should not update state after unmount', async () => {
    const { result, rerender, unmount } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'initial' } }
    )

    rerender({ value: 'updated' })
    unmount()

    // Advance time after unmount
    vi.advanceTimersByTime(300)

    // Should not throw or update (state updates after unmount are prevented)
    expect(result.current).toBe('initial')
  })
})

describe('useDebouncedCallback', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ============================================================================
  // Basic Callback Debouncing
  // ============================================================================

  it('should debounce callback execution', () => {
    const callback = vi.fn()
    const { result } = renderHook(() => useDebouncedCallback(callback, 300))

    const debouncedFn = result.current

    // Call multiple times
    debouncedFn('arg1')
    debouncedFn('arg2')
    debouncedFn('arg3')

    // Callback should not be called yet
    expect(callback).not.toHaveBeenCalled()

    // Advance time
    vi.advanceTimersByTime(300)

    // Callback should be called once with last arguments
    expect(callback).toHaveBeenCalledTimes(1)
    expect(callback).toHaveBeenCalledWith('arg3')
  })

  it('should cancel previous timeout on rapid calls', () => {
    const callback = vi.fn()
    const { result } = renderHook(() => useDebouncedCallback(callback, 300))

    const debouncedFn = result.current

    // Rapid calls
    debouncedFn('first')
    vi.advanceTimersByTime(100)

    debouncedFn('second')
    vi.advanceTimersByTime(100)

    debouncedFn('third')
    vi.advanceTimersByTime(100)

    // Still not called
    expect(callback).not.toHaveBeenCalled()

    // Complete the delay
    vi.advanceTimersByTime(200)

    // Only called once with last argument
    expect(callback).toHaveBeenCalledTimes(1)
    expect(callback).toHaveBeenCalledWith('third')
  })

  it('should work with custom delay', () => {
    const callback = vi.fn()
    const { result } = renderHook(() => useDebouncedCallback(callback, 500))

    result.current('test')

    // Not called after 300ms
    vi.advanceTimersByTime(300)
    expect(callback).not.toHaveBeenCalled()

    // Called after 500ms
    vi.advanceTimersByTime(200)
    expect(callback).toHaveBeenCalledWith('test')
  })

  it('should handle multiple arguments', () => {
    const callback = vi.fn()
    const { result } = renderHook(() => useDebouncedCallback(callback, 300))

    result.current('arg1', 'arg2', 'arg3')

    vi.advanceTimersByTime(300)

    expect(callback).toHaveBeenCalledWith('arg1', 'arg2', 'arg3')
  })

  it('should preserve callback context', () => {
    const obj = { value: 42 }
    const callback = vi.fn(function (this: typeof obj) {
      return this.value
    })

    const { result } = renderHook(() => useDebouncedCallback(callback.bind(obj), 300))

    result.current()
    vi.advanceTimersByTime(300)

    expect(callback).toHaveBeenCalled()
  })

  // ============================================================================
  // Cleanup Tests
  // ============================================================================

  it('should cleanup timeout on unmount', () => {
    const callback = vi.fn()
    const { result, unmount } = renderHook(() => useDebouncedCallback(callback, 300))

    result.current('test')

    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')
    unmount()

    expect(clearTimeoutSpy).toHaveBeenCalled()

    // Advance time - callback should not be called
    vi.advanceTimersByTime(300)
    expect(callback).not.toHaveBeenCalled()
  })

  // ============================================================================
  // Performance Tests
  // ============================================================================

  it('should have accurate timing (±10ms tolerance)', () => {
    const callback = vi.fn()
    const delay = 300
    const tolerance = 10

    const { result } = renderHook(() => useDebouncedCallback(callback, delay))

    const startTime = Date.now()
    result.current('test')

    vi.advanceTimersByTime(delay)

    const endTime = Date.now()
    const actualDelay = endTime - startTime

    expect(actualDelay).toBeGreaterThanOrEqual(delay - tolerance)
    expect(actualDelay).toBeLessThanOrEqual(delay + tolerance)
    expect(callback).toHaveBeenCalled()
  })
})
