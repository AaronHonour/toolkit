# Example 9: Distributed Cache System

Multi-tier distributed caching with 1M+ req/sec throughput.

## 🎯 Performance Targets

- **Throughput**: 1M+ req/sec
- **Latency**: < 1ms P99 (L1 cache)
- **Hit Rate**: > 90% with LRU
- **Sharding**: ConsistentHashRing (773K+ ops/sec)
- **Capacity**: 10M+ keys

## Features

- Multi-tier caching (L1/L2)
- Consistent hashing for distribution
- LRU eviction (326K+ ops/sec)
- Read-through/Write-through patterns
- Negative caching with BloomFilter
- TTL support
