# File Processing Service

High-throughput file processing pipeline achieving **10K+ files/minute** with object pooling and zero-copy I/O.

## Overview

Production-ready file processing service demonstrating:
- **Pipeline Pattern** for staged processing
- **Worker Pool** for parallel execution
- **Object Pooling** (2.35x speedup from toolkit)
- **Buffer Pooling** for zero-copy I/O (46K ops/sec)
- **Async Processing** for max throughput

## Performance Targets

| Metric | Target | Tech Used |
|--------|--------|-----------|
| Throughput | 10K+ files/min | Worker pool, object pooling |
| Processing Latency | < 100ms/file | Pipeline stages |
| Memory Efficiency | 90% reduction | Object/buffer pooling |
| CPU Utilization | 80%+ | Multi-worker processing |

## Features

### Pipeline Stages
1. **Validation**: Check file format and size
2. **Preprocessing**: Normalize and clean data
3. **Processing**: Apply transformations
4. **Postprocessing**: Generate outputs
5. **Storage**: Save processed files

### File Types Supported
- Images (JPEG, PNG) - resize, optimize, thumbnail
- Documents (PDF, DOCX) - extract text, metadata
- Videos (MP4) - transcode, extract frames
- CSV/JSON - parse, transform, validate

## Architecture

```
┌──────────────┐
│ File Upload  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────┐
│      Pipeline Stages            │
│  ┌────────────────────────┐    │
│  │  1. Validation         │    │
│  └────────────────────────┘    │
│           │                     │
│           ▼                     │
│  ┌────────────────────────┐    │
│  │  2. Preprocessing      │    │
│  └────────────────────────┘    │
│           │                     │
│           ▼                     │
│  ┌────────────────────────┐    │
│  │  3. Processing         │    │
│  │  (Worker Pool)         │    │
│  └────────────────────────┘    │
│           │                     │
│           ▼                     │
│  ┌────────────────────────┐    │
│  │  4. Postprocessing     │    │
│  └────────────────────────┘    │
│           │                     │
│           ▼                     │
│  ┌────────────────────────┐    │
│  │  5. Storage            │    │
│  └────────────────────────┘    │
└─────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Processed    │
│ Files        │
└──────────────┘
```

## Usage

### Installation

```bash
cd examples/03_file_processing_service
pip install -r requirements.txt
```

### Start Service

```bash
python src/main.py
```

### Process Files

```bash
# Upload file for processing
curl -X POST http://localhost:8002/api/v1/files \
  -F "file=@document.pdf" \
  -F "operation=extract_text"

# Check processing status
curl http://localhost:8002/api/v1/files/{file_id}/status

# Download processed file
curl http://localhost:8002/api/v1/files/{file_id}/download
```

## Performance Optimizations

### 1. Object Pooling (2.35x Speedup)
```python
# Reuse processor objects
processor_pool = ObjectPool(
    factory=lambda: FileProcessor(),
    max_size=100,
    min_size=10
)
```

### 2. Buffer Pooling (46K ops/sec)
```python
# Zero-copy I/O with buffer reuse
buffer_pool = BufferPool(
    buffer_size=8192,
    max_buffers=1000
)
```

### 3. Worker Pool
```python
# Parallel processing with workers
workers = WorkerPool(
    num_workers=8,
    queue_size=1000
)
```

### 4. Pipeline Stages
```python
# Staged processing for efficiency
pipeline = Pipeline(
    stages=[
        ValidationStage(),
        PreprocessingStage(),
        ProcessingStage(),
        PostprocessingStage(),
        StorageStage(),
    ]
)
```

## Configuration

```yaml
# config/config.yaml
workers:
  num_workers: 8
  queue_size: 1000

object_pool:
  min_size: 10
  max_size: 100
  idle_timeout: 300

buffer_pool:
  buffer_size: 8192
  max_buffers: 1000

pipeline:
  max_concurrent: 100
  timeout: 300
```

## Monitoring

```bash
# Get service metrics
GET /api/v1/metrics

{
  "files_processed": 150000,
  "files_per_minute": 12500,
  "avg_processing_time_ms": 85,
  "worker_utilization": 0.82,
  "pool_statistics": {
    "object_pool": {
      "size": 45,
      "hits": 120000,
      "misses": 1200
    },
    "buffer_pool": {
      "size": 850,
      "reuse_rate": 0.95
    }
  }
}
```

## License

See toolkit root LICENSE file.
