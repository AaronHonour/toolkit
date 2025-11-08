# OpenAPI 3.0 Specifications

This directory contains comprehensive OpenAPI 3.0 specifications for all 19 backend services in the toolkit project.

## Overview

Each service has a production-ready OpenAPI specification including:
- Detailed endpoint documentation
- Request/response schemas with examples
- Authentication and authorization (JWT)
- Rate limiting headers
- Error response formats
- Pagination patterns
- Comprehensive data validation

## API Specifications

### Core Services

#### 01. Inventory Management API
**File**: [`app01-inventory.yaml`](./app01-inventory.yaml)
**Port**: 8001
**Description**: RESTful API for product inventory management with CRUD operations, pagination, filtering, and stock tracking.

**Key Features**:
- Full CRUD operations for products
- Advanced filtering and search
- Stock level management
- Low stock alerts
- Bulk operations

---

#### 02. Analytics Engine API
**File**: [`app02-analytics.yaml`](./app02-analytics.yaml)
**Port**: 8002
**Description**: Real-time analytics with event tracking, metrics computation, and funnel analysis.

**Key Features**:
- Event ingestion (batch and single)
- Time-series aggregations
- Funnel analysis
- Cohort analysis
- Real-time metrics

---

#### 03. File Processor API
**File**: [`app03-file-processor.yaml`](./app03-file-processor.yaml)
**Port**: 8003
**Description**: File upload, processing, and transformation with async job management.

**Key Features**:
- Multi-part file uploads
- Format conversion
- Image processing
- Async job tracking
- Webhook notifications

---

#### 04. API Gateway
**File**: [`app04-api-gateway.yaml`](./app04-api-gateway.yaml)
**Port**: 8004
**Description**: Centralized gateway with authentication, rate limiting, and request routing.

**Key Features**:
- JWT authentication
- API key management
- Rate limiting per user/IP
- Request routing
- Response caching

---

#### 05. Data Export API
**File**: [`app05-data-export.yaml`](./app05-data-export.yaml)
**Port**: 8005
**Description**: Large-scale data export with multiple formats and scheduled exports.

**Key Features**:
- Export to CSV, JSON, Parquet, Avro
- Streaming exports
- Export templates
- Scheduled exports
- Compression support

---

### Stream Processing

#### 06. Kappa Architecture Monitor API
**File**: [`app06-kappa-monitor.yaml`](./app06-kappa-monitor.yaml)
**Port**: 8006
**Description**: Real-time stream processing monitor with Kafka topic visualization.

**Key Features**:
- Kafka topic monitoring
- Consumer group lag tracking
- Stream processor health
- Event replay
- Throughput metrics

---

#### 07. Event Sourcing API
**File**: [`app07-event-sourcing.yaml`](./app07-event-sourcing.yaml)
**Port**: 8007
**Description**: Event sourcing system with event store, aggregates, and projections.

**Key Features**:
- Append-only event log
- Aggregate root management
- Event replay
- Snapshots
- Time-travel queries

---

#### 08. Time-Series Database API
**File**: [`app08-timeseries.yaml`](./app08-timeseries.yaml)
**Port**: 8008
**Description**: High-performance time-series data storage and querying.

**Key Features**:
- 10K+ points/sec ingestion
- Range queries with aggregations
- Downsampling
- Retention policies
- Tags and labels

---

### Data Management

#### 09. Cache Browser API
**File**: [`app09-cache-browser.yaml`](./app09-cache-browser.yaml)
**Port**: 8009
**Description**: Redis cache visualization and management.

**Key Features**:
- Browse keys by pattern
- View/update key values
- TTL management
- Memory analytics
- Batch operations

---

#### 10. Message Queue Monitor API
**File**: [`app10-message-queue.yaml`](./app10-message-queue.yaml)
**Port**: 8010
**Description**: Queue monitoring for RabbitMQ/Kafka with dead letter handling.

**Key Features**:
- Queue depth monitoring
- Non-destructive message browsing
- Dead letter queue management
- Consumer lag tracking
- Performance metrics

---

#### 11. Rate Limiter Dashboard API
**File**: [`app11-rate-limiter.yaml`](./app11-rate-limiter.yaml)
**Port**: 8011
**Description**: Rate limiting visualization and quota management.

**Key Features**:
- Token bucket algorithm
- Sliding window algorithm
- Per-user/IP/endpoint limits
- Real-time usage tracking
- Multiple rate limit tiers

---

### Advanced Analytics

#### 12. Lambda Architecture API
**File**: [`app12-lambda-architecture.yaml`](./app12-lambda-architecture.yaml)
**Port**: 8012
**Description**: Unified batch and stream processing with serving layer.

**Key Features**:
- Batch layer (accuracy)
- Speed layer (low latency)
- Unified query interface
- Historical reprocessing
- View merging

---

#### 13. CDC Monitor API
**File**: [`app13-cdc-monitor.yaml`](./app13-cdc-monitor.yaml)
**Port**: 8013
**Description**: Database change data capture with Debezium integration.

**Key Features**:
- Real-time CDC (< 1s latency)
- Multiple database connectors
- Replication lag monitoring
- Change event browsing
- Connector management

---

#### 14. Recommendation Engine API
**File**: [`app14-recommendations.yaml`](./app14-recommendations.yaml)
**Port**: 8014
**Description**: ML-powered recommendations with collaborative filtering.

**Key Features**:
- Collaborative filtering
- Content-based recommendations
- Hybrid models
- Real-time personalization
- Feedback loop

---

#### 15. Full-Text Search API
**File**: [`app15-search.yaml`](./app15-search.yaml)
**Port**: 8015
**Description**: Elasticsearch-powered search with autocomplete and facets.

**Key Features**:
- Full-text search (< 50ms)
- Autocomplete (< 20ms)
- Faceted navigation
- Relevance tuning
- Fuzzy matching

---

### Machine Learning & Data Science

#### 16. ML Feature Store API
**File**: [`app16-feature-store.yaml`](./app16-feature-store.yaml)
**Port**: 8016
**Description**: Feature management for ML pipelines with online/offline serving.

**Key Features**:
- Feature registration
- Online serving (< 10ms)
- Offline retrieval
- Feature lineage
- Point-in-time correctness

---

#### 17. OLAP Analytics Dashboard API
**File**: [`app17-olap-dashboard.yaml`](./app17-olap-dashboard.yaml)
**Port**: 8017
**Description**: Multi-dimensional analytics with OLAP cubes.

**Key Features**:
- OLAP cube queries
- Pivot tables
- Drill-down navigation
- Slice and dice
- Real-time to hourly refresh

---

### Observability

#### 18. Distributed Tracing Viewer API
**File**: [`app18-trace-viewer.yaml`](./app18-trace-viewer.yaml)
**Port**: 8018
**Description**: OpenTelemetry trace visualization with Jaeger.

**Key Features**:
- Trace collection (100K+ spans/sec)
- Span timeline visualization
- Performance profiling
- Service dependency mapping
- Trace search

---

#### 19. Probabilistic Data Structures API
**File**: [`app19-probabilistic.yaml`](./app19-probabilistic.yaml)
**Port**: 8019
**Description**: Space-efficient data structures (Bloom filter, HyperLogLog, Count-Min Sketch).

**Key Features**:
- Bloom filters (< 1% FP rate)
- HyperLogLog (< 2% error)
- Count-Min Sketch
- 90%+ space reduction
- O(1) query time

---

## Usage

### Viewing Specifications

You can view these OpenAPI specs using:

1. **Swagger UI**: Import the YAML files into [Swagger Editor](https://editor.swagger.io/)
2. **Redoc**: Use [Redoc](https://redocly.github.io/redoc/) for beautiful API documentation
3. **Postman**: Import directly into Postman for API testing
4. **OpenAPI Generator**: Generate client SDKs in multiple languages

### Example: Loading in Swagger Editor

```bash
# Using Swagger UI Docker
docker run -p 8080:8080 -e SWAGGER_JSON=/openapi/app01-inventory.yaml \
  -v $(pwd):/openapi swaggerapi/swagger-ui

# Access at http://localhost:8080
```

### Generating Client SDKs

```bash
# Generate Python client
openapi-generator-cli generate \
  -i app01-inventory.yaml \
  -g python \
  -o ./clients/python/inventory

# Generate TypeScript client
openapi-generator-cli generate \
  -i app01-inventory.yaml \
  -g typescript-fetch \
  -o ./clients/typescript/inventory
```

## Authentication

All APIs (except health endpoints) require JWT authentication:

```http
Authorization: Bearer <your-jwt-token>
```

Obtain tokens via the API Gateway authentication endpoints.

## Rate Limiting

All APIs implement rate limiting with the following headers:

- `X-RateLimit-Limit`: Request limit per hour
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time (Unix timestamp)

## Common Response Codes

- **200**: Success
- **201**: Resource created
- **204**: Success with no content
- **400**: Bad request
- **401**: Unauthorized
- **404**: Not found
- **429**: Rate limit exceeded
- **500**: Internal server error

## Support

For questions or issues:
- Email: api@toolkit.example.com
- Documentation: See individual pattern documentation in `/docs/patterns/`

---

**Last Updated**: 2024-01-22
**OpenAPI Version**: 3.0.3
**Total APIs**: 19
