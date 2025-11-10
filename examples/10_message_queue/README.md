# Example 10: Message Queue/Broker

High-throughput message queue with 500K+ msg/sec using pub/sub pattern.

## Targets
- Throughput: 500K+ msg/sec
- Latency: < 5ms P99
- Persistence: RingBuffer
- Partitions: 16 with ConsistentHashRing

## Features
- Pub/Sub pattern
- Consumer groups
- Message persistence
- Dead letter queue
- At-least-once delivery
