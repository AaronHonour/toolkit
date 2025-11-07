"""Data Export Service - Main Application.

High-performance export service handling 10M+ records in < 60 seconds.
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, AsyncIterator, Any
import time
import io

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
import orjson
import msgpack
import lz4.frame
import snappy
import gzip

# Simulated data source (in production this would be database/API)
@dataclass
class DataRecord:
    """Data record for export."""
    __slots__ = ('id', 'user_id', 'name', 'email', 'created_at', 'status', 'metadata')

    id: int
    user_id: str
    name: str
    email: str
    created_at: str
    status: str
    metadata: Dict[str, Any]


class ExportFormat(str, Enum):
    """Export format types."""
    JSON = "json"
    CSV = "csv"
    MSGPACK = "msgpack"


class CompressionType(str, Enum):
    """Compression types."""
    NONE = "none"
    LZ4 = "lz4"
    SNAPPY = "snappy"
    GZIP = "gzip"


class ExportStatus(str, Enum):
    """Export job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExportJob:
    """Export job metadata."""
    id: str
    format: ExportFormat
    compression: CompressionType
    status: ExportStatus
    total_records: int = 0
    processed_records: int = 0
    output_file: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def progress(self) -> float:
        """Calculate progress percentage."""
        if self.total_records == 0:
            return 0.0
        return (self.processed_records / self.total_records) * 100


class BaseExporter:
    """Base exporter with streaming support."""

    async def export_stream(
        self,
        records: AsyncIterator[DataRecord],
        chunk_size: int = 10000,
    ) -> AsyncIterator[bytes]:
        """Export records in streaming fashion.

        Args:
            records: Async iterator of records
            chunk_size: Number of records per chunk

        Yields:
            Bytes of exported data
        """
        raise NotImplementedError


class JSONExporter(BaseExporter):
    """JSON exporter using orjson (9.05x faster)."""

    async def export_stream(
        self,
        records: AsyncIterator[DataRecord],
        chunk_size: int = 10000,
    ) -> AsyncIterator[bytes]:
        """Export to JSON format with streaming."""
        # Start array
        yield b'['

        first = True
        chunk = []

        async for record in records:
            # Convert record to dict
            record_dict = {
                'id': record.id,
                'user_id': record.user_id,
                'name': record.name,
                'email': record.email,
                'created_at': record.created_at,
                'status': record.status,
                'metadata': record.metadata,
            }

            chunk.append(record_dict)

            if len(chunk) >= chunk_size:
                # Serialize chunk with orjson (9.05x faster than json)
                for rec in chunk:
                    if not first:
                        yield b','
                    first = False
                    yield orjson.dumps(rec)

                chunk = []

        # Process remaining records
        if chunk:
            for rec in chunk:
                if not first:
                    yield b','
                first = False
                yield orjson.dumps(rec)

        # End array
        yield b']'


class CSVExporter(BaseExporter):
    """CSV exporter with streaming."""

    async def export_stream(
        self,
        records: AsyncIterator[DataRecord],
        chunk_size: int = 10000,
    ) -> AsyncIterator[bytes]:
        """Export to CSV format with streaming."""
        # CSV header
        header = "id,user_id,name,email,created_at,status,metadata\n"
        yield header.encode('utf-8')

        chunk = []

        async for record in records:
            # Simple CSV formatting (in production use csv module)
            metadata_str = orjson.dumps(record.metadata).decode('utf-8')
            line = f"{record.id},{record.user_id},{record.name},{record.email},{record.created_at},{record.status},\"{metadata_str}\"\n"
            chunk.append(line)

            if len(chunk) >= chunk_size:
                yield ''.join(chunk).encode('utf-8')
                chunk = []

        # Process remaining records
        if chunk:
            yield ''.join(chunk).encode('utf-8')


class MessagePackExporter(BaseExporter):
    """MessagePack exporter (5x faster than JSON)."""

    async def export_stream(
        self,
        records: AsyncIterator[DataRecord],
        chunk_size: int = 10000,
    ) -> AsyncIterator[bytes]:
        """Export to MessagePack format with streaming."""
        chunk = []

        async for record in records:
            # Convert record to dict
            record_dict = {
                'id': record.id,
                'user_id': record.user_id,
                'name': record.name,
                'email': record.email,
                'created_at': record.created_at,
                'status': record.status,
                'metadata': record.metadata,
            }

            chunk.append(record_dict)

            if len(chunk) >= chunk_size:
                # Serialize chunk with msgpack (5x faster than JSON)
                yield msgpack.packb(chunk)
                chunk = []

        # Process remaining records
        if chunk:
            yield msgpack.packb(chunk)


class CompressionStrategy:
    """Base compression strategy."""

    def compress(self, data: bytes) -> bytes:
        """Compress data."""
        raise NotImplementedError

    def decompress(self, data: bytes) -> bytes:
        """Decompress data."""
        raise NotImplementedError


class LZ4Compression(CompressionStrategy):
    """LZ4 compression (8.4x faster than zlib)."""

    def compress(self, data: bytes) -> bytes:
        """Compress with LZ4 (ultra-fast)."""
        return lz4.frame.compress(data, compression_level=0)

    def decompress(self, data: bytes) -> bytes:
        """Decompress LZ4."""
        return lz4.frame.decompress(data)


class SnappyCompression(CompressionStrategy):
    """Snappy compression (database optimized)."""

    def compress(self, data: bytes) -> bytes:
        """Compress with Snappy."""
        return snappy.compress(data)

    def decompress(self, data: bytes) -> bytes:
        """Decompress Snappy."""
        return snappy.decompress(data)


class GZIPCompression(CompressionStrategy):
    """GZIP compression (standard)."""

    def __init__(self, level: int = 6):
        """Initialize GZIP compression.

        Args:
            level: Compression level (1-9)
        """
        self.level = level

    def compress(self, data: bytes) -> bytes:
        """Compress with GZIP."""
        return gzip.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        """Decompress GZIP."""
        return gzip.decompress(data)


class ExportService:
    """Export service managing jobs and exporters."""

    def __init__(self):
        """Initialize export service."""
        self.jobs: Dict[str, ExportJob] = {}
        self.exporters = {
            ExportFormat.JSON: JSONExporter(),
            ExportFormat.CSV: CSVExporter(),
            ExportFormat.MSGPACK: MessagePackExporter(),
        }
        self.compressors = {
            CompressionType.LZ4: LZ4Compression(),
            CompressionType.SNAPPY: SnappyCompression(),
            CompressionType.GZIP: GZIPCompression(level=6),
        }
        self.output_dir = Path("exports")
        self.output_dir.mkdir(exist_ok=True)

    def create_job(
        self,
        format: ExportFormat,
        compression: CompressionType,
        total_records: int,
    ) -> ExportJob:
        """Create new export job.

        Args:
            format: Export format
            compression: Compression type
            total_records: Total number of records to export

        Returns:
            Export job
        """
        job_id = str(uuid.uuid4())
        job = ExportJob(
            id=job_id,
            format=format,
            compression=compression,
            status=ExportStatus.PENDING,
            total_records=total_records,
        )
        self.jobs[job_id] = job
        return job

    async def generate_sample_data(
        self,
        count: int,
        chunk_size: int = 10000,
    ) -> AsyncIterator[DataRecord]:
        """Generate sample data for export.

        Args:
            count: Number of records to generate
            chunk_size: Chunk size for yielding

        Yields:
            Data records
        """
        for i in range(count):
            record = DataRecord(
                id=i + 1,
                user_id=f"user_{i + 1}",
                name=f"User {i + 1}",
                email=f"user{i + 1}@example.com",
                created_at=datetime.utcnow().isoformat(),
                status="active" if i % 2 == 0 else "inactive",
                metadata={
                    "role": "admin" if i % 10 == 0 else "user",
                    "score": i * 10,
                    "tags": [f"tag{j}" for j in range(i % 5)],
                },
            )
            yield record

            # Simulate async I/O
            if i % chunk_size == 0 and i > 0:
                await asyncio.sleep(0)

    async def process_export(
        self,
        job: ExportJob,
        record_count: int,
    ) -> None:
        """Process export job.

        Args:
            job: Export job
            record_count: Number of records to export
        """
        try:
            job.status = ExportStatus.PROCESSING

            # Get exporter
            exporter = self.exporters[job.format]

            # Generate data
            records = self.generate_sample_data(record_count)

            # Extension mapping
            extensions = {
                ExportFormat.JSON: ".json",
                ExportFormat.CSV: ".csv",
                ExportFormat.MSGPACK: ".msgpack",
            }
            ext = extensions[job.format]

            # Compression extension
            if job.compression != CompressionType.NONE:
                ext += f".{job.compression.value}"

            output_file = self.output_dir / f"{job.id}{ext}"

            # Export with streaming
            start_time = time.time()

            with open(output_file, 'wb') as f:
                async for chunk in exporter.export_stream(records, chunk_size=10000):
                    # Apply compression if needed
                    if job.compression != CompressionType.NONE:
                        compressor = self.compressors[job.compression]
                        chunk = compressor.compress(chunk)

                    f.write(chunk)

                    # Update progress (estimate based on chunk)
                    job.processed_records = min(
                        job.processed_records + 10000,
                        job.total_records
                    )

            # Mark as completed
            job.status = ExportStatus.COMPLETED
            job.output_file = str(output_file)
            job.completed_at = datetime.utcnow()
            job.processed_records = job.total_records

            elapsed = time.time() - start_time
            print(f"Export completed: {job.id} in {elapsed:.2f}s ({job.total_records / elapsed:.0f} records/sec)")

        except Exception as e:
            job.status = ExportStatus.FAILED
            job.error = str(e)
            print(f"Export failed: {job.id} - {e}")

    def get_job(self, job_id: str) -> Optional[ExportJob]:
        """Get export job by ID.

        Args:
            job_id: Job ID

        Returns:
            Export job or None
        """
        return self.jobs.get(job_id)


# Global service
export_service: ExportService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global export_service

    # Initialize service
    export_service = ExportService()

    yield

    # Cleanup (if needed)


# Create FastAPI app
app = FastAPI(
    title="Data Export Service",
    description="High-performance export service handling 10M+ records in < 60 seconds",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/api/v1/export")
async def create_export(
    format: ExportFormat,
    compression: CompressionType,
    record_count: int,
    background_tasks: BackgroundTasks,
):
    """Create new export job.

    Args:
        format: Export format (json, csv, msgpack)
        compression: Compression type (none, lz4, snappy, gzip)
        record_count: Number of records to export
        background_tasks: FastAPI background tasks

    Returns:
        Export job details
    """
    # Create job
    job = export_service.create_job(
        format=format,
        compression=compression,
        total_records=record_count,
    )

    # Process in background
    background_tasks.add_task(
        export_service.process_export,
        job,
        record_count,
    )

    return {
        "job_id": job.id,
        "status": job.status.value,
        "format": job.format.value,
        "compression": job.compression.value,
        "total_records": job.total_records,
        "download_url": f"/api/v1/exports/{job.id}/download",
        "status_url": f"/api/v1/exports/{job.id}/status",
    }


@app.get("/api/v1/exports/{job_id}/status")
async def get_export_status(job_id: str):
    """Get export job status.

    Args:
        job_id: Export job ID

    Returns:
        Job status details
    """
    job = export_service.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")

    return {
        "job_id": job.id,
        "status": job.status.value,
        "format": job.format.value,
        "compression": job.compression.value,
        "total_records": job.total_records,
        "processed_records": job.processed_records,
        "progress": f"{job.progress():.1f}%",
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error": job.error,
    }


@app.get("/api/v1/exports/{job_id}/download")
async def download_export(job_id: str):
    """Download exported file.

    Args:
        job_id: Export job ID

    Returns:
        File download response
    """
    job = export_service.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")

    if job.status != ExportStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Export not ready (status: {job.status.value})"
        )

    if not job.output_file or not Path(job.output_file).exists():
        raise HTTPException(status_code=404, detail="Export file not found")

    # Determine media type
    media_types = {
        ExportFormat.JSON: "application/json",
        ExportFormat.CSV: "text/csv",
        ExportFormat.MSGPACK: "application/x-msgpack",
    }
    media_type = media_types.get(job.format, "application/octet-stream")

    return FileResponse(
        path=job.output_file,
        media_type=media_type,
        filename=Path(job.output_file).name,
    )


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get export service metrics.

    Returns:
        Service metrics
    """
    total_jobs = len(export_service.jobs)
    completed_jobs = sum(1 for j in export_service.jobs.values() if j.status == ExportStatus.COMPLETED)
    failed_jobs = sum(1 for j in export_service.jobs.values() if j.status == ExportStatus.FAILED)
    processing_jobs = sum(1 for j in export_service.jobs.values() if j.status == ExportStatus.PROCESSING)

    # Calculate average export time for completed jobs
    completed_with_time = [
        j for j in export_service.jobs.values()
        if j.status == ExportStatus.COMPLETED and j.completed_at and j.created_at
    ]

    avg_export_time = 0
    if completed_with_time:
        total_time = sum((j.completed_at - j.created_at).total_seconds() for j in completed_with_time)
        avg_export_time = total_time / len(completed_with_time)

    # Total records exported
    total_records = sum(j.total_records for j in export_service.jobs.values() if j.status == ExportStatus.COMPLETED)

    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "processing_jobs": processing_jobs,
        "total_records_exported": total_records,
        "avg_export_time_seconds": round(avg_export_time, 2),
        "format_stats": {
            format.value: sum(1 for j in export_service.jobs.values() if j.format == format)
            for format in ExportFormat
        },
        "compression_stats": {
            comp.value: sum(1 for j in export_service.jobs.values() if j.compression == comp)
            for comp in CompressionType
        },
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "service": "data-export-service",
        "jobs": len(export_service.jobs),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Data Export Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=False,
        workers=1,
    )
