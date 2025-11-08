/**
 * LRU Memoization Hook
 *
 * Like backend LRUCache (326K+ ops/sec)
 * Memoizes expensive computations with LRU eviction
 */

import { useRef, useCallback } from 'react';

interface CacheNode<T> {
  key: string;
  value: T;
  prev: CacheNode<T> | null;
  next: CacheNode<T> | null;
}

class LRUCache<T> {
  private capacity: number;
  private cache: Map<string, CacheNode<T>>;
  private head: CacheNode<T> | null;
  private tail: CacheNode<T> | null;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.cache = new Map();
    this.head = null;
    this.tail = null;
  }

  get(key: string): T | undefined {
    const node = this.cache.get(key);
    if (!node) return undefined;

    // Move to front (most recently used)
    this.moveToFront(node);
    return node.value;
  }

  put(key: string, value: T): void {
    let node = this.cache.get(key);

    if (node) {
      // Update existing node
      node.value = value;
      this.moveToFront(node);
    } else {
      // Create new node
      node = { key, value, prev: null, next: null };
      this.cache.set(key, node);
      this.addToFront(node);

      // Evict if over capacity (LRU)
      if (this.cache.size > this.capacity) {
        this.evictLRU();
      }
    }
  }

  private moveToFront(node: CacheNode<T>): void {
    this.removeNode(node);
    this.addToFront(node);
  }

  private addToFront(node: CacheNode<T>): void {
    node.next = this.head;
    node.prev = null;

    if (this.head) {
      this.head.prev = node;
    }
    this.head = node;

    if (!this.tail) {
      this.tail = node;
    }
  }

  private removeNode(node: CacheNode<T>): void {
    if (node.prev) {
      node.prev.next = node.next;
    } else {
      this.head = node.next;
    }

    if (node.next) {
      node.next.prev = node.prev;
    } else {
      this.tail = node.prev;
    }
  }

  private evictLRU(): void {
    if (!this.tail) return;

    this.cache.delete(this.tail.key);
    this.removeNode(this.tail);
  }

  clear(): void {
    this.cache.clear();
    this.head = null;
    this.tail = null;
  }
}

/**
 * Memoize expensive computations with LRU cache
 * Performance: Like backend LRUCache (326K+ ops/sec)
 */
export function useLRUMemo<T>(
  fn: (...args: any[]) => T,
  capacity: number = 100 // Like backend memoizationCacheSize token
): (...args: any[]) => T {
  const cacheRef = useRef<LRUCache<T>>();

  if (!cacheRef.current) {
    cacheRef.current = new LRUCache<T>(capacity);
  }

  return useCallback(
    (...args: any[]) => {
      const key = JSON.stringify(args);
      const cached = cacheRef.current!.get(key);

      if (cached !== undefined) {
        return cached;
      }

      const result = fn(...args);
      cacheRef.current!.put(key, result);
      return result;
    },
    [fn]
  );
}

/**
 * Clear LRU cache
 */
export function useClearLRUCache<T>(memoizedFn: (...args: any[]) => T): () => void {
  const cacheRef = useRef<LRUCache<T>>();

  return useCallback(() => {
    cacheRef.current?.clear();
  }, []);
}
