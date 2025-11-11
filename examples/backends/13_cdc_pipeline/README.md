# Example 13: CDC Pipeline (Change Data Capture)

Database change streaming pipeline with 100K+ changes/sec.

## Targets
- Change capture: 100K+ changes/sec
- Latency: < 50ms end-to-end
- Exactly-once: BloomFilter deduplication
- Transformations: Schema evolution support

## Features
- Database change streaming
- Transform and route changes
- Schema evolution handling
- Exactly-once semantics with BloomFilter
- Multiple sinks (DB, queue, file)
