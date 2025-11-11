# Frontend Applications: Architectural Concepts & Trade-offs

**Purpose:** This document explains the business and technical concepts behind each application, helping developers understand WHEN and WHY to use each architectural pattern.

---

## Overview: Composable Architecture Philosophy

Each application demonstrates a **specific architectural pattern** or **data structure** optimized for particular use cases. The key insight: **there is no one-size-fits-all solution** - different problems require different trade-offs.

### Core Principle
**Composability over Monoliths** - Mix and match patterns based on your specific requirements rather than forcing everything into a single architectural style.

---

## Pattern Categories

### 🔵 Data Access Patterns (Apps 01, 04, 05)
*When and how to retrieve data efficiently*

### 🟢 Real-time Processing (Apps 02, 06, 07, 08, 12)
*Handling streaming data and events*

### 🟡 Scalability & Reliability (Apps 03, 09, 10, 11, 13)
*Managing load and system coordination*

### 🟣 Advanced Features (Apps 14, 15, 16, 17, 18, 19)
*Specialized algorithms and structures*

---

## App 01: REST API Client (LRU Cache Pattern)

### Business Concept
**E-commerce inventory management** - Fast product lookups with caching to reduce database load and API latency.

### Technical Pattern
**LRU (Least Recently Used) Cache** - Keep frequently accessed data in memory, evict stale data.

### Key Metrics
- **Performance:** 445K RPS, P99 < 100ms
- **Cache Hit Rate:** ~85% (configurable)
- **Memory:** O(n) where n = cache size

### When to Use
✅ **Use When:**
- Read-heavy workloads (reads >> writes)
- Data has natural "hotspots" (80/20 rule applies)
- Acceptable to serve slightly stale data (seconds old)
- Database is bottleneck

❌ **Don't Use When:**
- Write-heavy workloads (cache thrashing)
- Data must be real-time (no staleness tolerance)
- Working set > available memory
- Reads are uniformly distributed (no hotspots)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Speed** | 50-100x faster than DB | Cache misses are slower |
| **Cost** | Reduces DB load = lower costs | Memory costs for cache |
| **Complexity** | Simple to implement | Cache invalidation is hard |
| **Consistency** | High throughput | Eventual consistency |

### Business Impact
- **Cost Savings:** Reduce database costs by 60-80% (fewer queries)
- **User Experience:** Sub-100ms response times
- **Scalability:** Handle 10x more traffic with same DB

### Real-world Example
**Amazon Product Catalog** - Product details cached aggressively since they change infrequently but are read millions of times.

### Decision Criteria
```
IF (read_ratio > 80% AND data_staleness_acceptable > 1s)
  THEN use_lru_cache = TRUE
ELSE
  consider_other_pattern
```

---

## App 02: Real-time Analytics (Event Stream Processing)

### Business Concept
**Live analytics dashboard** - Process 1M+ events/second for real-time insights (user behavior, system metrics, etc.)

### Technical Pattern
**Stream Processing** - Process events as they arrive, maintain running aggregations.

### Key Metrics
- **Throughput:** 1M+ events/second
- **Latency:** <100ms event-to-dashboard
- **Storage:** In-memory + time-windowed

### When to Use
✅ **Use When:**
- Need real-time (sub-second) insights
- Data has time-decay (recent more important)
- High event volume (thousands/sec+)
- Continuous queries on live data

❌ **Don't Use When:**
- Batch processing is acceptable (hourly/daily)
- Historical analysis more important than real-time
- Low event volume (<100/sec)
- Complex joins across time windows

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Speed** | Real-time insights | Higher infrastructure cost |
| **Freshness** | Always current | Can't change history |
| **Scalability** | Horizontal scaling | Complex windowing logic |
| **Reliability** | At-least-once delivery | Exactly-once is hard |

### Business Impact
- **Competitive Advantage:** React to trends in real-time
- **Operational:** Detect issues immediately
- **Cost:** 2-3x more expensive than batch

### Real-world Examples
- **Uber:** Real-time driver/rider matching
- **Netflix:** Live viewing metrics for content recommendations
- **Datadog:** System monitoring and alerting

### Decision Criteria
```
IF (latency_requirement < 1s AND event_volume > 1000/sec)
  THEN use_stream_processing = TRUE
ELSE IF (can_wait_hours)
  THEN use_batch_processing = TRUE (cheaper)
```

---

## App 03: File Processing Pipeline (Worker Pool Pattern)

### Business Concept
**High-throughput file processing** - Process 10K+ files/minute (images, videos, documents) with parallel workers.

### Technical Pattern
**Worker Pool** - Distribute CPU-intensive tasks across multiple workers, queue for load balancing.

### Key Metrics
- **Throughput:** 10K+ files/minute
- **Worker Utilization:** 80-95%
- **Avg Processing Time:** <100ms per file

### When to Use
✅ **Use When:**
- CPU-bound tasks (transcoding, image processing, ML)
- Tasks are independent (no dependencies)
- Varying task duration (needs queue buffering)
- Need to limit concurrency

❌ **Don't Use When:**
- IO-bound tasks (use async instead)
- Tasks have dependencies (use DAG)
- Need strict ordering
- Single-threaded is fast enough

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Throughput** | Linear scaling with cores | Worker overhead |
| **Cost** | Maximize hardware utilization | Complex error handling |
| **Latency** | Queue smooths spikes | Queue wait time |
| **Reliability** | Retry failed tasks | Needs monitoring |

### Business Impact
- **Efficiency:** Process hours of work in minutes
- **Cost:** Use cheaper compute (vs serverless)
- **Reliability:** Automatic retries, graceful degradation

### Real-world Examples
- **Figma:** Image export and rendering
- **YouTube:** Video transcoding pipeline
- **Dropbox:** File preview generation

### Decision Criteria
```
IF (task_is_cpu_bound AND tasks_are_independent)
  THEN use_worker_pool = TRUE
  optimal_workers = cpu_cores * (1 + wait_time/compute_time)
```

---

## App 04: API Gateway (Service Routing Pattern)

### Business Concept
**Microservices entry point** - Route 50K+ req/sec to appropriate backend services, handle auth, rate limiting, circuit breaking.

### Technical Pattern
**Gateway/Proxy** - Single entry point for multiple services with cross-cutting concerns.

### Key Metrics
- **Throughput:** 50K+ requests/second
- **Latency Overhead:** +2-5ms
- **Services:** Can route to dozens/hundreds

### When to Use
✅ **Use When:**
- Multiple backend services (microservices)
- Need centralized auth, logging, monitoring
- API versioning and backward compatibility
- Rate limiting and circuit breaking

❌ **Don't Use When:**
- Monolithic architecture (adds unnecessary hop)
- Ultra-low latency required (every hop costs)
- Services are internal-only (no external API)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Simplicity** | Single client endpoint | Gateway is SPOF |
| **Security** | Centralized auth | Gateway complexity |
| **Monitoring** | Unified logging | Added latency |
| **Evolution** | Service changes hidden | Versioning complexity |

### Business Impact
- **Developer Productivity:** Services evolve independently
- **Security:** Single auth/security layer
- **Cost:** Prevent cascading failures (circuit breaker)

### Real-world Examples
- **Netflix Zuul:** Gateway for 1000+ microservices
- **Kong/AWS API Gateway:** Commercial solutions
- **Stripe API:** Versioned API with backward compatibility

### Decision Criteria
```
IF (num_services > 5 AND need_centralized_concerns)
  THEN use_api_gateway = TRUE
ELSE IF (monolith OR ultra_low_latency_required)
  THEN direct_connection = TRUE
```

---

## App 05: Data Export Service (Serialization Pattern)

### Business Concept
**Bulk data export** - Export 10M records in 60 seconds with compression, supporting multiple formats (CSV, JSON, Parquet).

### Technical Pattern
**Fast Serialization + Compression** - Optimize for sequential writes, use columnar formats, streaming compression.

### Key Metrics
- **Speed:** 10M records/60s (166K/sec)
- **Compression:** LZ4 8.4x faster than zlib
- **Formats:** CSV, JSON, Parquet, Avro

### When to Use
✅ **Use When:**
- Bulk data transfers (analytics, backups)
- Batch ETL pipelines
- Data warehouse ingestion
- Compliance/audit exports

❌ **Don't Use When:**
- Real-time data needed
- Small result sets (<1000 rows)
- Interactive queries (use streaming)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Speed** | Columnar formats 10x faster | Upfront serialization cost |
| **Storage** | Compression saves 70-90% | CPU for compression |
| **Compatibility** | Multiple formats | Format-specific logic |
| **Memory** | Streaming avoids OOM | Slower than in-memory |

### Business Impact
- **Cost Savings:** 80% storage reduction with compression
- **Analytics:** Fast data warehouse loading
- **Compliance:** Efficient audit trail exports

### Real-world Examples
- **Snowflake:** Parquet-based data loading
- **BigQuery:** Columnar storage for analytics
- **Stripe:** Daily transaction exports for accounting

### Decision Criteria
```
IF (export_size > 100K rows AND not_real_time)
  THEN use_bulk_export = TRUE
  format = parquet IF analytics ELSE csv IF human_readable
  compression = lz4 IF speed_priority ELSE zlib IF size_priority
```

---

## App 06: Kappa Architecture (Stream-only Pattern)

### Business Concept
**Simplified real-time processing** - Process all data as streams, eliminate batch layer complexity.

### Technical Pattern
**Kappa Architecture** - Everything is a stream, reprocessing via replay, single code path.

### Key Metrics
- **Throughput:** 500K+ events/second
- **Reprocessing:** Replay from offset
- **Complexity:** Simpler than Lambda (no batch layer)

### When to Use
✅ **Use When:**
- All data arrives as streams
- Reprocessing = replay from beginning
- Team expertise in stream processing
- Don't need complex batch analytics

❌ **Don't Use When:**
- Need complex batch joins
- Historical reprocessing is expensive
- Data arrives in batches
- Team lacks streaming expertise

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Simplicity** | Single code path | Stream-only mindset |
| **Maintenance** | One system to manage | Replay can be slow |
| **Speed** | Real-time by default | Complex windowing |
| **Reprocessing** | Replay from offset | Storage of full history |

### Business Impact
- **Reduced Complexity:** No batch/stream divergence
- **Faster Development:** Single code path
- **Lower Costs:** Fewer systems to maintain

### Real-world Examples
- **LinkedIn:** Kafka-based processing
- **Uber:** Trip data processing

### Decision Criteria
```
IF (data_is_streams AND reprocessing_via_replay_ok)
  THEN use_kappa = TRUE
ELSE IF (need_batch_analytics)
  THEN use_lambda = TRUE (see App 12)
```

---

## App 07: Event Sourcing (Audit Trail Pattern)

### Business Concept
**Complete audit history** - Store all changes as events, reconstruct state at any point in time, perfect for financial systems.

### Technical Pattern
**Event Sourcing + CQRS** - Append-only event log, separate read/write models, projections for queries.

### Key Metrics
- **Write Speed:** 500K+ events/second
- **Storage:** Linear growth with events
- **Audit:** Complete history, never lose data

### When to Use
✅ **Use When:**
- Need complete audit trail (compliance)
- Time-travel queries (state at any point)
- Complex business workflows
- Undo/replay capabilities

❌ **Don't Use When:**
- Simple CRUD (overkill)
- Storage costs are concern
- Team unfamiliar with pattern
- Don't need history

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Audit** | Perfect compliance | Storage grows forever |
| **Debug** | Replay production bugs | Complexity |
| **Flexibility** | Change projections | Eventual consistency |
| **Reliability** | Never lose data | Snapshots for performance |

### Business Impact
- **Compliance:** Perfect audit for regulations
- **Debug:** Reproduce any historical state
- **Cost:** 10x more storage than current state

### Real-world Examples
- **Banking:** Transaction ledgers
- **Healthcare:** Patient record changes
- **Insurance:** Policy modification history

### Decision Criteria
```
IF (need_audit_trail OR time_travel OR compliance_critical)
  THEN use_event_sourcing = TRUE
  implement_cqrs = TRUE (separate read/write)
  storage_cost = 10x_current_state
```

---

## App 08: TimeSeries Database (Time-ordered Data Pattern)

### Business Concept
**Metrics and monitoring** - Store 1M+ metrics/second with efficient time-range queries, downsampling, and retention policies.

### Technical Pattern
**TimeSeries DB** - Optimized for time-ordered data, compression, aggregations.

### Key Metrics
- **Ingestion:** 1M+ points/second
- **Compression:** 10-20x vs general DB
- **Query:** Time-range queries in milliseconds

### When to Use
✅ **Use When:**
- Monitoring/metrics (CPU, memory, etc.)
- IoT sensor data
- Financial tick data
- Time is primary query dimension

❌ **Don't Use When:**
- Time not primary dimension
- Need complex joins
- Low data volume (<1K points/sec)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Compression** | 10-20x space savings | Write amplification |
| **Query Speed** | Optimized for time ranges | Poor for other queries |
| **Retention** | Auto-downsampling | Lose precision over time |
| **Ingestion** | Massive throughput | Eventual consistency |

### Business Impact
- **Cost:** 90% storage reduction
- **Monitoring:** Fast dashboards
- **Scale:** Handle millions of metrics

### Real-world Examples
- **Prometheus/Grafana:** Monitoring stack
- **InfluxDB/TimescaleDB:** Purpose-built TSDBs
- **Datadog:** SaaS monitoring

### Decision Criteria
```
IF (data_is_time_series AND volume > 10K_points/sec)
  THEN use_tsdb = TRUE
  retention_policy = full_resolution_7d + downsampled_90d + aggregated_1y
```

---

## App 09: Distributed Cache (Multi-tier Caching Pattern)

### Business Concept
**Reduce latency and load** - Multi-level cache (L1: local, L2: distributed) handling 1M+ req/sec.

### Technical Pattern
**Cache Hierarchy** - Local cache (fast, small) + distributed cache (shared, larger).

### Key Metrics
- **Throughput:** 1M+ requests/second
- **L1 Hit Rate:** ~70-80%
- **L2 Hit Rate:** ~15-20%
- **Total Hit Rate:** ~90-95%

### When to Use
✅ **Use When:**
- Hot data accessed repeatedly
- Read >> writes
- Acceptable staleness
- Multiple servers sharing data

❌ **Don't Use When:**
- Data must be fresh
- Working set fits in L1
- Write-heavy workload

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Speed** | L1 microseconds, L2 milliseconds | Complexity |
| **Scalability** | Horizontal scaling | Cache coherence |
| **Cost** | Reduce DB load 90%+ | Memory costs |
| **Consistency** | High throughput | Eventual consistency |

### Business Impact
- **Cost:** 80% infrastructure savings
- **Latency:** 100x faster than DB
- **Reliability:** Survive DB outages briefly

### Real-world Examples
- **Facebook:** TAO (multi-tier graph cache)
- **Twitter:** Manhattan (distributed KV store)
- **Reddit:** L1 application cache + L2 Redis

### Decision Criteria
```
cache_strategy:
  IF (data_locality_high) THEN use_l1_only
  ELSE IF (shared_across_servers) THEN use_l1_plus_l2
  ELSE IF (low_latency_critical) THEN use_l1_plus_l2_plus_cdn

ttl_strategy:
  volatile_data: 10-60s
  semi_static: 5-15min
  static_content: 24h+
```

---

## App 10: Message Queue (Async Communication Pattern)

### Business Concept
**Decouple services** - Process 500K+ messages/second asynchronously, buffer spikes, guarantee delivery.

### Technical Pattern
**Message Queue** - Producer/consumer decoupling, at-least-once delivery, dead letter queues.

### Key Metrics
- **Throughput:** 500K+ messages/second
- **Latency:** Milliseconds (not real-time)
- **Reliability:** Persistent, retry logic

### When to Use
✅ **Use When:**
- Tasks can be async (email, notifications)
- Microservices communication
- Load leveling (buffer spikes)
- Need retry logic

❌ **Don't Use When:**
- Need synchronous response
- Ultra-low latency (<10ms)
- Simple request/response
- Ordering critical (use Kafka)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Decoupling** | Services independent | Complexity |
| **Reliability** | Retry + DLQ | Duplicates possible |
| **Scalability** | Buffer traffic spikes | Added latency |
| **Debug** | Async = harder to trace | Monitoring needed |

### Business Impact
- **Resilience:** Services don't fail together
- **Scalability:** Handle 10x traffic spikes
- **Cost:** Process async = smaller instances

### Real-world Examples
- **AWS SQS:** Managed queue service
- **RabbitMQ:** Open source broker
- **Slack:** Message delivery guarantees

### Decision Criteria
```
IF (task_can_be_async AND need_reliability)
  THEN use_message_queue = TRUE
  delivery_guarantee = at_least_once (default)
  dlq = TRUE (for poison messages)

ELSE IF (need_ordering)
  THEN use_kafka = TRUE (ordered partitions)
```

---

---

## App 11: Rate Limiter (Resource Protection Pattern)

### Business Concept
**Protect resources** - Prevent abuse, ensure fair access, control costs with token bucket algorithm.

### Technical Pattern
**Token Bucket** - Tokens refill at fixed rate, requests consume tokens, smooth bursts while enforcing limits.

### Key Metrics
- **Capacity:** Configurable bucket size
- **Refill Rate:** Tokens/second
- **Overhead:** <1ms per check

### When to Use
✅ **Use When:**
- Protect expensive resources (DB, API)
- Prevent abuse/DOS
- Enforce SLA tiers (free vs paid)
- Cost control (API usage limits)

❌ **Don't Use When:**
- Unlimited resources
- Single user systems
- Latency ultra-critical (<1ms)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Protection** | Prevents overload | Rejects valid requests |
| **Fairness** | Equal access | Complex to tune |
| **Cost Control** | Budget enforcement | User frustration if too strict |
| **Simplicity** | Easy to implement | Per-user state required |

### Business Impact
- **Cost Savings:** Prevent runaway usage
- **Stability:** System survives traffic spikes
- **Monetization:** Tiered pricing (rate limits)

### Real-world Examples
- **Stripe:** API rate limiting per tier
- **Twitter:** Tweet rate limits
- **AWS:** API request quotas

### Decision Criteria
```
token_bucket_vs_alternatives:
  IF (need_smooth_bursts) THEN token_bucket
  ELSE IF (strict_rps_limit) THEN sliding_window
  ELSE IF (simple_daily_quota) THEN counter

capacity = expected_burst_size
refill_rate = sustained_rps_limit
```

---

## App 12: Lambda Architecture (Batch + Stream Pattern)

### Business Concept
**Best of both worlds** - Combine batch (accurate, complex) with streaming (fast, simple) for comprehensive analytics.

### Technical Pattern
**Lambda Architecture** - Batch layer (historical), speed layer (real-time), serving layer (queries).

### Key Metrics
- **Batch:** High accuracy, complex joins
- **Speed:** Real-time, approximate results
- **Latency:** Milliseconds (speed) + hours (batch)

### When to Use
✅ **Use When:**
- Need both real-time AND complex analytics
- Can tolerate batch delay for accuracy
- Different SLAs for different queries
- Team has expertise in both batch & stream

❌ **Don't Use When:**
- Can use Kappa (stream only)
- Don't need historical reprocessing
- Team lacks batch OR stream expertise
- Simplicity more valuable than features

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Completeness** | Batch + Stream coverage | Maintain 2 code paths |
| **Accuracy** | Batch provides exact results | Complexity |
| **Speed** | Real-time via speed layer | Eventual consistency |
| **Reprocessing** | Batch can recompute | Dual infrastructure |

### Business Impact
- **Analytics:** Real-time dashboards + accurate reports
- **Cost:** 2x infrastructure (batch + stream)
- **Complexity:** 2 systems to maintain

### Real-world Examples
- **Netflix:** Viewing analytics
- **LinkedIn:** User activity processing

### Decision Criteria
```
IF (need_real_time AND need_complex_batch_analytics)
  THEN lambda_architecture = TRUE
  batch_delay_acceptable = TRUE
  cost = 2x_single_system

ELSE IF (stream_only_sufficient)
  THEN kappa_architecture = TRUE (simpler)
```

---

## App 13: Change Data Capture (Data Sync Pattern)

### Business Concept
**Keep systems in sync** - Capture database changes in real-time, propagate to downstream systems without custom triggers.

### Technical Pattern
**CDC (Change Data Capture)** - Read database transaction log, emit change events, consumers react.

### Key Metrics
- **Latency:** <100ms from DB write to event
- **Throughput:** 500K+ changes/second
- **Deduplication:** 90%+ reduction

### When to Use
✅ **Use When:**
- Multiple systems need same data
- Microservices need to stay in sync
- Build event-driven architecture
- Avoid coupling via DB sharing

❌ **Don't Use When:**
- Single system (no sync needed)
- Batch sync acceptable (ETL)
- Source DB doesn't support CDC

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Coupling** | Services decoupled | Eventual consistency |
| **Real-time** | Immediate propagation | CDC infrastructure |
| **Accuracy** | Captures all changes | Requires CDC tooling |
| **Flexibility** | Transform in consumers | Schema evolution complexity |

### Business Impact
- **Agility:** Add new consumers easily
- **Reliability:** No missed updates
- **Cost:** CDC infrastructure + storage

### Real-world Examples
- **Debezium:** Open-source CDC
- **Netflix:** Service data synchronization
- **Uber:** Database replication

### Decision Criteria
```
IF (multiple_systems_need_db_data AND real_time_required)
  THEN cdc = TRUE
  tool = debezium OR aws_dms

ELSE IF (batch_acceptable)
  THEN etl_jobs = TRUE (simpler, cheaper)
```

---

## App 14: Recommendation Engine (ML in Production Pattern)

### Business Concept
**Personalization** - Real-time product/content recommendations using ML models with sub-100ms latency.

### Technical Pattern
**ML Inference** - Pre-trained models, feature engineering, real-time scoring, A/B testing.

### Key Metrics
- **Latency:** P99 < 100ms
- **Accuracy:** Precision/recall metrics
- **Throughput:** 10K+ predictions/second

### When to Use
✅ **Use When:**
- Have training data (user behavior)
- Recommendations add value
- Can measure impact (CTR, revenue)
- Low latency required

❌ **Don't Use When:**
- Insufficient training data
- Business logic sufficient (rules)
- Can't measure improvement
- Latency not critical (batch OK)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Personalization** | Better user experience | ML infrastructure |
| **Revenue** | Higher conversion rates | Model training costs |
| **Complexity** | vs simple rules | Feature engineering |
| **Maintenance** | Models need retraining | Data drift monitoring |

### Business Impact
- **Revenue:** 10-30% increase in conversion
- **Engagement:** Users stay longer
- **Cost:** ML infrastructure + data scientists

### Real-world Examples
- **Amazon:** Product recommendations (35% of revenue)
- **Netflix:** Content recommendations
- **Spotify:** Discover Weekly

### Decision Criteria
```
IF (have_training_data AND can_measure_roi)
  THEN ml_recommendations = TRUE
  start_with = collaborative_filtering (simple)
  scale_to = deep_learning (if data permits)

ELSE IF (cold_start_problem)
  THEN content_based = TRUE (use item features)
```

---

## App 15: Full-text Search (Search Index Pattern)

### Business Concept
**Fast text search** - Search millions of documents in milliseconds with relevance ranking, facets, and highlighting.

### Technical Pattern
**Inverted Index** - Pre-compute term-to-document mappings, rank by relevance (TF-IDF, BM25).

### Key Metrics
- **Index Size:** 10-30% of source data
- **Query Speed:** <50ms for millions of docs
- **Indexing:** Real-time or batch

### When to Use
✅ **Use When:**
- Text search across large corpus
- Need ranking (not just matching)
- Faceted search (filters)
- Autocomplete/suggestions

❌ **Don't Use When:**
- Simple exact matches (use DB)
- <10K documents (scan is fine)
- Don't need relevance ranking

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Speed** | 1000x faster than DB scan | Index storage |
| **Relevance** | Sophisticated ranking | Tuning required |
| **Features** | Facets, highlighting, etc | Complexity |
| **Freshness** | Near real-time updates | Reindexing cost |

### Business Impact
- **User Experience:** Find things fast
- **Conversion:** Better search = more sales
- **Cost:** Dedicated search infrastructure

### Real-world Examples
- **Elasticsearch:** Most popular search engine
- **Amazon:** Product search
- **Google:** Well... Google

### Decision Criteria
```
IF (corpus_size > 10K AND need_relevance_ranking)
  THEN full_text_search = TRUE
  tool = elasticsearch OR solr OR typesense

ELSE IF (simple_exact_match)
  THEN db_like_query = TRUE
```

---

## App 16: Feature Store (ML Feature Management Pattern)

### Business Concept
**Centralize ML features** - Shared feature repository for training and serving, ensuring consistency and reusability.

### Technical Pattern
**Feature Store** - Precompute features, low-latency serving, point-in-time correct training data.

### Key Metrics
- **Latency:** <10ms feature lookup
- **Features:** Thousands of features
- **Reuse:** Share across models

### When to Use
✅ **Use When:**
- Multiple ML models
- Feature engineering is complex
- Train-serve skew is problem
- Team > 1 data scientist

❌ **Don't Use When:**
- Single model
- Simple features (no reuse)
- Feature computation is trivial

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Consistency** | Training = Serving | Infrastructure |
| **Reuse** | DRY for features | Migration effort |
| **Speed** | Precomputed features | Storage costs |
| **Governance** | Feature discovery | Additional system |

### Business Impact
- **ML Velocity:** 3-5x faster model development
- **Quality:** Eliminates train-serve skew
- **Cost:** Feature store infrastructure

### Real-world Examples
- **Uber Michelangelo:** Feature store at scale
- **Netflix:** Feature engineering platform
- **Feast:** Open-source feature store

### Decision Criteria
```
IF (num_ml_models > 3 AND feature_reuse_opportunities)
  THEN feature_store = TRUE
  start_with = feast (open source)

compute_strategy:
  real_time_features: compute_on_read
  batch_features: precompute_daily
```

---

## App 17: OLAP Cube (Pre-aggregation Pattern)

### Business Concept
**Fast analytics** - Pre-aggregate data across dimensions for sub-second ad-hoc queries on billions of rows.

### Technical Pattern
**OLAP Cube** - Materialize aggregations, columnar storage, drill-down/roll-up.

### Key Metrics
- **Query Speed:** <100ms on 1B+ rows
- **Dimensions:** 100+ dimensions
- **Refresh:** Real-time or periodic

### When to Use
✅ **Use When:**
- Analytical queries (GROUP BY heavy)
- Known dimensions (product, region, time)
- Same queries repeatedly
- Dashboard/BI workloads

❌ **Don't Use When:**
- Ad-hoc queries on random dimensions
- Data changes frequently
- Real-time updates critical

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Speed** | 100-1000x faster | Storage explosion |
| **Concurrency** | Many users simultaneously | Pre-aggregation time |
| **Flexibility** | vs raw queries | Dimension limits |
| **Freshness** | Materialization lag | Incremental updates |

### Business Impact
- **BI Performance:** Instant dashboards
- **Cost:** 10-50x storage for pre-aggregations
- **User Satisfaction:** No waiting

### Real-world Examples
- **Druid:** Real-time OLAP
- **ClickHouse:** Fast analytics
- **Google BigQuery:** Columnar analytics

### Decision Criteria
```
IF (analytical_workload AND known_dimensions)
  THEN olap = TRUE
  storage_multiplier = 10-50x (worst case)
  refresh_strategy = real_time OR hourly OR daily

ELSE IF (ad_hoc_queries)
  THEN columnar_db = TRUE (not pre-aggregated)
```

---

## App 18: Distributed Tracing (Observability Pattern)

### Business Concept
**Debug microservices** - Track requests across 10+ services, visualize latency, identify bottlenecks.

### Technical Pattern
**Distributed Tracing** - Trace ID propagation, span collection, flame graphs.

### Key Metrics
- **Overhead:** <5% latency impact
- **Sampling:** 1-100% of requests
- **Retention:** Days to weeks

### When to Use
✅ **Use When:**
- Microservices architecture
- Cross-service debugging needed
- Performance optimization
- Complex distributed systems

❌ **Don't Use When:**
- Monolith (simple logs suffice)
- <3 services
- No performance issues

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Debugging** | Find issues across services | Instrumentation required |
| **Performance** | Identify bottlenecks | Storage for traces |
| **Understanding** | Visualize request flow | <5% overhead |
| **Monitoring** | Latency percentiles | Sampling strategy needed |

### Business Impact
- **MTTR:** 5-10x faster debugging
- **Performance:** Find optimization opportunities
- **Cost:** Tracing infrastructure

### Real-world Examples
- **Jaeger/Zipkin:** Open-source tracing
- **Datadog APM:** Commercial solution
- **AWS X-Ray:** Managed tracing

### Decision Criteria
```
IF (num_services > 3 AND debugging_is_hard)
  THEN distributed_tracing = TRUE
  sampling_rate = 1% (production) OR 100% (development)

ELSE IF (monolith)
  THEN structured_logging = TRUE (simpler)
```

---

## App 19: Probabilistic Structures (Approximation Pattern)

### Business Concept
**Trade accuracy for speed/memory** - Approximate algorithms (Bloom filters, HyperLogLog) for massive scale.

### Technical Pattern
**Probabilistic Data Structures** - Accept false positives for 10-1000x memory reduction.

### Key Metrics
- **Memory:** 1/100 to 1/1000 of exact
- **Speed:** 10-100x faster
- **Accuracy:** 99-99.9% (configurable)

### When to Use
✅ **Use When:**
- Exact not required (deduplication, caching)
- Memory/CPU constrained
- Scale is massive (billions of items)
- False positives acceptable

❌ **Don't Use When:**
- Need exact results
- Small data (<1M items)
- False positives unacceptable (financial)

### Trade-offs

| Dimension | Benefit | Cost |
|-----------|---------|------|
| **Memory** | 1/1000 of exact | False positives |
| **Speed** | 10-100x faster | Approximate |
| **Scale** | Billions of items | Tuning required |
| **Simplicity** | Elegant algorithms | Counterintuitive |

### Business Impact
- **Scale:** Handle data that wouldn't fit in memory
- **Cost:** 99% memory reduction
- **Accuracy:** 0.1-1% error rate

### Real-world Examples
- **Google:** Bloom filters for safe browsing
- **Redis:** HyperLogLog for cardinality
- **Akamai:** Count-Min Sketch for top-K

### Structures Demonstrated

| Structure | Use Case | Error | Memory |
|-----------|----------|-------|--------|
| **Bloom Filter** | "Is X in set?" | False positives | 10 bits/item |
| **HyperLogLog** | Cardinality (COUNT DISTINCT) | ~2% error | 1.5KB fixed |
| **Count-Min Sketch** | Frequency estimation | Over-counting | Configurable |

### Decision Criteria
```
bloom_filter:
  IF (membership_test AND false_positives_ok)
    space_savings = 90-99%
    use_case = cache_check, deduplication

hyperloglog:
  IF (count_distinct AND approximate_ok)
    fixed_size = 1.5KB (any cardinality!)
    use_case = unique_visitors, distinct_events

count_min_sketch:
  IF (top_k_items AND approximate_ok)
    memory = width * depth * 4 bytes
    use_case = heavy_hitters, trending_topics
```

---

## Architecture Decision Matrix

### Quick Reference Guide

| Your Need | Recommended Pattern | App # |
|-----------|---------------------|-------|
| Fast API responses | LRU Cache | 01 |
| Real-time analytics | Stream Processing | 02 |
| Process many files | Worker Pool | 03 |
| Multiple microservices | API Gateway | 04 |
| Export large datasets | Bulk Export | 05 |
| Simplify streaming | Kappa Architecture | 06 |
| Perfect audit trail | Event Sourcing | 07 |
| Time-series metrics | TimeSeries DB | 08 |
| Multi-tier caching | Distributed Cache | 09 |
| Async task processing | Message Queue | 10 |
| Protect resources | Rate Limiter | 11 |
| Batch + Stream | Lambda Architecture | 12 |
| Sync multiple DBs | Change Data Capture | 13 |
| Personalization | ML Recommendations | 14 |
| Search documents | Full-text Search | 15 |
| Share ML features | Feature Store | 16 |
| Fast analytics | OLAP Cube | 17 |
| Debug microservices | Distributed Tracing | 18 |
| Massive scale | Probabilistic Structures | 19 |

---

## Cost & Performance Comparison

### Infrastructure Cost (Relative to simple REST API = 1x)

| Pattern | Infra Cost | Why |
|---------|------------|-----|
| REST + Cache | 1.2x | +Memory for cache |
| Stream Processing | 2-3x | Always-on stream processors |
| Worker Pool | 1.5x | Worker instances |
| API Gateway | 1.1x | Gateway overhead minimal |
| Bulk Export | 1x | Batch, no always-on |
| Kappa | 2x | Stream infrastructure |
| Event Sourcing | 2-3x | Event store + projections |
| TimeSeries DB | 1.5x | Specialized DB |
| Distributed Cache | 2x | Multi-tier cache |
| Message Queue | 1.3x | Queue infrastructure |
| Rate Limiter | 1.1x | State storage minimal |
| Lambda | 3-4x | Batch + Stream layers |
| CDC | 1.5x | CDC tooling + queue |
| ML Recommendations | 3-5x | GPU instances + training |
| Full-text Search | 1.5-2x | Search cluster |
| Feature Store | 2x | Feature computation |
| OLAP | 10-50x | Massive pre-aggregations |
| Distributed Tracing | 1.2x | Trace storage |
| Probabilistic | 0.1-0.5x | Memory efficiency |

### Latency Characteristics

| Pattern | P50 Latency | P99 Latency | Notes |
|---------|-------------|-------------|-------|
| REST + Cache | 5ms | 50ms | Cache hit fast, miss slow |
| Stream | 10ms | 100ms | Processing delay |
| Worker Pool | 50ms | 500ms | Queue wait time |
| API Gateway | 2ms | 10ms | Routing overhead |
| Message Queue | 10ms | 100ms | Async, not real-time |
| Rate Limiter | <1ms | 2ms | Fast check |
| ML Inference | 20ms | 100ms | Model evaluation |
| Full-text Search | 10ms | 50ms | Index lookup |
| OLAP | 50ms | 500ms | Complex aggregations |
| Distributed Tracing | +5% | +5% | Overhead percentage |

---

## Decision Tree

### Start Here: What's Your Primary Challenge?

```
[Your Challenge?]
    ├─ High read load → App 01 (Cache) or App 09 (Multi-tier)
    ├─ Need real-time data → App 02 (Stream) or App 06 (Kappa)
    ├─ CPU-intensive tasks → App 03 (Worker Pool)
    ├─ Many microservices → App 04 (Gateway) + App 18 (Tracing)
    ├─ Large data exports → App 05 (Bulk Export)
    ├─ Complete audit trail → App 07 (Event Sourcing)
    ├─ Time-series data → App 08 (TimeSeries DB)
    ├─ Async processing → App 10 (Message Queue)
    ├─ Resource protection → App 11 (Rate Limiter)
    ├─ Batch + Real-time → App 12 (Lambda)
    ├─ Data synchronization → App 13 (CDC)
    ├─ Personalization → App 14 (ML)
    ├─ Text search → App 15 (Full-text)
    ├─ ML at scale → App 16 (Feature Store)
    ├─ Fast analytics → App 17 (OLAP)
    └─ Memory constraints → App 19 (Probabilistic)
```

### Composability: Mix and Match

**Example 1: E-commerce Platform**
- App 01: Product catalog (cache)
- App 02: Real-time inventory (stream)
- App 10: Order processing (queue)
- App 14: Product recommendations (ML)
- App 15: Product search (full-text)

**Example 2: Monitoring Platform**
- App 02: Metrics ingestion (stream)
- App 08: Metrics storage (TimeSeries)
- App 17: Analytics dashboard (OLAP)
- App 18: Service tracing (distributed tracing)

**Example 3: Financial System**
- App 07: Transaction ledger (event sourcing)
- App 11: API rate limiting (rate limiter)
- App 13: Sync to data warehouse (CDC)
- App 19: Fraud detection (probabilistic)

---

## Next Steps

### Want to Learn More?

1. **Try the demos** - Each app has sample data and realistic workloads
2. **Read the source** - `/examples/` directory has full implementations
3. **Mix patterns** - Combine multiple apps for your use case
4. **Measure** - Profile your specific workload

### Implementation Guide

For each pattern, ask:
1. **Do I need this?** - Check "When to Use"
2. **What's the cost?** - See trade-offs table
3. **How do I start?** - See decision criteria
4. **What's the ROI?** - See business impact

---

## Summary

The key insight of composable architecture:

> **There is no silver bullet. Different problems require different trade-offs.**

- Use **caching** for read-heavy workloads
- Use **streams** for real-time requirements
- Use **batching** when latency isn't critical
- Use **queues** for async processing
- Use **probabilistic structures** for massive scale

**The best architecture is the one that solves YOUR specific problem with acceptable trade-offs.**

Choose wisely. Compose freely. 🚀
