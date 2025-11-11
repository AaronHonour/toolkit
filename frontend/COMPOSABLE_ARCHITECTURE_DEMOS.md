# Composable Architecture Demos & Narratives

This guide demonstrates how to combine multiple architectural patterns from our 19 frontend applications to build real-world systems. Each demo provides a complete narrative: the business problem, technical solution, pattern composition, and implementation roadmap.

---

## Table of Contents

1. [Demo 1: E-commerce Platform](#demo-1-e-commerce-platform)
2. [Demo 2: Real-time Analytics Platform](#demo-2-real-time-analytics-platform)
3. [Demo 3: Financial Trading System](#demo-3-financial-trading-system)
4. [Demo 4: Content Delivery Platform](#demo-4-content-delivery-platform)
5. [Demo 5: IoT Monitoring System](#demo-5-iot-monitoring-system)
6. [Demo 6: Machine Learning Platform](#demo-6-machine-learning-platform)
7. [Pattern Composition Cheat Sheet](#pattern-composition-cheat-sheet)
8. [Implementation Roadmap Templates](#implementation-roadmap-templates)

---

## Demo 1: E-commerce Platform

### 🎯 Business Problem

**Company**: ModernShop (Online Retailer)
**Challenge**: Build a scalable e-commerce platform handling 1M+ daily users with:
- Fast product searches
- Real-time inventory updates
- Personalized recommendations
- Order tracking
- Flash sale support (10K concurrent users)

### 📊 Current Pain Points

- Product database queries taking 500ms average
- Inventory sync delays causing overselling
- Generic product listings (no personalization)
- Search taking 2-3 seconds
- System crashes during flash sales

### 🏗️ Pattern Composition

We'll combine **5 patterns** from our toolkit:

| App | Pattern | Purpose | Expected Impact |
|-----|---------|---------|-----------------|
| **App 01** | LRU Cache | Product catalog caching | 50x faster reads (10ms vs 500ms) |
| **App 13** | CDC (Change Data Capture) | Real-time inventory sync | 100ms sync latency (was 5s) |
| **App 14** | Recommendation Engine | Personalized product suggestions | +35% conversion rate |
| **App 15** | Search Engine | Fast product search | 50ms search (was 2-3s) |
| **App 11** | Rate Limiter | Protect during flash sales | Graceful degradation vs crashes |

### 🔧 Technical Implementation Narrative

#### Phase 1: Product Catalog Performance (Week 1-2)

**Problem**: Database queries for product details hitting 500ms average, 2s P99.

**Solution**: Implement App 01 (LRU Cache Pattern)

```typescript
// Product Service with LRU Cache
class ProductService {
  private cache: LRUCache<string, Product>;

  constructor() {
    // Cache 10,000 most popular products (80/20 rule)
    this.cache = new LRUCache({
      max: 10000,
      ttl: 1000 * 60 * 5, // 5 minutes
      updateAgeOnGet: true
    });
  }

  async getProduct(productId: string): Promise<Product> {
    // Check cache first
    const cached = this.cache.get(productId);
    if (cached) {
      return cached; // ~10ms response
    }

    // Cache miss - fetch from database
    const product = await this.db.query('SELECT * FROM products WHERE id = ?', [productId]);
    this.cache.set(productId, product);
    return product; // ~500ms response
  }
}
```

**Results**:
- ✅ Cache hit rate: 85% (due to product popularity distribution)
- ✅ Average response time: 85ms (from 500ms)
- ✅ P99 latency: 150ms (from 2s)
- ✅ Database load reduced by 85%

**Cost Impact**:
- Before: 1000 RDS r5.2xlarge instances ($800/mo each) = $800K/mo
- After: 150 instances + 50GB Redis ($0.50/GB/mo) = $120K/mo + $25/mo = **$120,025/mo**
- **Savings: $680K/mo (85% reduction)**

#### Phase 2: Real-time Inventory Sync (Week 3-4)

**Problem**: Inventory updates taking 5+ seconds to propagate, causing overselling.

**Solution**: Implement App 13 (CDC Pattern)

```typescript
// CDC Pipeline for Inventory
class InventorySync {
  private debeziumConnector: DebeziumConnector;
  private cache: LRUCache;

  constructor(productService: ProductService) {
    this.cache = productService.cache;

    // Listen to inventory table changes
    this.debeziumConnector = new DebeziumConnector({
      database: 'inventory_db',
      tables: ['inventory'],
      operations: ['UPDATE', 'INSERT']
    });

    // Stream changes to cache invalidation
    this.debeziumConnector.on('change', (event) => {
      const productId = event.payload.after.product_id;

      // Invalidate cache immediately
      this.cache.delete(productId);

      // Broadcast to all frontend clients via WebSocket
      this.websocket.broadcast({
        type: 'INVENTORY_UPDATE',
        productId,
        quantity: event.payload.after.quantity
      });
    });
  }
}
```

**Results**:
- ✅ Sync latency: 100ms (from 5s)
- ✅ Overselling incidents: 0 (from 50/day)
- ✅ Real-time UI updates for all users

**Cost Impact**:
- CDC infrastructure: Kafka + Debezium = $500/mo
- WebSocket connections: 1M users × $0.25/1000 = $250/mo
- **Total: $750/mo**

#### Phase 3: Personalized Recommendations (Week 5-6)

**Problem**: Generic product listings, low conversion rates.

**Solution**: Implement App 14 (Recommendation Engine)

```typescript
// ML Recommendation Service
class RecommendationService {
  private modelCache: Map<string, TensorFlowModel>;
  private featureStore: FeatureStore;

  async getRecommendations(userId: string, context: Context): Promise<Product[]> {
    // Fetch user features from feature store (App 16)
    const userFeatures = await this.featureStore.getFeatures(userId, [
      'purchase_history_30d',
      'browsing_history_7d',
      'category_affinity',
      'price_sensitivity'
    ]);

    // Load pre-trained model
    const model = await this.loadModel('product_recommendation_v3');

    // Run inference (optimized for <50ms)
    const predictions = await model.predict({
      user: userFeatures,
      context: {
        time: context.timestamp,
        device: context.device,
        location: context.location
      }
    });

    // Fetch top 20 products from cache (App 01)
    const productIds = predictions.topK(20);
    return await Promise.all(
      productIds.map(id => this.productService.getProduct(id))
    );
  }
}
```

**Results**:
- ✅ Conversion rate: +35% (from 2.5% to 3.4%)
- ✅ Average order value: +22% ($75 to $92)
- ✅ Recommendation latency: 45ms P99

**Business Impact**:
- Revenue: 1M daily users × 3.4% conversion × $92 AOV = **$3.13M/day** (was $1.88M/day)
- **Additional revenue: $1.25M/day = $456M/year**

**Cost Impact**:
- ML inference: 100 GPU instances (g4dn.xlarge) @ $400/mo = $40K/mo
- Feature store: $5K/mo
- **Total: $45K/mo**
- **ROI: $1.25M/day revenue vs $45K/mo cost = 2,778% monthly ROI**

#### Phase 4: Fast Product Search (Week 7-8)

**Problem**: Product search taking 2-3 seconds, poor relevance.

**Solution**: Implement App 15 (Search Engine)

```typescript
// Elasticsearch-based Product Search
class ProductSearchService {
  private esClient: ElasticsearchClient;

  async search(query: string, filters: Filters): Promise<SearchResults> {
    const response = await this.esClient.search({
      index: 'products',
      body: {
        query: {
          bool: {
            must: [
              {
                multi_match: {
                  query: query,
                  fields: ['name^3', 'description', 'category^2', 'tags'],
                  type: 'best_fields',
                  fuzziness: 'AUTO'
                }
              }
            ],
            filter: [
              { range: { price: { gte: filters.minPrice, lte: filters.maxPrice } } },
              { term: { in_stock: true } }
            ]
          }
        },
        aggs: {
          category_facets: { terms: { field: 'category' } },
          price_ranges: { range: { field: 'price', ranges: [...] } }
        },
        size: 50,
        from: filters.page * 50
      }
    });

    // Boost results using ML recommendations
    const boosted = await this.boostWithRecommendations(
      response.hits.hits,
      userId
    );

    return {
      products: boosted,
      facets: response.aggregations,
      total: response.hits.total,
      took: response.took // ~50ms
    };
  }
}
```

**Results**:
- ✅ Search latency: 50ms (from 2-3s)
- ✅ Relevance score: 0.92 (from 0.65)
- ✅ Search-to-purchase conversion: +45%

**Cost Impact**:
- Elasticsearch cluster: 10 nodes (r5.xlarge) @ $250/mo = $2.5K/mo
- **Total: $2.5K/mo**

#### Phase 5: Flash Sale Protection (Week 9-10)

**Problem**: System crashes during flash sales (10K concurrent requests).

**Solution**: Implement App 11 (Rate Limiter)

```typescript
// Multi-tier Rate Limiting
class FlashSaleRateLimiter {
  private rateLimiters: Map<string, TokenBucket>;

  constructor() {
    // Tier 1: Global rate limit (system protection)
    this.rateLimiters.set('global', new TokenBucket({
      capacity: 10000,
      fillRate: 5000, // 5K requests/second
      algorithm: 'token_bucket'
    }));

    // Tier 2: Per-user rate limit (fairness)
    this.rateLimiters.set('per_user', new TokenBucket({
      capacity: 10,
      fillRate: 5, // 5 requests/second per user
      algorithm: 'sliding_window'
    }));

    // Tier 3: Per-product rate limit (inventory protection)
    this.rateLimiters.set('per_product', new TokenBucket({
      capacity: 100,
      fillRate: 50, // 50 purchases/second per product
      algorithm: 'leaky_bucket'
    }));
  }

  async checkAddToCart(userId: string, productId: string): Promise<RateLimitResult> {
    // Check all three tiers
    const checks = await Promise.all([
      this.rateLimiters.get('global').consume(1),
      this.rateLimiters.get('per_user').consume(userId, 1),
      this.rateLimiters.get('per_product').consume(productId, 1)
    ]);

    if (checks.every(check => check.allowed)) {
      return { allowed: true };
    }

    // Return graceful degradation response
    return {
      allowed: false,
      retryAfter: Math.max(...checks.map(c => c.retryAfter)),
      message: 'High demand - please try again in a moment'
    };
  }
}
```

**Results**:
- ✅ System uptime during flash sales: 99.99% (from 60%)
- ✅ Fair distribution: All users get equal chance
- ✅ Database protection: No overload incidents

**Business Impact**:
- Flash sale revenue protected: $500K/sale × 12 sales/year = **$6M/year**
- Customer satisfaction: NPS +15 points

**Cost Impact**:
- Rate limiting infrastructure: Redis cluster = $200/mo
- **Total: $200/mo**

### 📈 Combined Results: The Complete System

#### Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Product page load** | 500ms | 10ms | **50x faster** |
| **Search latency** | 2-3s | 50ms | **40-60x faster** |
| **Inventory sync** | 5s | 100ms | **50x faster** |
| **Flash sale uptime** | 60% | 99.99% | **+66% uptime** |
| **Conversion rate** | 2.5% | 3.4% | **+36%** |

#### Cost Analysis

| Component | Monthly Cost | Annual Cost |
|-----------|--------------|-------------|
| RDS (reduced) | $120K | $1.44M |
| Redis (cache + rate limiting) | $225 | $2.7K |
| CDC infrastructure | $750 | $9K |
| ML inference | $45K | $540K |
| Elasticsearch | $2.5K | $30K |
| **Total Infrastructure** | **$168,475** | **$2,021,700** |
| **Previous Infrastructure** | **$800K** | **$9.6M** |
| **Savings** | **$631,525/mo** | **$7,578,300/year** |

#### Revenue Impact

| Revenue Source | Annual Impact |
|----------------|---------------|
| Increased conversion (2.5% → 3.4%) | **+$456M** |
| Increased AOV ($75 → $92) | **+$165M** |
| Flash sales protected | **+$6M** |
| **Total Revenue Increase** | **+$627M/year** |

#### ROI Summary

```
Cost Savings:     $7.6M/year
Revenue Increase: $627M/year
Total Benefit:    $634.6M/year

Infrastructure Investment: $2M/year
ROI: 31,730%
Payback Period: 1.1 days
```

### 🛠️ Implementation Code Example

Here's how the complete system integrates:

```typescript
// Main E-commerce Application
class EcommerceApp {
  private productService: ProductService;           // App 01: LRU Cache
  private inventorySync: InventorySync;            // App 13: CDC
  private recommendations: RecommendationService;   // App 14: ML Recommendations
  private search: ProductSearchService;             // App 15: Search
  private rateLimiter: FlashSaleRateLimiter;       // App 11: Rate Limiting

  async handleProductPageRequest(req: Request): Promise<Response> {
    const { productId, userId } = req.params;

    // Fast product fetch from cache (10ms)
    const product = await this.productService.getProduct(productId);

    // Personalized recommendations (45ms)
    const recommendations = await this.recommendations.getRecommendations(
      userId,
      { page: 'product', currentProduct: productId }
    );

    // Related search suggestions (20ms)
    const relatedSearches = await this.search.suggestRelated(product.name);

    return {
      product,
      recommendations,
      relatedSearches,
      responseTime: 75 // ms (combined)
    };
  }

  async handleAddToCart(req: Request): Promise<Response> {
    const { userId, productId, quantity } = req.body;

    // Rate limiting check (2ms)
    const rateLimitCheck = await this.rateLimiter.checkAddToCart(userId, productId);
    if (!rateLimitCheck.allowed) {
      return {
        error: 'RATE_LIMITED',
        message: rateLimitCheck.message,
        retryAfter: rateLimitCheck.retryAfter
      };
    }

    // Get real-time inventory (cache + CDC)
    const product = await this.productService.getProduct(productId);

    if (product.inventory < quantity) {
      return {
        error: 'OUT_OF_STOCK',
        message: 'This item is currently out of stock'
      };
    }

    // Add to cart
    await this.cartService.add(userId, productId, quantity);

    return { success: true };
  }

  async handleSearch(req: Request): Promise<Response> {
    const { query, filters, userId } = req.params;

    // Fast search with personalization (50ms)
    const results = await this.search.search(query, filters);

    // Boost with recommendations (15ms)
    const boosted = await this.recommendations.boostResults(results, userId);

    return {
      products: boosted,
      total: results.total,
      facets: results.facets,
      responseTime: 65 // ms
    };
  }
}
```

---

## Demo 2: Real-time Analytics Platform

### 🎯 Business Problem

**Company**: DataPulse (SaaS Analytics Provider)
**Challenge**: Build real-time analytics dashboard for IoT devices:
- 100K devices sending metrics every 5 seconds
- Real-time dashboard updates (<1s latency)
- Historical data analysis (2 years retention)
- Anomaly detection
- Cost-effective storage ($50K/month budget)

### 📊 Current Pain Points

- Batch processing causing 1-hour dashboard delays
- Database overwhelmed by write load (20K writes/second)
- Query performance degrading (10s+ for dashboards)
- Storage costs exploding ($200K/month)
- No anomaly alerts

### 🏗️ Pattern Composition

We'll combine **7 patterns**:

| App | Pattern | Purpose | Expected Impact |
|-----|---------|---------|-----------------|
| **App 02** | Stream Processing | Real-time metric aggregation | <1s latency (was 1 hour) |
| **App 08** | TimeSeries Database | Efficient time-ordered storage | 10x storage reduction |
| **App 17** | OLAP | Fast analytical queries | 100x faster dashboards |
| **App 10** | Message Queue | Decouple ingestion from processing | 99.99% reliability |
| **App 19** | Probabilistic (HyperLogLog) | Efficient unique counts | 1000x memory reduction |
| **App 18** | Distributed Tracing | Debug performance issues | MTTD reduction 80% |
| **App 09** | Multi-tier Cache | Fast dashboard serving | 50x faster queries |

### 🔧 Technical Implementation Narrative

#### Phase 1: Stream Processing Pipeline (Week 1-2)

**Problem**: Batch processing causing 1-hour delays, no real-time visibility.

**Solution**: Implement App 02 (Stream Processing)

```typescript
// Real-time Metric Processing with Apache Flink
class MetricStreamProcessor {
  private flink: FlinkJobManager;

  async startProcessing() {
    // Define stream processing job
    const job = this.flink.createJob({
      source: 'kafka.metrics.raw', // 20K messages/second

      // Step 1: Parse and validate
      map: (event) => ({
        deviceId: event.device_id,
        metric: event.metric_name,
        value: parseFloat(event.value),
        timestamp: new Date(event.timestamp)
      }),

      // Step 2: Tumbling window aggregation (1-minute windows)
      keyBy: ['deviceId', 'metric'],
      window: {
        type: 'tumbling',
        duration: '1 minute'
      },
      aggregate: {
        count: (values) => values.length,
        sum: (values) => values.reduce((a, b) => a + b.value, 0),
        avg: (values) => values.reduce((a, b) => a + b.value, 0) / values.length,
        min: (values) => Math.min(...values.map(v => v.value)),
        max: (values) => Math.max(...values.map(v => v.value)),
        p50: (values) => this.percentile(values, 0.5),
        p95: (values) => this.percentile(values, 0.95),
        p99: (values) => this.percentile(values, 0.99)
      },

      // Step 3: Sink to TimeSeries DB
      sink: 'timescaledb.metrics_aggregated'
    });

    await job.start();
  }
}
```

**Results**:
- ✅ Processing latency: 500ms (from 1 hour)
- ✅ Throughput: 20K events/second sustained
- ✅ Dashboard updates: Real-time (<1s)

**Cost Impact**:
- Flink cluster: 5 nodes (c5.2xlarge) @ $250/mo = $1,250/mo
- Kafka: 3 brokers @ $150/mo = $450/mo
- **Total: $1,700/mo**

#### Phase 2: TimeSeries Storage (Week 3-4)

**Problem**: PostgreSQL overwhelmed, storage costs $200K/month.

**Solution**: Implement App 08 (TimeSeries Database)

```typescript
// TimescaleDB with Continuous Aggregates
class TimeSeriesStorage {
  private db: TimescaleDB;

  async initialize() {
    // Create hypertable for raw metrics
    await this.db.query(`
      CREATE TABLE metrics_raw (
        time TIMESTAMPTZ NOT NULL,
        device_id VARCHAR(50) NOT NULL,
        metric_name VARCHAR(100) NOT NULL,
        value DOUBLE PRECISION NOT NULL
      );

      -- Convert to hypertable (automatic partitioning)
      SELECT create_hypertable('metrics_raw', 'time', chunk_time_interval => INTERVAL '1 day');

      -- Create indexes on commonly queried dimensions
      CREATE INDEX idx_device_time ON metrics_raw (device_id, time DESC);
      CREATE INDEX idx_metric_time ON metrics_raw (metric_name, time DESC);
    `);

    // Continuous aggregates (pre-computed rollups)
    await this.db.query(`
      -- 1-minute rollups (kept for 7 days)
      CREATE MATERIALIZED VIEW metrics_1min
      WITH (timescaledb.continuous) AS
        SELECT device_id, metric_name,
               time_bucket('1 minute', time) AS bucket,
               AVG(value) as avg, MIN(value) as min, MAX(value) as max, COUNT(*) as count
        FROM metrics_raw
        GROUP BY device_id, metric_name, bucket;

      -- 1-hour rollups (kept for 90 days)
      CREATE MATERIALIZED VIEW metrics_1hour
      WITH (timescaledb.continuous) AS
        SELECT device_id, metric_name,
               time_bucket('1 hour', time) AS bucket,
               AVG(value) as avg, MIN(value) as min, MAX(value) as max, COUNT(*) as count
        FROM metrics_raw
        GROUP BY device_id, metric_name, bucket;

      -- 1-day rollups (kept for 2 years)
      CREATE MATERIALIZED VIEW metrics_1day
      WITH (timescaledb.continuous) AS
        SELECT device_id, metric_name,
               time_bucket('1 day', time) AS bucket,
               AVG(value) as avg, MIN(value) as min, MAX(value) as max, COUNT(*) as count
        FROM metrics_raw
        GROUP BY device_id, metric_name, bucket;
    `);

    // Retention policies (automatic data lifecycle)
    await this.db.query(`
      -- Drop raw data older than 7 days
      SELECT add_retention_policy('metrics_raw', INTERVAL '7 days');

      -- Drop 1-minute aggregates older than 90 days
      SELECT add_retention_policy('metrics_1min', INTERVAL '90 days');

      -- Drop 1-hour aggregates older than 2 years
      SELECT add_retention_policy('metrics_1hour', INTERVAL '2 years');
    `);

    // Compression (reduces storage by 90%)
    await this.db.query(`
      ALTER TABLE metrics_raw SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'device_id, metric_name'
      );

      -- Compress chunks older than 1 day
      SELECT add_compression_policy('metrics_raw', INTERVAL '1 day');
    `);
  }

  async queryDashboard(deviceId: string, timeRange: TimeRange): Promise<Metrics> {
    // Smart query routing based on time range
    const duration = timeRange.end - timeRange.start;

    if (duration <= 7 * 24 * 60 * 60 * 1000) {
      // Last 7 days - use 1-minute aggregates
      return this.db.query(`
        SELECT bucket as time, avg, min, max
        FROM metrics_1min
        WHERE device_id = $1 AND bucket >= $2 AND bucket < $3
        ORDER BY bucket DESC
      `, [deviceId, timeRange.start, timeRange.end]);
    } else if (duration <= 90 * 24 * 60 * 60 * 1000) {
      // Last 90 days - use 1-hour aggregates
      return this.db.query(`
        SELECT bucket as time, avg, min, max
        FROM metrics_1hour
        WHERE device_id = $1 AND bucket >= $2 AND bucket < $3
        ORDER BY bucket DESC
      `, [deviceId, timeRange.start, timeRange.end]);
    } else {
      // Older than 90 days - use 1-day aggregates
      return this.db.query(`
        SELECT bucket as time, avg, min, max
        FROM metrics_1day
        WHERE device_id = $1 AND bucket >= $2 AND bucket < $3
        ORDER BY bucket DESC
      `, [deviceId, timeRange.start, timeRange.end]);
    }
  }
}
```

**Results**:
- ✅ Write throughput: 20K inserts/second (was 2K)
- ✅ Storage reduction: 90% (compression + rollups)
- ✅ Query performance: 100ms (from 10s+)

**Cost Impact**:
- Before: 50TB × $4K/TB/mo = $200K/mo
- After: 5TB (compressed) × $1K/TB/mo = $5K/mo
- TimescaleDB cluster: 3 nodes (r5.4xlarge) @ $1.5K/mo = $4.5K/mo
- **Total: $9.5K/mo**
- **Savings: $190.5K/mo (95% reduction)**

#### Phase 3: OLAP Analytics (Week 5-6)

**Problem**: Complex analytical queries (device comparisons, trend analysis) timing out.

**Solution**: Implement App 17 (OLAP with ClickHouse)

```typescript
// ClickHouse OLAP Engine
class OLAPAnalytics {
  private clickhouse: ClickHouseClient;

  async initialize() {
    // Create distributed table for analytics
    await this.clickhouse.query(`
      CREATE TABLE metrics_olap (
        timestamp DateTime,
        device_id String,
        metric_name String,
        value Float64,
        device_type String,
        location String,
        customer_id String
      ) ENGINE = MergeTree()
      PARTITION BY toYYYYMM(timestamp)
      ORDER BY (device_id, metric_name, timestamp);

      -- Create materialized view for common aggregations
      CREATE MATERIALIZED VIEW device_daily_stats
      ENGINE = SummingMergeTree()
      PARTITION BY toYYYYMM(day)
      ORDER BY (device_id, metric_name, day)
      AS SELECT
        toDate(timestamp) as day,
        device_id,
        metric_name,
        count() as event_count,
        avg(value) as avg_value,
        min(value) as min_value,
        max(value) as max_value,
        quantile(0.95)(value) as p95_value
      FROM metrics_olap
      GROUP BY day, device_id, metric_name;
    `);
  }

  async analyzeDeviceComparison(deviceIds: string[], metric: string): Promise<Analysis> {
    // Complex analytical query (executes in <200ms)
    const result = await this.clickhouse.query(`
      SELECT
        device_id,
        toStartOfHour(timestamp) as hour,
        avg(value) as avg_value,
        quantile(0.5)(value) as median,
        quantile(0.95)(value) as p95,
        stddevPop(value) as stddev
      FROM metrics_olap
      WHERE device_id IN (${deviceIds.map(id => `'${id}'`).join(',')})
        AND metric_name = '${metric}'
        AND timestamp >= now() - INTERVAL 24 HOUR
      GROUP BY device_id, hour
      ORDER BY hour, device_id
    `);

    return this.formatComparisonReport(result);
  }

  async detectAnomalies(customerId: string): Promise<Anomaly[]> {
    // Statistical anomaly detection using OLAP
    const result = await this.clickhouse.query(`
      WITH stats AS (
        SELECT
          device_id,
          metric_name,
          avg(value) as mean,
          stddevPop(value) as stddev
        FROM metrics_olap
        WHERE customer_id = '${customerId}'
          AND timestamp >= now() - INTERVAL 7 DAY
        GROUP BY device_id, metric_name
      ),
      recent AS (
        SELECT
          device_id,
          metric_name,
          timestamp,
          value
        FROM metrics_olap
        WHERE customer_id = '${customerId}'
          AND timestamp >= now() - INTERVAL 1 HOUR
      )
      SELECT
        r.device_id,
        r.metric_name,
        r.timestamp,
        r.value,
        s.mean,
        s.stddev,
        abs(r.value - s.mean) / s.stddev as z_score
      FROM recent r
      JOIN stats s ON r.device_id = s.device_id AND r.metric_name = s.metric_name
      WHERE abs(r.value - s.mean) / s.stddev > 3.0  -- 3-sigma anomalies
      ORDER BY z_score DESC
    `);

    return result;
  }
}
```

**Results**:
- ✅ Analytical query latency: 200ms (from 10s+)
- ✅ Concurrent query capacity: 1000+ users
- ✅ Anomaly detection: Real-time (<5 min detection)

**Cost Impact**:
- ClickHouse cluster: 5 nodes (c5.2xlarge) @ $250/mo = $1,250/mo
- **Total: $1,250/mo**

#### Phase 4: Efficient Cardinality Counting (Week 7)

**Problem**: Counting unique devices/metrics consuming massive memory (10GB+ per query).

**Solution**: Implement App 19 (Probabilistic - HyperLogLog)

```typescript
// HyperLogLog for Unique Counts
class CardinalityCounter {
  private redis: RedisClient;

  async trackUniqueDevices(customerId: string, deviceId: string) {
    // Add to HyperLogLog (12KB memory vs 10GB for exact set)
    await this.redis.pfadd(`unique_devices:${customerId}:${this.today()}`, deviceId);
  }

  async getUniqueDeviceCount(customerId: string, dateRange: DateRange): Promise<number> {
    const keys = [];
    for (let date = dateRange.start; date <= dateRange.end; date.addDays(1)) {
      keys.push(`unique_devices:${customerId}:${date.format('YYYY-MM-DD')}`);
    }

    // Merge HyperLogLogs and get cardinality estimate
    // Error rate: ±0.81% (acceptable for analytics)
    const uniqueCount = await this.redis.pfcount(...keys);

    return uniqueCount;
  }

  async getTopMetrics(customerId: string): Promise<MetricStats[]> {
    // Combine HyperLogLog with Count-Min Sketch
    const metrics = await this.redis.scan(`metric_count:${customerId}:*`);

    const stats = await Promise.all(metrics.map(async (metric) => {
      const [frequency, cardinality] = await Promise.all([
        this.redis.get(`metric_count:${customerId}:${metric}`),
        this.redis.pfcount(`metric_devices:${customerId}:${metric}`)
      ]);

      return {
        metric,
        frequency: parseInt(frequency),
        uniqueDevices: cardinality
      };
    }));

    return stats.sort((a, b) => b.frequency - a.frequency).slice(0, 100);
  }
}
```

**Results**:
- ✅ Memory reduction: 1000x (12KB vs 10GB)
- ✅ Accuracy: 99.19% (±0.81% error)
- ✅ Query speed: 10ms (from 5s)

**Cost Impact**:
- Redis cluster: 3 nodes (r5.large) @ $100/mo = $300/mo
- **Total: $300/mo**

### 📈 Combined Results: Analytics Platform

#### Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Dashboard latency** | 1 hour | <1s | **3,600x faster** |
| **Write throughput** | 2K/s | 20K/s | **10x increase** |
| **Query performance** | 10s | 200ms | **50x faster** |
| **Anomaly detection** | None | <5min | **Real-time** |

#### Cost Analysis

| Component | Monthly Cost |
|-----------|--------------|
| Stream processing (Flink + Kafka) | $1,700 |
| TimeSeries DB (TimescaleDB) | $9,500 |
| OLAP (ClickHouse) | $1,250 |
| Probabilistic structures (Redis) | $300 |
| **Total Infrastructure** | **$12,750** |
| **Previous Infrastructure** | **$200,000** |
| **Savings** | **$187,250/mo (94% reduction)** |

---

## Demo 3: Financial Trading System

### 🎯 Business Problem

**Company**: FastTrade (Algorithmic Trading Platform)
**Challenge**: Build ultra-low-latency trading system:
- Order execution <5ms P99
- Real-time risk calculations
- Audit trail for compliance
- Handle 50K orders/second during peak
- Zero data loss (regulatory requirement)

### 🏗️ Pattern Composition

| App | Pattern | Purpose | Expected Impact |
|-----|---------|---------|-----------------|
| **App 07** | Event Sourcing | Complete audit trail | 100% compliance |
| **App 10** | Message Queue | Reliable order routing | Zero message loss |
| **App 11** | Rate Limiter | Risk management | Prevent runaway trading |
| **App 09** | Multi-tier Cache | Fast price lookups | <1ms latency |
| **App 18** | Distributed Tracing | Debug trade execution | MTTD 90% reduction |
| **App 12** | Lambda Architecture | Real-time + historical analysis | Best of both worlds |

### 🔧 Technical Implementation Narrative

#### Phase 1: Event Sourcing for Audit Trail (Week 1-2)

**Problem**: Regulatory compliance requires complete, immutable audit trail of all trading decisions.

**Solution**: Implement App 07 (Event Sourcing)

```typescript
// Event Sourcing for Trading System
class TradingEventStore {
  private eventStore: EventStoreDB;

  async recordOrderPlaced(order: Order) {
    // Every action is an immutable event
    await this.eventStore.appendToStream(`order-${order.id}`, [
      {
        type: 'OrderPlaced',
        data: {
          orderId: order.id,
          userId: order.userId,
          symbol: order.symbol,
          quantity: order.quantity,
          price: order.price,
          timestamp: Date.now(),
          riskCheckPassed: order.riskCheckPassed,
          accountBalance: order.accountBalance
        },
        metadata: {
          userId: order.userId,
          ipAddress: order.ipAddress,
          sessionId: order.sessionId
        }
      }
    ]);
  }

  async recordOrderExecuted(orderId: string, execution: Execution) {
    await this.eventStore.appendToStream(`order-${orderId}`, [
      {
        type: 'OrderExecuted',
        data: {
          orderId,
          executionId: execution.id,
          fillPrice: execution.price,
          fillQuantity: execution.quantity,
          venue: execution.venue,
          timestamp: Date.now(),
          latency: execution.latency
        }
      }
    ]);
  }

  // Reconstruct complete order history from events
  async reconstructOrderState(orderId: string): Promise<OrderState> {
    const events = await this.eventStore.readStream(`order-${orderId}`);

    let state: OrderState = { status: 'UNKNOWN' };

    for (const event of events) {
      switch (event.type) {
        case 'OrderPlaced':
          state = {
            ...event.data,
            status: 'PLACED',
            fills: []
          };
          break;
        case 'OrderExecuted':
          state.fills.push(event.data);
          state.status = state.fills.reduce((sum, fill) => sum + fill.fillQuantity, 0) >= state.quantity
            ? 'FILLED'
            : 'PARTIALLY_FILLED';
          break;
        case 'OrderCancelled':
          state.status = 'CANCELLED';
          break;
      }
    }

    return state;
  }

  // Compliance: Generate audit report
  async generateAuditReport(userId: string, dateRange: DateRange): Promise<AuditReport> {
    const events = await this.eventStore.readAll({
      filter: {
        streamNamePrefix: 'order-',
        metadata: { userId }
      },
      timeRange: dateRange
    });

    return {
      totalOrders: events.filter(e => e.type === 'OrderPlaced').length,
      totalExecutions: events.filter(e => e.type === 'OrderExecuted').length,
      events: events.map(e => ({
        timestamp: e.created,
        type: e.type,
        data: e.data,
        sequenceNumber: e.position
      }))
    };
  }
}
```

**Results**:
- ✅ Audit completeness: 100% (every action recorded)
- ✅ Compliance: SEC/FINRA ready
- ✅ Reconstruction: Any order state recoverable
- ✅ Time-travel debugging: Replay events to find bugs

**Cost Impact**:
- EventStoreDB cluster: $2K/mo
- **Total: $2K/mo**

#### Phase 2: Order Routing with Message Queue (Week 3-4)

**Problem**: Order routing must be 100% reliable (zero message loss), handle 50K orders/second.

**Solution**: Implement App 10 (Message Queue)

```typescript
// RabbitMQ for Reliable Order Routing
class OrderRouter {
  private rabbitMQ: RabbitMQClient;

  async initialize() {
    // Create durable queues with guaranteed delivery
    await this.rabbitMQ.declareQueue('orders.incoming', {
      durable: true,
      maxPriority: 10, // Priority queue for urgent orders
      deadLetterExchange: 'orders.dlx'
    });

    await this.rabbitMQ.declareQueue('orders.risk-check', {
      durable: true
    });

    await this.rabbitMQ.declareQueue('orders.execution', {
      durable: true,
      arguments: {
        'x-max-priority': 10
      }
    });

    // Dead letter queue for failed orders
    await this.rabbitMQ.declareQueue('orders.failed', {
      durable: true
    });
  }

  async routeOrder(order: Order) {
    // Publish with publisher confirms (guaranteed delivery)
    await this.rabbitMQ.publish('orders.incoming', order, {
      persistent: true,
      mandatory: true,
      priority: order.urgent ? 10 : 5,
      headers: {
        orderId: order.id,
        userId: order.userId,
        timestamp: Date.now()
      }
    });

    // Wait for broker acknowledgment
    await this.rabbitMQ.waitForConfirms();
  }

  async processRiskChecks() {
    // Consumer with manual acknowledgments
    await this.rabbitMQ.consume('orders.incoming', async (msg) => {
      const order = JSON.parse(msg.content.toString());

      try {
        // Perform risk check
        const riskCheck = await this.performRiskCheck(order);

        if (riskCheck.passed) {
          // Route to execution queue
          await this.rabbitMQ.publish('orders.execution', {
            ...order,
            riskCheckPassed: true
          }, { persistent: true });

          // Acknowledge message (remove from queue)
          msg.ack();
        } else {
          // Reject and move to DLQ
          msg.reject(false);

          // Notify user
          await this.notifyRiskRejection(order.userId, riskCheck.reason);
        }
      } catch (error) {
        // Requeue for retry (exponential backoff)
        msg.nack(true);
      }
    }, {
      prefetch: 100, // Process 100 messages at a time
      noAck: false // Manual acknowledgments
    });
  }
}
```

**Results**:
- ✅ Message loss: 0 (guaranteed delivery)
- ✅ Throughput: 50K orders/second
- ✅ Latency: 2ms P99 (queue processing)
- ✅ Reliability: 99.999% uptime

**Cost Impact**:
- RabbitMQ cluster: 5 nodes @ $200/mo = $1K/mo
- **Total: $1K/mo**

#### Phase 3: Risk Management with Rate Limiting (Week 5)

**Problem**: Prevent runaway algorithmic trading, enforce position limits.

**Solution**: Implement App 11 (Rate Limiter)

```typescript
// Multi-dimensional Rate Limiting
class TradingRiskLimiter {
  private limiters: Map<string, RateLimiter>;

  constructor() {
    // Per-user order rate limit
    this.limiters.set('user_orders', new SlidingWindowRateLimiter({
      window: 1000, // 1 second
      maxRequests: 100 // 100 orders/second per user
    }));

    // Per-user position limit
    this.limiters.set('user_position', new TokenBucketLimiter({
      capacity: 1000000, // $1M position limit
      fillRate: 0 // Static limit (no refill)
    }));

    // System-wide circuit breaker
    this.limiters.set('system_circuit_breaker', new CircuitBreaker({
      failureThreshold: 0.5, // 50% error rate
      timeout: 30000, // 30 seconds
      resetTimeout: 60000 // 1 minute reset
    }));
  }

  async checkOrderAllowed(userId: string, order: Order): Promise<RiskCheckResult> {
    // Check 1: Order rate limit
    const rateCheck = await this.limiters.get('user_orders').consume(userId, 1);
    if (!rateCheck.allowed) {
      return {
        allowed: false,
        reason: 'RATE_LIMIT_EXCEEDED',
        retryAfter: rateCheck.retryAfter
      };
    }

    // Check 2: Position limit
    const currentPosition = await this.getPositionValue(userId);
    const orderValue = order.quantity * order.price;

    if (currentPosition + orderValue > 1000000) {
      return {
        allowed: false,
        reason: 'POSITION_LIMIT_EXCEEDED',
        currentPosition,
        limit: 1000000
      };
    }

    // Check 3: System circuit breaker
    const systemCheck = await this.limiters.get('system_circuit_breaker').check();
    if (systemCheck.state === 'OPEN') {
      return {
        allowed: false,
        reason: 'SYSTEM_CIRCUIT_BREAKER_OPEN',
        message: 'Trading temporarily halted due to system errors'
      };
    }

    return { allowed: true };
  }
}
```

**Results**:
- ✅ Risk incidents: 0 (from 5/month)
- ✅ Position violations: 0
- ✅ System protection: Auto-halt on errors

**Cost Impact**:
- Redis for rate limiting: $150/mo
- **Total: $150/mo**

### 📈 Combined Results: Trading System

#### Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Order execution** | 50ms | 3ms | **17x faster** |
| **Audit completeness** | 60% | 100% | **Full compliance** |
| **Message loss** | 0.1% | 0% | **Zero loss** |
| **Risk violations** | 5/month | 0 | **100% prevention** |

#### Cost Analysis

| Component | Monthly Cost |
|-----------|--------------|
| Event sourcing | $2,000 |
| Message queue | $1,000 |
| Rate limiting | $150 |
| Cache tier | $500 |
| Distributed tracing | $300 |
| **Total Infrastructure** | **$3,950** |

#### Business Impact

- **Compliance fines avoided**: $50M/year potential
- **Trading volume increase**: +40% (due to faster execution)
- **Risk incidents avoided**: $2M/year potential losses

---

## Pattern Composition Cheat Sheet

### Quick Reference: Pattern Combinations

| Business Need | Pattern Combination | Expected Benefit |
|---------------|---------------------|------------------|
| **Fast reads + writes** | Cache (01) + CDC (13) | 50x read speed + real-time sync |
| **Real-time analytics** | Stream (02) + TimeSeries (08) + OLAP (17) | <1s latency + deep analysis |
| **Scalable API** | Gateway (04) + Cache (09) + Rate Limiter (11) | High throughput + protection |
| **ML at scale** | Recommendations (14) + Feature Store (16) + Cache (01) | Fast inference + consistency |
| **Search + discovery** | Search (15) + Recommendations (14) + Cache (09) | <50ms + personalization |
| **Compliance + audit** | Event Sourcing (07) + Message Queue (10) | 100% trail + zero loss |
| **IoT/telemetry** | Stream (02) + TimeSeries (08) + Probabilistic (19) | Real-time + efficient storage |
| **High reliability** | Message Queue (10) + Rate Limiter (11) + Circuit Breaker | 99.99% uptime |

### Anti-patterns: What NOT to Combine

| ❌ Bad Combination | Why It's Bad | ✅ Better Alternative |
|-------------------|--------------|----------------------|
| Cache (01) + Event Sourcing (07) | Cache invalidation nightmare | Use CDC (13) for cache updates |
| OLAP (17) + Real-time writes | OLAP optimized for reads | Stream (02) → OLAP for writes |
| Probabilistic (19) for exact counts | Inherent ±0.81% error | Use exact counting for critical metrics |
| Rate Limiter (11) everywhere | Adds latency to every request | Only at entry points |
| Search (15) as primary database | Not designed for transactional writes | Use DB + Search index |

---

## Implementation Roadmap Templates

### Template 1: MVP → Production (12 weeks)

**Week 1-2: Foundation**
- Set up infrastructure (cloud accounts, networking)
- Deploy monitoring & alerting (App 18: Distributed Tracing)
- Implement core caching (App 01: LRU Cache)

**Week 3-4: Core Features**
- Build primary data pipeline (App 02: Stream Processing OR App 10: Message Queue)
- Implement database strategy (App 08: TimeSeries OR standard RDBMS)
- Add rate limiting (App 11: Rate Limiter)

**Week 5-8: Advanced Features**
- Add analytics (App 17: OLAP) OR search (App 15: Search Engine)
- Implement personalization (App 14: Recommendations)
- Build CDC pipeline (App 13: CDC)

**Week 9-10: Optimization**
- Tune cache strategies (App 09: Multi-tier Cache)
- Optimize queries and indexes
- Load testing & performance tuning

**Week 11-12: Launch Prep**
- Security audit
- Compliance review (App 07: Event Sourcing if needed)
- Production deployment

### Template 2: Modernization (Lift & Shift → Cloud Native)

**Phase 1: Observe (Weeks 1-2)**
- Deploy App 18 (Distributed Tracing) on existing system
- Identify bottlenecks
- Measure current performance baselines

**Phase 2: Cache Layer (Weeks 3-4)**
- Add App 01 (LRU Cache) in front of database
- Reduce database load by 70-80%
- Measure cost savings

**Phase 3: Async Processing (Weeks 5-8)**
- Introduce App 10 (Message Queue) for background jobs
- Decouple synchronous dependencies
- Improve user-facing latency

**Phase 4: Data Pipeline (Weeks 9-12)**
- Replace batch ETL with App 02 (Stream Processing)
- Real-time analytics instead of overnight reports
- Reduce data freshness from hours to seconds

**Phase 5: Advanced Features (Weeks 13-16)**
- Add App 14 (Recommendations) for personalization
- Add App 15 (Search Engine) for fast lookups
- Implement App 13 (CDC) for data synchronization

---

## Summary: The Power of Composition

### Key Principles

1. **Start Simple**: Begin with 2-3 patterns (Cache + Rate Limiter + Monitoring)
2. **Measure First**: Deploy tracing (App 18) before optimization
3. **Compose Gradually**: Add patterns as needs arise, not speculatively
4. **Cost-Conscious**: Most powerful combinations cost <$50K/month
5. **ROI-Driven**: Each pattern should have clear business justification

### Success Metrics

Track these metrics to validate pattern effectiveness:

| Metric | Target | Indicates Success For |
|--------|--------|----------------------|
| Cache hit rate | >80% | App 01, 09 |
| Stream processing latency | <1s | App 02, 06, 12 |
| Search query time | <100ms | App 15 |
| Message delivery rate | 99.99% | App 10 |
| Recommendation CTR | >5% | App 14 |
| Storage cost/GB | <$1 | App 08, 17 |
| Anomaly detection time | <5min | App 17, 19 |

### Next Steps

1. **Identify Your Primary Challenge**: Use the decision tree in ARCHITECTURAL_CONCEPTS.md
2. **Select 2-3 Starter Patterns**: Keep it simple initially
3. **Implement with Monitoring**: Deploy App 18 first
4. **Measure & Iterate**: Track success metrics
5. **Expand Gradually**: Add patterns based on measured needs

---

**Questions? Ready to start composing?**

Refer to:
- `ARCHITECTURAL_CONCEPTS.md` for detailed pattern explanations
- `DESIGN_SYSTEM.md` for frontend component library
- Individual app READMEs for implementation details
