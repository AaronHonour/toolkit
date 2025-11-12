# Observability Stack

Production-ready monitoring, logging, and tracing for Unistax.

## Quick Start

```bash
# Start full stack with observability
make dev

# Access dashboards
open http://localhost:3001  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
open http://localhost:16686 # Jaeger tracing
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Applications (19 services)            │
│  Expose /metrics, emit logs, send traces                │
└──────┬──────────────────────┬──────────────────┬────────┘
       │                      │                  │
       │ Metrics              │ Logs             │ Traces
       ▼                      ▼                  ▼
┌─────────────┐      ┌─────────────┐    ┌──────────────┐
│ Prometheus  │      │    Loki     │    │   Jaeger     │
│ (Metrics)   │      │ (Logs)      │    │  (Traces)    │
└──────┬──────┘      └──────┬──────┘    └───────┬──────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                      ┌─────▼──────┐
                      │  Grafana   │
                      │ (Visualize)│
                      └────────────┘
```

## Components

### 1. Prometheus - Metrics Collection

**Port**: 9090
**Purpose**: Scrape and store time-series metrics

**What it monitors**:
- Request rate (RPS)
- Error rate
- Latency (p50, p95, p99)
- Resource usage (CPU, memory)
- Database connections
- Cache hit rates
- Queue depths

**Configuration**: `observability/prometheus/prometheus.yml`

```yaml
# Metrics exposed by each service
http_requests_total          # Total HTTP requests
http_request_duration_seconds # Request latency
http_requests_in_flight      # Active requests
cache_hits_total            # Cache hits
cache_misses_total          # Cache misses
queue_depth                 # Items in queue
db_connection_pool_active   # Active DB connections
```

**Accessing**:
```bash
# Prometheus UI
open http://localhost:9090

# Query examples
http_requests_total                                    # All requests
rate(http_requests_total[1m])                         # Request rate
histogram_quantile(0.95, http_request_duration_seconds_bucket)  # P95 latency
```

---

### 2. Grafana - Visualization

**Port**: 3001
**Credentials**: admin / admin
**Purpose**: Visualize metrics, logs, and traces

**Pre-configured Dashboards**:
1. **Overview** - System-wide health
2. **Service Details** - Per-service metrics
3. **Infrastructure** - PostgreSQL, Redis, Kafka
4. **SLO Dashboard** - Service Level Objectives

**Features**:
- Real-time dashboards
- Alert visualization
- Log exploration (via Loki)
- Trace viewing (via Jaeger)
- Custom queries

**Accessing**:
```bash
open http://localhost:3001
# Login: admin / admin
```

---

### 3. Jaeger - Distributed Tracing

**Port**: 16686
**Purpose**: Trace requests across services

**What it shows**:
- Request flow through microservices
- Service dependencies
- Latency breakdown per service
- Error propagation
- Database query timing

**Example Trace**:
```
GET /api/orders/123
  → app04-gateway (5ms)
    → app01-inventory (15ms)
      → PostgreSQL query (12ms)
    → app05-export (8ms)
      → Redis get (1ms)
Total: 28ms
```

**Accessing**:
```bash
open http://localhost:16686
# Search for traces by service, operation, or tags
```

---

### 4. Loki - Log Aggregation

**Port**: 3100
**Purpose**: Centralized log collection

**Log Sources**:
- Application logs (stdout/stderr)
- System logs (/var/log)
- Access logs (nginx)

**Features**:
- Label-based indexing (like Prometheus)
- Full-text search
- Log correlation with metrics/traces
- Log streaming

**Querying** (via Grafana):
```logql
{job="toolkit"} |= "error"           # All error logs
{service="app01-inventory"} | json   # Parse JSON logs
rate({job="toolkit"}[1m])            # Log rate
```

---

### 5. Promtail - Log Shipper

**Purpose**: Ships logs from files to Loki

**Configuration**: `observability/promtail/config.yml`

Automatically collects logs from:
- `/var/log/*.log`
- `/var/log/toolkit/*.log`

---

## Metrics Reference

### RED Metrics (Requests, Errors, Duration)

```promql
# Request Rate
sum(rate(http_requests_total[1m])) by (service)

# Error Rate
sum(rate(http_requests_total{status=~"5.."}[1m])) by (service)
/ sum(rate(http_requests_total[1m])) by (service)

# Duration (p95)
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)
```

### USE Metrics (Utilization, Saturation, Errors)

```promql
# CPU Utilization
rate(process_cpu_seconds_total[1m])

# Memory Utilization
process_resident_memory_bytes / 1024 / 1024 / 1024  # GB

# Connection Pool Saturation
db_connection_pool_active / db_connection_pool_size
```

### Custom Business Metrics

```promql
# Orders per second
rate(orders_total[1m])

# Revenue per second
rate(revenue_total[1m])

# Active users
active_users_gauge

# Cache hit rate
sum(rate(cache_hits_total[1m]))
/ sum(rate(cache_requests_total[1m]))
```

---

## Alerting

### Alert Rules

Located in: `observability/prometheus/rules/alerts.yml`

**Critical Alerts**:
- `HighErrorRate`: Error rate > 5% for 5 minutes
- `ServiceDown`: Service unavailable for 2 minutes
- `SLOAvailabilityBreach`: Availability < 99.9%
- `PostgreSQLDown`: Database unavailable
- `RedisDown`: Cache unavailable

**Warning Alerts**:
- `HighLatency`: p95 > 1 second for 10 minutes
- `HighMemoryUsage`: Memory > 1GB for 10 minutes
- `LowCacheHitRate`: Hit rate < 50% for 15 minutes
- `QueueDepthGrowing`: Queue growing > 10 items/sec
- `DiskSpaceLow`: Disk space < 10%

### Alert Testing

```bash
# Trigger high error rate
for i in {1..1000}; do
  curl http://localhost:8001/simulate-error
done

# Check alerts in Prometheus
open http://localhost:9090/alerts

# View in Grafana
open http://localhost:3001/alerting/list
```

---

## Service Level Objectives (SLOs)

### Availability SLO: 99.9%

```promql
# Current availability (30-day window)
sum(rate(http_requests_total{status!~"5.."}[30d]))
/ sum(rate(http_requests_total[30d]))
```

**Budget**: 43.2 minutes downtime per month

### Latency SLO: p95 < 100ms

```promql
# P95 latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[10m])) by (le)
)
```

### Error Rate SLO: < 0.1%

```promql
# Error rate
sum(rate(http_requests_total{status=~"5.."}[1h]))
/ sum(rate(http_requests_total[1h]))
```

---

## Instrumenting Your Code

### Adding Metrics (Python)

```python
from prometheus_client import Counter, Histogram, Gauge
from fastapi import FastAPI

app = FastAPI()

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    # Track request
    with request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).time():
        response = await call_next(request)

    # Count request
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    return response

# Expose metrics endpoint
from prometheus_client import generate_latest

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Adding Tracing

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracer
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Use in code
@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("order.id", order_id)

        # Database query
        with tracer.start_as_current_span("db.query"):
            order = await db.get_order(order_id)

        # Cache check
        with tracer.start_as_current_span("cache.check"):
            cached = await cache.get(f"order:{order_id}")

        return order
```

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "app01-inventory",
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None),
        }
        return json.dumps(log_data)

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use in code
logger.info("Order created", extra={
    "order_id": order.id,
    "user_id": user.id,
    "amount": order.total
})
```

---

## Dashboards

### Overview Dashboard

**Panels**:
1. Total RPS (stat)
2. Active Services (stat)
3. Request Rate by Service (graph)
4. Error Rate (graph)
5. P95 Latency (graph)
6. Cache Hit Rate (graph)
7. Queue Depth (graph)
8. Database Connections (graph)
9. Memory Usage (graph)

**Refresh**: 10 seconds

### Service Detail Dashboard

Per-service deep dive:
- Request rate
- Error breakdown by status code
- Latency percentiles (p50, p90, p95, p99)
- Top slow endpoints
- Database query performance
- Cache statistics

### Infrastructure Dashboard

- PostgreSQL: Connections, queries/sec, cache hit ratio
- Redis: Commands/sec, memory usage, evictions
- Kafka: Messages/sec, lag, partition distribution
- System: CPU, memory, disk, network

---

## Troubleshooting

### No Metrics Appearing

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check if services expose /metrics
curl http://localhost:8001/metrics

# View Prometheus logs
docker logs toolkit-prometheus

# Verify network connectivity
docker exec toolkit-prometheus ping app01-inventory
```

### Grafana Can't Connect to Prometheus

```bash
# Check Grafana datasource
curl http://localhost:3001/api/datasources

# Test Prometheus from Grafana container
docker exec toolkit-grafana curl http://prometheus:9090/api/v1/query?query=up

# View Grafana logs
docker logs toolkit-grafana
```

### No Traces in Jaeger

```bash
# Check Jaeger is receiving spans
curl http://localhost:14269/metrics | grep spans

# View Jaeger logs
docker logs toolkit-jaeger

# Verify tracer configuration in app
# Ensure: JAEGER_AGENT_HOST=jaeger, JAEGER_AGENT_PORT=6831
```

### Logs Not Appearing in Loki

```bash
# Check Loki is running
curl http://localhost:3100/ready

# Check Promtail is shipping logs
curl http://localhost:9080/metrics | grep promtail

# View Promtail logs
docker logs toolkit-promtail

# Query Loki directly
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="toolkit"}'
```

---

## Performance Impact

### Metrics Collection

- **CPU overhead**: < 1% per service
- **Memory overhead**: ~10-20MB per service
- **Network**: ~1KB/sec per metric

### Tracing

- **Sampling rate**: 10% (configurable)
- **CPU overhead**: < 2% when sampled
- **Storage**: ~1KB per trace

### Logging

- **CPU overhead**: Minimal (async)
- **Disk I/O**: Depends on log volume
- **Network**: Compressed, ~50% reduction

**Recommendation**: For production, adjust sampling rates based on traffic volume.

---

## Best Practices

### 1. Metric Naming

```
# Good
http_requests_total
http_request_duration_seconds
db_connection_pool_active

# Bad
requests  # Too generic
request_time_ms  # Use seconds
connections_count  # Redundant suffix
```

### 2. Label Cardinality

```python
# Good - Low cardinality
labels=['method', 'endpoint', 'status']  # ~100s of combinations

# Bad - High cardinality
labels=['user_id', 'order_id']  # Millions of combinations
```

### 3. Dashboard Organization

- Overview → Service → Infrastructure
- RED metrics prominently displayed
- Time range selector visible
- Annotations for deployments

### 4. Alert Fatigue

- Set appropriate thresholds
- Use `for:` duration to avoid flapping
- Group related alerts
- Route by severity

---

## Cost Optimization

### Metrics Retention

```yaml
# prometheus.yml
storage:
  tsdb:
    retention.time: 15d  # Keep 15 days
    retention.size: 10GB # Or 10GB max
```

### Log Sampling

```python
# Sample 10% of debug logs in production
if os.getenv("ENV") == "production":
    if random.random() < 0.1:
        logger.debug("Debug message")
```

### Trace Sampling

```python
# Sample 10% of traces
sampler = TraceIdRatioBased(0.1)
```

---

## Production Checklist

- [ ] Prometheus has persistent storage
- [ ] Grafana has authentication enabled
- [ ] Alert rules configured
- [ ] Alertmanager routing set up
- [ ] Retention policies defined
- [ ] Backup strategy for metrics
- [ ] Runbooks for common alerts
- [ ] SLO dashboards created
- [ ] Team training on dashboards
- [ ] On-call rotation defined

---

## Additional Resources

- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **Jaeger**: https://www.jaegertracing.io/docs/
- **Loki**: https://grafana.com/docs/loki/
- **OpenTelemetry**: https://opentelemetry.io/docs/

---

**Phase 2.3: Observability Stack** ✓ Complete

Next: Phase 3 - Developer Experience Excellence
