"""Performance benchmarks for File Processing Service."""

import pytest
import asyncio
import time

from src.main import FileProcessor, Pipeline
from unistax.algorithms import ObjectPool, BufferPool, PoolConfig


class TestObjectPoolPerformance:
    """Test ObjectPool performance (target: 2.35x speedup)."""

    @pytest.mark.benchmark
    def test_object_pool_vs_new_objects(self):
        """Test ObjectPool vs creating new objects."""
        # Test with ObjectPool
        pool = ObjectPool(
            factory=lambda: FileProcessor(),
            config=PoolConfig(max_size=100, min_size=10),
        )

        operations = 10000
        start = time.perf_counter()

        for _ in range(operations):
            obj = pool.acquire()
            pool.release(obj)

        elapsed_pool = time.perf_counter() - start

        # Test without pool (creating new objects)
        start = time.perf_counter()

        for _ in range(operations):
            obj = FileProcessor()  # Create new object each time

        elapsed_new = time.perf_counter() - start

        speedup = elapsed_new / elapsed_pool

        print(f"\nObjectPool speedup: {speedup:.2f}x")
        assert speedup > 1.5  # At least 1.5x speedup

    @pytest.mark.benchmark
    def test_object_pool_throughput(self):
        """Test ObjectPool acquisition throughput."""
        pool = ObjectPool(
            factory=lambda: FileProcessor(),
            config=PoolConfig(max_size=100, min_size=10),
        )

        operations = 100000
        start = time.perf_counter()

        for _ in range(operations):
            obj = pool.acquire()
            pool.release(obj)

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nObjectPool throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 50000  # Target: 50K+ ops/sec


class TestBufferPoolPerformance:
    """Test BufferPool performance (target: 46K+ ops/sec)."""

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_buffer_pool_throughput(self):
        """Test BufferPool throughput."""
        pool = BufferPool(buffer_size=8192, max_buffers=1000)

        operations = 10000
        start = time.perf_counter()

        for _ in range(operations):
            buffer = await pool.acquire()
            await pool.release(buffer)

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nBufferPool throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 40000  # Target: 40K+ ops/sec

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_buffer_pool_zero_copy(self):
        """Test BufferPool zero-copy performance."""
        pool = BufferPool(buffer_size=8192, max_buffers=100)

        operations = 5000
        start = time.perf_counter()

        for _ in range(operations):
            buffer = await pool.acquire()
            # Simulate I/O operation
            buffer[:100] = b"x" * 100
            await pool.release(buffer)

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nBufferPool zero-copy: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 30000


class TestFileProcessingPerformance:
    """Test file processing performance."""

    @pytest.mark.benchmark
    def test_file_processor_throughput(self):
        """Test FileProcessor throughput."""
        processor = FileProcessor()
        data = b"hello world" * 100  # 1.1KB

        operations = 10000
        start = time.perf_counter()

        for _ in range(operations):
            processor.process(data, "uppercase")

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nFileProcessor throughput: {ops_per_sec:.0f} files/sec")
        assert ops_per_sec > 50000  # Target: 50K+ files/sec

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_pipeline_throughput(self):
        """Test Pipeline throughput."""
        pipeline = Pipeline(num_workers=10)

        operations = 1000
        start = time.perf_counter()

        # Submit jobs
        job_ids = []
        for i in range(operations):
            job_id = await pipeline.submit_job(
                file_data=b"test data",
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            job_ids.append(job_id)

        # Process all jobs
        tasks = [pipeline.process_job(job_id) for job_id in job_ids]
        await asyncio.gather(*tasks)

        elapsed = time.perf_counter() - start
        files_per_sec = operations / elapsed
        files_per_min = files_per_sec * 60

        print(f"\nPipeline throughput: {files_per_min:.0f} files/min")
        assert files_per_min > 10000  # Target: 10K+ files/min


class TestEndToEndPerformance:
    """Test end-to-end processing performance."""

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_high_volume_processing(self):
        """Test high-volume file processing."""
        pipeline = Pipeline(num_workers=20)

        # Process 10K files
        operations = 10000
        file_size = 1024  # 1KB

        start = time.perf_counter()

        job_ids = []
        for i in range(operations):
            data = b"x" * file_size
            job_id = await pipeline.submit_job(
                file_data=data,
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            job_ids.append(job_id)

        # Process all
        tasks = [pipeline.process_job(job_id) for job_id in job_ids]
        await asyncio.gather(*tasks)

        elapsed = time.perf_counter() - start
        files_per_sec = operations / elapsed
        files_per_min = files_per_sec * 60

        print(f"\nHigh-volume throughput: {files_per_min:.0f} files/min")
        print(f"Total data processed: {operations * file_size / 1024 / 1024:.2f} MB")

        assert files_per_min > 10000  # Target: 10K+ files/min

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory efficiency with buffer pooling."""
        pipeline = Pipeline()

        # Process many files (should reuse buffers)
        operations = 1000

        for i in range(operations):
            buffer = await pipeline.buffer_pool.acquire()
            # Use buffer
            await pipeline.buffer_pool.release(buffer)

        stats = pipeline.buffer_pool.stats()
        reuse_ratio = stats['total_reused'] / operations if operations > 0 else 0

        print(f"\nBuffer reuse ratio: {reuse_ratio:.2%}")
        assert stats['total_created'] < operations / 2  # Should reuse at least 50%

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_different_file_sizes(self):
        """Test performance with different file sizes."""
        pipeline = Pipeline()

        file_sizes = [1024, 10240, 102400, 1024000]  # 1KB, 10KB, 100KB, 1MB

        for size in file_sizes:
            data = b"x" * size

            operations = 100
            start = time.perf_counter()

            for i in range(operations):
                job_id = await pipeline.submit_job(
                    file_data=data,
                    filename=f"file{i}.txt",
                    operation="uppercase",
                )
                await pipeline.process_job(job_id)

            elapsed = time.perf_counter() - start
            throughput_mbps = (operations * size / 1024 / 1024) / elapsed

            print(f"\nFile size {size} bytes: {throughput_mbps:.2f} MB/sec")
            assert throughput_mbps > 1  # At least 1 MB/sec
