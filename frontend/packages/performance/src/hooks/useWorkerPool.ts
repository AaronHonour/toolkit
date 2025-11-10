/**
 * Web Worker Pool Hook
 *
 * Like backend ObjectPool - reuses workers for heavy computation
 * Performance: Offloads work to background threads
 */

import { useRef, useCallback, useEffect } from 'react';

interface WorkerTask<T, R> {
  data: T;
  resolve: (result: R) => void;
  reject: (error: Error) => void;
}

class WorkerPool {
  private workers: Worker[] = [];
  private availableWorkers: Worker[] = [];
  private taskQueue: WorkerTask<any, any>[] = [];
  private workerUrl: string;

  constructor(workerUrl: string, poolSize: number = navigator.hardwareConcurrency || 4) {
    this.workerUrl = workerUrl;
    this.initializePool(poolSize);
  }

  private initializePool(size: number): void {
    for (let i = 0; i < size; i++) {
      const worker = new Worker(this.workerUrl, { type: 'module' });
      this.workers.push(worker);
      this.availableWorkers.push(worker);
    }
  }

  async execute<T, R>(data: T): Promise<R> {
    return new Promise((resolve, reject) => {
      const task: WorkerTask<T, R> = { data, resolve, reject };

      if (this.availableWorkers.length > 0) {
        this.runTask(task);
      } else {
        this.taskQueue.push(task);
      }
    });
  }

  private runTask<T, R>(task: WorkerTask<T, R>): void {
    const worker = this.availableWorkers.pop()!;

    const onMessage = (e: MessageEvent) => {
      worker.removeEventListener('message', onMessage);
      worker.removeEventListener('error', onError);

      this.availableWorkers.push(worker);
      task.resolve(e.data);

      // Process next task in queue
      if (this.taskQueue.length > 0) {
        const nextTask = this.taskQueue.shift()!;
        this.runTask(nextTask);
      }
    };

    const onError = (error: ErrorEvent) => {
      worker.removeEventListener('message', onMessage);
      worker.removeEventListener('error', onError);

      this.availableWorkers.push(worker);
      task.reject(new Error(error.message));

      // Process next task in queue
      if (this.taskQueue.length > 0) {
        const nextTask = this.taskQueue.shift()!;
        this.runTask(nextTask);
      }
    };

    worker.addEventListener('message', onMessage);
    worker.addEventListener('error', onError);
    worker.postMessage(task.data);
  }

  terminate(): void {
    this.workers.forEach(worker => worker.terminate());
    this.workers = [];
    this.availableWorkers = [];
    this.taskQueue = [];
  }
}

/**
 * Use Web Worker pool for heavy computations
 * Like backend ObjectPool - reuses workers efficiently
 */
export function useWorkerPool(
  workerUrl: string,
  poolSize?: number
): {
  execute: <T, R>(data: T) => Promise<R>;
  terminate: () => void;
} {
  const poolRef = useRef<WorkerPool>();

  if (!poolRef.current) {
    poolRef.current = new WorkerPool(workerUrl, poolSize);
  }

  const execute = useCallback(<T, R>(data: T): Promise<R> => {
    return poolRef.current!.execute<T, R>(data);
  }, []);

  const terminate = useCallback(() => {
    poolRef.current?.terminate();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      poolRef.current?.terminate();
    };
  }, []);

  return { execute, terminate };
}
