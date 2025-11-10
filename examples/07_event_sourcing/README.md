# Example 7: Event Sourcing + CQRS System

Complete event-driven architecture with event store, CQRS, and saga pattern.

## 🎯 Performance Targets

- **Write Throughput**: 500K+ events/sec
- **Read Throughput**: 1M+ queries/sec
- **Event Store**: 10M+ events capacity
- **Projection Update**: < 10ms lag
- **Replay Speed**: 2M+ events/sec

## 🏗️ Architecture

```
Commands                Events                 Queries
   │                      │                       │
   ▼                      ▼                       ▼
┌──────────┐         ┌──────────┐         ┌──────────┐
│ Command  │────────>│  Event   │────────>│  Read    │
│ Handler  │         │  Store   │         │  Model   │
└──────────┘         └──────────┘         └──────────┘
                          │
                          ▼
                    ┌──────────┐
                    │Projections│
                    └──────────┘
```

## 🔧 Features

- Event Store with complete audit trail
- CQRS (separate read/write models)
- Multiple projections from same events
- Event replay and time travel
- Saga pattern for distributed workflows
- Snapshot optimization
- Idempotent event handling

## 📊 Toolkit Usage

- **RingBuffer**: Event streaming (284K+ ops/sec)
- **LRUCache**: Projection caching (326K+ ops/sec)
- **BloomFilter**: Idempotency (131K+ ops/sec)
- **fast_hash**: Aggregate IDs (886K+ ops/sec)
