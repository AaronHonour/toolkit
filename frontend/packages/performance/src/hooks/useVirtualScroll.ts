/**
 * Virtual Scroll Hook
 *
 * Like backend RingBuffer - efficient handling of large lists
 * Target: 60fps with 1M+ items
 */

import { useState, useEffect, useRef, useMemo } from 'react';

export interface VirtualScrollOptions {
  /** Total number of items */
  itemCount: number;
  /** Height of each item in pixels */
  itemHeight: number;
  /** Container height in pixels */
  containerHeight: number;
  /** Overscan count (items to render outside viewport) */
  overscan?: number;
}

export interface VirtualScrollResult {
  /** Items to render */
  virtualItems: Array<{
    index: number;
    start: number;
    size: number;
  }>;
  /** Total height of scrollable area */
  totalHeight: number;
  /** Scroll handler */
  onScroll: (e: React.UIEvent<HTMLElement>) => void;
  /** Container props */
  containerProps: {
    style: React.CSSProperties;
  };
  /** Wrapper props */
  wrapperProps: {
    style: React.CSSProperties;
  };
}

/**
 * Virtual scrolling hook for large lists
 * Performance: Like RingBuffer (284K+ ops/sec)
 */
export function useVirtualScroll({
  itemCount,
  itemHeight,
  containerHeight,
  overscan = 5, // Like backend virtualScrollOverscan token
}: VirtualScrollOptions): VirtualScrollResult {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollingRef = useRef<number>();

  // Calculate visible range (memoized for performance)
  const virtualItems = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      itemCount - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );

    const items = [];
    for (let i = startIndex; i <= endIndex; i++) {
      items.push({
        index: i,
        start: i * itemHeight,
        size: itemHeight,
      });
    }

    return items;
  }, [scrollTop, itemHeight, containerHeight, itemCount, overscan]);

  const totalHeight = itemCount * itemHeight;

  // Scroll handler with performance optimization
  const onScroll = (e: React.UIEvent<HTMLElement>) => {
    const target = e.currentTarget;

    // Debounce scroll updates for 60fps (< 16ms per frame)
    if (scrollingRef.current) {
      cancelAnimationFrame(scrollingRef.current);
    }

    scrollingRef.current = requestAnimationFrame(() => {
      setScrollTop(target.scrollTop);
    });
  };

  // Cleanup
  useEffect(() => {
    return () => {
      if (scrollingRef.current) {
        cancelAnimationFrame(scrollingRef.current);
      }
    };
  }, []);

  return {
    virtualItems,
    totalHeight,
    onScroll,
    containerProps: {
      style: {
        height: containerHeight,
        overflow: 'auto',
      },
    },
    wrapperProps: {
      style: {
        height: totalHeight,
        position: 'relative',
      },
    },
  };
}
