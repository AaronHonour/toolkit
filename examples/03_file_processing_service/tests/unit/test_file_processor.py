"""Unit tests for FileProcessor and Pipeline."""

import pytest
import asyncio
from uuid import UUID

from src.main import FileProcessor, Pipeline, ProcessingStage
from toolkit.algorithms import ObjectPool, BufferPool, PoolConfig


class TestFileProcessor:
    """Test FileProcessor."""

    def test_processor_creation(self):
        """Test processor creation."""
        processor = FileProcessor()
        assert processor is not None

    def test_uppercase_processing(self):
        """Test uppercase operation."""
        processor = FileProcessor()
        data = b"hello world"

        result = processor.process(data, "uppercase")

        assert result == b"HELLO WORLD"

    def test_lowercase_processing(self):
        """Test lowercase operation."""
        processor = FileProcessor()
        data = b"HELLO WORLD"

        result = processor.process(data, "lowercase")

        assert result == b"hello world"

    def test_no_operation(self):
        """Test no operation (passthrough)."""
        processor = FileProcessor()
        data = b"Hello World"

        result = processor.process(data, "none")

        assert result == data

    def test_empty_file(self):
        """Test processing empty file."""
        processor = FileProcessor()
        data = b""

        result = processor.process(data, "uppercase")

        assert result == b""

    def test_large_file_processing(self):
        """Test processing large file."""
        processor = FileProcessor()
        data = b"hello world" * 10000  # 110KB

        result = processor.process(data, "uppercase")

        assert len(result) == len(data)
        assert result == data.upper()

    def test_binary_data(self):
        """Test processing binary data."""
        processor = FileProcessor()
        data = bytes(range(256))

        result = processor.process(data, "none")

        assert result == data

    def test_multiple_operations(self):
        """Test multiple operations in sequence."""
        processor = FileProcessor()
        data = b"Hello World"

        # Chain operations
        result1 = processor.process(data, "uppercase")
        result2 = processor.process(result1, "lowercase")

        assert result1 == b"HELLO WORLD"
        assert result2 == b"hello world"


class TestPipeline:
    """Test Pipeline with ObjectPool and BufferPool."""

    @pytest.mark.asyncio
    async def test_pipeline_creation(self):
        """Test pipeline creation."""
        pipeline = Pipeline(num_workers=4)

        assert pipeline.processor_pool is not None
        assert pipeline.buffer_pool is not None
        assert len(pipeline.jobs) == 0

    @pytest.mark.asyncio
    async def test_submit_job(self):
        """Test submitting a job."""
        pipeline = Pipeline()

        job_id = await pipeline.submit_job(
            file_data=b"test data",
            filename="test.txt",
            operation="uppercase",
        )

        assert isinstance(job_id, UUID)
        assert job_id in pipeline.jobs

    @pytest.mark.asyncio
    async def test_job_tracking(self):
        """Test job tracking information."""
        pipeline = Pipeline()

        job_id = await pipeline.submit_job(
            file_data=b"test data",
            filename="test.txt",
            operation="uppercase",
        )

        job = pipeline.jobs[job_id]
        assert job['filename'] == "test.txt"
        assert job['operation'] == "uppercase"
        assert job['stage'] == ProcessingStage.UPLOADED

    @pytest.mark.asyncio
    async def test_process_job(self):
        """Test processing a job."""
        pipeline = Pipeline()

        job_id = await pipeline.submit_job(
            file_data=b"hello",
            filename="test.txt",
            operation="uppercase",
        )

        result = await pipeline.process_job(job_id)

        assert result == b"HELLO"
        assert pipeline.jobs[job_id]['stage'] == ProcessingStage.COMPLETED

    @pytest.mark.asyncio
    async def test_multiple_jobs(self):
        """Test submitting multiple jobs."""
        pipeline = Pipeline()

        job_ids = []
        for i in range(10):
            job_id = await pipeline.submit_job(
                file_data=f"data{i}".encode(),
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            job_ids.append(job_id)

        assert len(pipeline.jobs) == 10
        assert all(job_id in pipeline.jobs for job_id in job_ids)

    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self):
        """Test concurrent job processing."""
        pipeline = Pipeline()

        # Submit multiple jobs
        job_ids = []
        for i in range(5):
            job_id = await pipeline.submit_job(
                file_data=f"data{i}".encode(),
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            job_ids.append(job_id)

        # Process concurrently
        tasks = [pipeline.process_job(job_id) for job_id in job_ids]
        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result == f"DATA{i}".encode()

    @pytest.mark.asyncio
    async def test_object_pool_reuse(self):
        """Test ObjectPool processor reuse."""
        pipeline = Pipeline()

        # Process multiple jobs (should reuse processors)
        for i in range(20):
            job_id = await pipeline.submit_job(
                file_data=b"test",
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            await pipeline.process_job(job_id)

        # Verify pool statistics
        stats = pipeline.processor_pool.stats()
        assert stats['total_acquisitions'] >= 20

    @pytest.mark.asyncio
    async def test_buffer_pool_usage(self):
        """Test BufferPool usage."""
        pipeline = Pipeline()

        # Get buffer
        buffer = await pipeline.buffer_pool.acquire()
        assert buffer is not None
        assert len(buffer) == 8192

        # Return buffer
        await pipeline.buffer_pool.release(buffer)

    @pytest.mark.asyncio
    async def test_get_job_status(self):
        """Test getting job status."""
        pipeline = Pipeline()

        job_id = await pipeline.submit_job(
            file_data=b"test",
            filename="test.txt",
            operation="uppercase",
        )

        status = pipeline.get_job_status(job_id)

        assert status is not None
        assert status['id'] == job_id
        assert status['stage'] == ProcessingStage.UPLOADED

    @pytest.mark.asyncio
    async def test_invalid_job_id(self):
        """Test handling invalid job ID."""
        pipeline = Pipeline()

        from uuid import uuid4
        invalid_id = uuid4()

        status = pipeline.get_job_status(invalid_id)

        assert status is None

    @pytest.mark.asyncio
    async def test_pipeline_stats(self):
        """Test pipeline statistics."""
        pipeline = Pipeline()

        # Process some jobs
        for i in range(5):
            job_id = await pipeline.submit_job(
                file_data=b"test",
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            await pipeline.process_job(job_id)

        stats = pipeline.stats
        assert stats['total_processed'] == 5

    @pytest.mark.asyncio
    async def test_failed_job_tracking(self):
        """Test tracking failed jobs."""
        pipeline = Pipeline()

        job_id = await pipeline.submit_job(
            file_data=b"test",
            filename="test.txt",
            operation="invalid_operation",
        )

        # Try to process (should handle gracefully)
        try:
            await pipeline.process_job(job_id)
        except Exception:
            pass

        # Job should still be tracked
        assert job_id in pipeline.jobs

    @pytest.mark.asyncio
    async def test_high_throughput(self):
        """Test high-throughput processing."""
        pipeline = Pipeline(num_workers=10)

        # Submit 100 jobs
        job_ids = []
        for i in range(100):
            job_id = await pipeline.submit_job(
                file_data=f"data{i}".encode(),
                filename=f"file{i}.txt",
                operation="uppercase",
            )
            job_ids.append(job_id)

        # Process all concurrently
        import time
        start = time.time()

        tasks = [pipeline.process_job(job_id) for job_id in job_ids]
        await asyncio.gather(*tasks)

        elapsed = time.time() - start
        throughput = 100 / elapsed

        # Should handle 100 files quickly
        assert elapsed < 2.0  # Less than 2 seconds
        assert throughput > 50  # More than 50 files/sec

    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory efficiency with buffer pooling."""
        pipeline = Pipeline()

        # Acquire and release buffers multiple times
        for _ in range(100):
            buffer = await pipeline.buffer_pool.acquire()
            # Use buffer
            await pipeline.buffer_pool.release(buffer)

        # Should reuse buffers efficiently
        stats = pipeline.buffer_pool.stats()
        assert stats['total_created'] < 100  # Reused buffers

    @pytest.mark.asyncio
    async def test_different_file_sizes(self):
        """Test processing different file sizes."""
        pipeline = Pipeline()

        sizes = [100, 1000, 10000, 100000]

        for size in sizes:
            data = b"x" * size
            job_id = await pipeline.submit_job(
                file_data=data,
                filename=f"file_{size}.txt",
                operation="uppercase",
            )

            result = await pipeline.process_job(job_id)
            assert len(result) == size

    @pytest.mark.asyncio
    async def test_pipeline_cleanup(self):
        """Test pipeline cleanup."""
        pipeline = Pipeline()

        # Submit jobs
        for i in range(10):
            await pipeline.submit_job(
                file_data=b"test",
                filename=f"file{i}.txt",
                operation="uppercase",
            )

        # Cleanup (if implemented)
        # pipeline.cleanup()

        # For now just verify jobs exist
        assert len(pipeline.jobs) == 10
