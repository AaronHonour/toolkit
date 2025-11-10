/**
 * Throttle Hook
 *
 * Like backend rate limiting - limits execution frequency
 * Performance: Ensures max 60fps (16ms intervals)
 */

import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Throttle a value
 * Like backend rate limiting - limits update frequency
 */
export function useThrottle<T>(value: T, interval: number = 16): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastUpdated = useRef<number>(Date.now());

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdated.current;

    if (timeSinceLastUpdate >= interval) {
      lastUpdated.current = now;
      setThrottledValue(value);
    } else {
      const timer = setTimeout(() => {
        lastUpdated.current = Date.now();
        setThrottledValue(value);
      }, interval - timeSinceLastUpdate);

      return () => {
        clearTimeout(timer);
      };
    }
  }, [value, interval]);

  return throttledValue;
}

/**
 * Throttle a callback function
 * Ensures function is called at most once per interval
 */
export function useThrottledCallback<T extends (...args: any[]) => any>(
  callback: T,
  interval: number = 16 // 60fps = 16.67ms per frame
): (...args: Parameters<T>) => void {
  const lastRan = useRef<number>(Date.now());
  const timeoutId = useRef<NodeJS.Timeout>();

  useEffect(() => {
    return () => {
      if (timeoutId.current) {
        clearTimeout(timeoutId.current);
      }
    };
  }, []);

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastRan = now - lastRan.current;

      if (timeSinceLastRan >= interval) {
        callback(...args);
        lastRan.current = now;
      } else {
        if (timeoutId.current) {
          clearTimeout(timeoutId.current);
        }

        timeoutId.current = setTimeout(() => {
          callback(...args);
          lastRan.current = Date.now();
        }, interval - timeSinceLastRan);
      }
    },
    [callback, interval]
  );
}
