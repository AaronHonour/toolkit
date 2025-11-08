# Example 8: Time-Series Database

High-performance time-series data storage and querying with 1M+ data points/sec.

## 🎯 Performance Targets

- **Ingestion**: 1M+ data points/sec
- **Query Latency**: < 10ms P99
- **Compression**: 10:1 ratio with LZ4
- **Retention**: Auto-downsampling
- **Range Queries**: 100K+ points/sec

## 📊 Features

- High-speed ingestion with BufferPool
- LZ4 compression (8.4x faster)
- Automatic downsampling and rollups
- Efficient range queries
- Windowed aggregations
- Tag-based indexing with ConsistentHashRing
