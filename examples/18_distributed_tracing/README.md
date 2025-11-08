# Example 18: Distributed Tracing System

Microservices observability with 1M+ spans/sec ingestion.

## Targets
- Span Ingestion: 1M+ spans/sec
- Trace Assembly: < 100ms
- Retention: 30 days
- Query Latency: < 50ms

## Features
- Span ingestion with RingBuffer (284K+ ops/sec)
- Trace assembly with LRUCache
- ConsistentHashRing sharding
- LZ4 compression for storage
- Real-time trace search
