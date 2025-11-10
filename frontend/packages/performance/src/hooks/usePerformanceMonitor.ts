/**
 * Performance Monitor Hook
 *
 * Like backend metrics tracking - monitors component performance
 * Target: Identify renders > 16ms (60fps threshold)
 */

import { useEffect, useRef } from 'react';

export interface PerformanceMetrics {
  componentName: string;
  renderTime: number;
  timestamp: number;
  fps: number;
}

/**
 * Monitor component render performance
 * Like backend performance tracking
 */
export function usePerformanceMonitor(componentName: string, enabled: boolean = false): void {
  const renderStart = useRef<number>(0);
  const frameCount = useRef<number>(0);
  const lastTime = useRef<number>(performance.now());

  useEffect(() => {
    if (!enabled) return;

    renderStart.current = performance.now();

    return () => {
      const renderTime = performance.now() - renderStart.current;
      const now = performance.now();
      const delta = now - lastTime.current;

      frameCount.current++;
      const fps = Math.round(1000 / (delta / frameCount.current));

      // Warn if render time exceeds 16ms (60fps threshold)
      if (renderTime > 16) {
        console.warn(`[Performance] ${componentName} render took ${renderTime.toFixed(2)}ms (target: < 16ms for 60fps)`);
      }

      // Log metrics
      const metrics: PerformanceMetrics = {
        componentName,
        renderTime,
        timestamp: now,
        fps,
      };

      // Can send to analytics service
      if (renderTime > 16) {
        console.log('[Performance Metrics]', metrics);
      }

      lastTime.current = now;
    };
  });
}

/**
 * Measure async operation performance
 */
export function useMeasureAsync<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  label: string
): T {
  return (async (...args: any[]) => {
    const start = performance.now();
    try {
      const result = await fn(...args);
      const duration = performance.now() - start;
      console.log(`[Async Performance] ${label}: ${duration.toFixed(2)}ms`);
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      console.error(`[Async Performance] ${label} failed after ${duration.toFixed(2)}ms`, error);
      throw error;
    }
  }) as T;
}
