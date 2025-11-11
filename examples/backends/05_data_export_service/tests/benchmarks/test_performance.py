"""Performance benchmarks for Data Export Service."""

import pytest
import time
import asyncio
import orjson
import msgpack

from src.main import (
    JSONExporter,
    MessagePackExporter,
    LZ4Compression,
    SnappyCompression,
    GZIPCompression,
    DataRecord,
)


class TestSerializationPerformance:
    """Test serialization performance."""

    @pytest.mark.benchmark
    def test_orjson_vs_stdlib(self):
        """Test orjson vs stdlib json (target: 9.05x faster)."""
        import json

        data = [
            {
                "id": i,
                "user_id": f"user{i}",
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "metadata": {"key": "value", "list": [1, 2, 3]},
            }
            for i in range(1000)
        ]

        # orjson
        operations = 1000
        start = time.perf_counter()

        for _ in range(operations):
            orjson.dumps(data)

        elapsed_orjson = time.perf_counter() - start

        # stdlib json
        start = time.perf_counter()

        for _ in range(operations):
            json.dumps(data)

        elapsed_stdlib = time.perf_counter() - start

        speedup = elapsed_stdlib / elapsed_orjson

        print(f"\norjson speedup: {speedup:.2f}x vs stdlib json")
        assert speedup > 3.0  # At least 3x faster

    @pytest.mark.benchmark
    def test_msgpack_vs_json(self):
        """Test MessagePack vs JSON (target: 5x faster)."""
        import json

        data = [
            {
                "id": i,
                "user_id": f"user{i}",
                "name": f"User {i}",
            }
            for i in range(1000)
        ]

        # MessagePack
        operations = 1000
        start = time.perf_counter()

        for _ in range(operations):
            msgpack.packb(data)

        elapsed_msgpack = time.perf_counter() - start

        # JSON
        start = time.perf_counter()

        for _ in range(operations):
            json.dumps(data)

        elapsed_json = time.perf_counter() - start

        speedup = elapsed_json / elapsed_msgpack

        print(f"\nMessagePack speedup: {speedup:.2f}x vs JSON")
        assert speedup > 2.0  # At least 2x faster


class TestCompressionPerformance:
    """Test compression performance."""

    @pytest.mark.benchmark
    def test_lz4_vs_gzip(self):
        """Test LZ4 vs GZIP (target: 8.4x faster)."""
        import gzip

        data = b"hello world" * 10000  # 110KB

        # LZ4
        lz4_comp = LZ4Compression()
        operations = 1000
        start = time.perf_counter()

        for _ in range(operations):
            lz4_comp.compress(data)

        elapsed_lz4 = time.perf_counter() - start

        # GZIP
        start = time.perf_counter()

        for _ in range(operations):
            gzip.compress(data, compresslevel=6)

        elapsed_gzip = time.perf_counter() - start

        speedup = elapsed_gzip / elapsed_lz4

        print(f"\nLZ4 speedup: {speedup:.2f}x vs GZIP")
        assert speedup > 3.0  # At least 3x faster

    @pytest.mark.benchmark
    def test_compression_throughput(self):
        """Test compression throughput."""
        data = b"x" * 1024 * 1024  # 1MB

        compressors = {
            "LZ4": LZ4Compression(),
            "Snappy": SnappyCompression(),
            "GZIP": GZIPCompression(level=6),
        }

        for name, compressor in compressors.items():
            operations = 100
            start = time.perf_counter()

            for _ in range(operations):
                compressor.compress(data)

            elapsed = time.perf_counter() - start
            mb_per_sec = (operations * len(data) / 1024 / 1024) / elapsed

            print(f"\n{name} throughput: {mb_per_sec:.2f} MB/sec")


class TestExportPerformance:
    """Test export performance."""

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_json_export_throughput(self):
        """Test JSON export throughput."""
        exporter = JSONExporter()

        async def generate_records():
            for i in range(10000):
                yield DataRecord(
                    id=i,
                    user_id=f"user{i}",
                    name=f"User {i}",
                    email=f"user{i}@example.com",
                    created_at="2024-01-01",
                    status="active",
                    metadata={},
                )

        start = time.perf_counter()

        count = 0
        async for chunk in exporter.export_stream(generate_records(), chunk_size=1000):
            count += 1

        elapsed = time.perf_counter() - start
        records_per_sec = 10000 / elapsed

        print(f"\nJSON export throughput: {records_per_sec:.0f} records/sec")
        assert records_per_sec > 50000  # Target: 50K+ records/sec

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_high_volume_export(self):
        """Test high-volume export (10M records target)."""
        from src.main import ExportService

        service = ExportService()

        # Create job for 100K records (scaled down for testing)
        from src.main import ExportFormat, CompressionType
        job = service.create_job(
            format=ExportFormat.JSON,
            compression=CompressionType.LZ4,
            total_records=100000,
        )

        start = time.perf_counter()

        await service.process_export(job, record_count=100000)

        elapsed = time.perf_counter() - start
        records_per_sec = 100000 / elapsed

        print(f"\nHigh-volume export: {records_per_sec:.0f} records/sec")
        print(f"Time for 100K records: {elapsed:.2f}s")

        # Scale to 10M estimate
        estimated_10m_time = (10000000 / records_per_sec)
        print(f"Estimated time for 10M records: {estimated_10m_time:.2f}s")

        assert records_per_sec > 50000  # Target: 50K+ records/sec
        assert estimated_10m_time < 300  # Should be under 5 minutes


class TestEndToEndPerformance:
    """Test end-to-end export performance."""

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_json_lz4_pipeline(self):
        """Test JSON + LZ4 pipeline performance."""
        from src.main import ExportService, ExportFormat, CompressionType

        service = ExportService()

        job = service.create_job(
            format=ExportFormat.JSON,
            compression=CompressionType.LZ4,
            total_records=50000,
        )

        start = time.perf_counter()

        await service.process_export(job, record_count=50000)

        elapsed = time.perf_counter() - start
        records_per_sec = 50000 / elapsed
        records_per_min = records_per_sec * 60

        print(f"\nJSON + LZ4 pipeline: {records_per_min:.0f} records/min")
        assert records_per_min > 1000000  # Target: 1M+ records/min

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_msgpack_snappy_pipeline(self):
        """Test MessagePack + Snappy pipeline performance."""
        from src.main import ExportService, ExportFormat, CompressionType

        service = ExportService()

        job = service.create_job(
            format=ExportFormat.MSGPACK,
            compression=CompressionType.SNAPPY,
            total_records=50000,
        )

        start = time.perf_counter()

        await service.process_export(job, record_count=50000)

        elapsed = time.perf_counter() - start
        records_per_sec = 50000 / elapsed
        records_per_min = records_per_sec * 60

        print(f"\nMessagePack + Snappy pipeline: {records_per_min:.0f} records/min")
        assert records_per_min > 1000000  # Target: 1M+ records/min
