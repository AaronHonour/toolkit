"""Unit tests for Exporters and Compression."""

import pytest
import asyncio

from src.main import (
    JSONExporter,
    CSVExporter,
    MessagePackExporter,
    LZ4Compression,
    SnappyCompression,
    GZIPCompression,
    DataRecord,
)


class TestJSONExporter:
    """Test JSONExporter with orjson."""

    @pytest.mark.asyncio
    async def test_json_export_empty(self):
        """Test exporting empty data."""
        exporter = JSONExporter()

        async def empty_records():
            return
            yield  # Make it a generator

        chunks = []
        async for chunk in exporter.export_stream(empty_records(), chunk_size=10):
            chunks.append(chunk)

        result = b''.join(chunks)
        assert result == b'[]'

    @pytest.mark.asyncio
    async def test_json_export_single_record(self):
        """Test exporting single record."""
        exporter = JSONExporter()

        async def single_record():
            yield DataRecord(
                id=1,
                user_id="user1",
                name="Test User",
                email="test@example.com",
                created_at="2024-01-01",
                status="active",
                metadata={},
            )

        chunks = []
        async for chunk in exporter.export_stream(single_record(), chunk_size=10):
            chunks.append(chunk)

        result = b''.join(chunks)
        assert result.startswith(b'[')
        assert result.endswith(b']')
        assert b'"user_id":"user1"' in result or b'"user_id": "user1"' in result

    @pytest.mark.asyncio
    async def test_json_export_multiple_records(self):
        """Test exporting multiple records."""
        exporter = JSONExporter()

        async def multiple_records():
            for i in range(5):
                yield DataRecord(
                    id=i,
                    user_id=f"user{i}",
                    name=f"User {i}",
                    email=f"user{i}@example.com",
                    created_at="2024-01-01",
                    status="active",
                    metadata={},
                )

        chunks = []
        async for chunk in exporter.export_stream(multiple_records(), chunk_size=10):
            chunks.append(chunk)

        result = b''.join(chunks)
        assert result.startswith(b'[')
        assert result.endswith(b']')


class TestCSVExporter:
    """Test CSVExporter."""

    @pytest.mark.asyncio
    async def test_csv_export_empty(self):
        """Test exporting empty data."""
        exporter = CSVExporter()

        async def empty_records():
            return
            yield

        chunks = []
        async for chunk in exporter.export_stream(empty_records(), chunk_size=10):
            chunks.append(chunk)

        result = b''.join(chunks)
        # Should have header
        assert b'id,user_id,name,email' in result

    @pytest.mark.asyncio
    async def test_csv_export_single_record(self):
        """Test exporting single record."""
        exporter = CSVExporter()

        async def single_record():
            yield DataRecord(
                id=1,
                user_id="user1",
                name="Test",
                email="test@example.com",
                created_at="2024-01-01",
                status="active",
                metadata={},
            )

        chunks = []
        async for chunk in exporter.export_stream(single_record(), chunk_size=10):
            chunks.append(chunk)

        result = b''.join(chunks)
        assert b'1,user1,Test,test@example.com' in result


class TestMessagePackExporter:
    """Test MessagePackExporter."""

    @pytest.mark.asyncio
    async def test_msgpack_export(self):
        """Test MessagePack export."""
        exporter = MessagePackExporter()

        async def records():
            yield DataRecord(
                id=1,
                user_id="user1",
                name="Test",
                email="test@example.com",
                created_at="2024-01-01",
                status="active",
                metadata={},
            )

        chunks = []
        async for chunk in exporter.export_stream(records(), chunk_size=10):
            chunks.append(chunk)

        # Should produce binary data
        assert len(chunks) > 0
        assert all(isinstance(c, bytes) for c in chunks)


class TestLZ4Compression:
    """Test LZ4 compression (8.4x faster)."""

    def test_lz4_compress(self):
        """Test LZ4 compression."""
        compressor = LZ4Compression()
        data = b"hello world" * 1000

        compressed = compressor.compress(data)

        assert len(compressed) < len(data)
        assert compressed != data

    def test_lz4_decompress(self):
        """Test LZ4 decompression."""
        compressor = LZ4Compression()
        data = b"hello world" * 1000

        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data

    def test_lz4_empty_data(self):
        """Test LZ4 with empty data."""
        compressor = LZ4Compression()
        data = b""

        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data


class TestSnappyCompression:
    """Test Snappy compression."""

    def test_snappy_compress(self):
        """Test Snappy compression."""
        compressor = SnappyCompression()
        data = b"hello world" * 1000

        compressed = compressor.compress(data)

        assert len(compressed) < len(data)

    def test_snappy_decompress(self):
        """Test Snappy decompression."""
        compressor = SnappyCompression()
        data = b"hello world" * 1000

        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data


class TestGZIPCompression:
    """Test GZIP compression."""

    def test_gzip_compress(self):
        """Test GZIP compression."""
        compressor = GZIPCompression(level=6)
        data = b"hello world" * 1000

        compressed = compressor.compress(data)

        assert len(compressed) < len(data)

    def test_gzip_decompress(self):
        """Test GZIP decompression."""
        compressor = GZIPCompression(level=6)
        data = b"hello world" * 1000

        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data

    def test_gzip_different_levels(self):
        """Test GZIP with different compression levels."""
        data = b"hello world" * 1000

        compressor_fast = GZIPCompression(level=1)
        compressor_slow = GZIPCompression(level=9)

        compressed_fast = compressor_fast.compress(data)
        compressed_slow = compressor_slow.compress(data)

        # Higher level should compress better
        assert len(compressed_slow) <= len(compressed_fast)
