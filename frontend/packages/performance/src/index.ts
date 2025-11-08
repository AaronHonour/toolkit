/**
 * Performance Utilities
 *
 * High-performance hooks mirroring backend algorithms
 */

// Virtual Scrolling (like RingBuffer)
export { useVirtualScroll, type VirtualScrollOptions, type VirtualScrollResult } from './hooks/useVirtualScroll';

// LRU Memoization (like LRUCache)
export { useLRUMemo, useClearLRUCache } from './hooks/useLRUMemo';

// Debouncing (like rate limiting)
export { useDebounce, useDebouncedCallback } from './hooks/useDebounce';

// Throttling (like rate limiting)
export { useThrottle, useThrottledCallback } from './hooks/useThrottle';

// Worker Pool (like ObjectPool)
export { useWorkerPool } from './hooks/useWorkerPool';

// Performance Monitoring
export { usePerformanceMonitor, useMeasureAsync, type PerformanceMetrics } from './hooks/usePerformanceMonitor';
