# Example 11: Distributed Rate Limiter

Token bucket rate limiting with 1M+ checks/sec.

## Targets
- Checks/sec: 1M+
- Algorithms: Token bucket, Sliding window
- Distributed: Multi-tenant with ConsistentHashRing
- Cache: LRUCache for counters (326K+ ops/sec)
