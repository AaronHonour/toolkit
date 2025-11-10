# Scaling Guide

Comprehensive guide for scaling Composable Toolkit applications from prototype to enterprise scale (100K - 10M+ requests/day).

## Table of Contents

- [Quick Reference](#quick-reference)
- [Horizontal Scaling](#horizontal-scaling)
- [Vertical Scaling](#vertical-scaling)
- [Reference Architectures](#reference-architectures)
- [Microservices Architecture](#microservices-architecture)
- [Event-Driven Architecture](#event-driven-architecture)
- [Database Scaling](#database-scaling)
- [Caching Strategies](#caching-strategies)
- [Load Balancing](#load-balancing)
- [Monitoring & Auto-Scaling](#monitoring--auto-scaling)

---

## Quick Reference

| Traffic Level | Architecture | Scaling Strategy | Example Setup |
|--------------|--------------|------------------|---------------|
| **< 100K req/day** | Single server | Vertical scaling | 1 app server, 1 DB |
| **100K - 1M req/day** | Load balanced | Horizontal + Caching | 3-5 app servers, Redis, DB replica |
| **1M - 10M req/day** | Microservices | Horizontal + Sharding | 10-20 services, distributed cache, DB cluster |
| **10M+ req/day** | Distributed | Full horizontal + CDN | 50+ services, multi-region, event streaming |

---

## Horizontal Scaling

Horizontal scaling adds more instances of your application to handle increased load.

### When to Scale Horizontally

✅ **Scale horizontally when:**
- CPU usage consistently > 70%
- Request latency increasing
- Queue depths growing
- Need fault tolerance
- Traffic is spiky/unpredictable

❌ **Don't scale horizontally when:**
- Single-threaded bottleneck
- Database is the bottleneck
- Memory-bound operations
- State synchronization issues

### Stateless Application Design

```python
# ❌ BAD: Storing state in memory
class UserSession:
    sessions = {}  # Shared state - won't work across instances!

    def store_session(self, user_id, data):
        self.sessions[user_id] = data

# ✅ GOOD: Storing state in distributed cache
from toolkit.cache import CacheManager

class UserSession:
    def __init__(self):
        self.cache = CacheManager(backend="redis")

    def store_session(self, user_id, data):
        self.cache.set(f"session:{user_id}", data, ttl=3600)

    def get_session(self, user_id):
        return self.cache.get(f"session:{user_id}")
```

### Load Balancing Configuration

#### Nginx Load Balancer

```nginx
upstream backend {
    # Load balancing method
    least_conn;  # Route to server with fewest connections

    # Backend servers
    server app1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server app2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server app3:8000 weight=1 max_fails=3 fail_timeout=30s;

    # Health checks
    check interval=3000 rise=2 fall=3 timeout=1000;

    # Sticky sessions (if needed)
    # ip_hash;  # Same client → same server
}

server {
    listen 80;

    location / {
        proxy_pass http://backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        # Connection settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

#### Docker Compose with Multiple Instances

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

  app:
    build: .
    deploy:
      replicas: 5  # Run 5 instances
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    environment:
      REDIS_URL: redis://redis:6379
      DATABASE_URL: postgresql://postgres:5432/mydb
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

#### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: toolkit-app
spec:
  replicas: 5  # Start with 5 pods
  selector:
    matchLabels:
      app: toolkit-app
  template:
    metadata:
      labels:
        app: toolkit-app
    spec:
      containers:
      - name: app
        image: toolkit-app:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: toolkit-app-service
spec:
  type: LoadBalancer
  selector:
    app: toolkit-app
  ports:
  - port: 80
    targetPort: 8000

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: toolkit-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: toolkit-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Session Management at Scale

#### Redis-based Sessions

```python
from toolkit.cache import CacheManager
from fastapi import FastAPI, Request, Response
import uuid

app = FastAPI()
cache = CacheManager(backend="redis", url="redis://redis:6379")

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Get or create session ID
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    # Attach session to request
    request.state.session_id = session_id
    request.state.session = cache.get(f"session:{session_id}") or {}

    response = await call_next(request)

    # Save session
    cache.set(f"session:{session_id}", request.state.session, ttl=3600)
    response.set_cookie("session_id", session_id, httponly=True, secure=True)

    return response
```

---

## Vertical Scaling

Vertical scaling increases resources (CPU, RAM) on existing servers.

### When to Scale Vertically

✅ **Scale vertically when:**
- Database performance bottleneck
- Memory-intensive operations
- Single-threaded workloads
- Simpler than horizontal scaling
- Lower operational complexity

❌ **Don't scale vertically when:**
- Already at instance size limits
- Need fault tolerance
- Cost per unit performance is high
- Application can scale horizontally

### Vertical Scaling Limits

| Resource | Small | Medium | Large | XLarge | Maximum |
|----------|-------|--------|-------|--------|---------|
| **CPU** | 2 cores | 8 cores | 32 cores | 64 cores | 96 cores |
| **RAM** | 4 GB | 16 GB | 64 GB | 256 GB | 1 TB+ |
| **RPS** | ~5K | ~20K | ~80K | ~150K | ~200K |
| **Cost** | $50/mo | $200/mo | $800/mo | $3K/mo | $10K+/mo |

**Diminishing Returns:**
- 2 cores → 4 cores: ~1.8x improvement
- 4 cores → 8 cores: ~1.6x improvement
- 8 cores → 16 cores: ~1.4x improvement
- 16 cores → 32 cores: ~1.2x improvement

**Sweet Spot:** 8-16 cores for most workloads

### Optimizing for Vertical Scale

#### Worker Configuration

```python
# gunicorn.conf.py
import multiprocessing

# Workers = (2 x CPU cores) + 1
workers = (multiprocessing.cpu_count() * 2) + 1

# Worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Threads per worker (for I/O bound)
threads = 4

# Worker connections (for async)
worker_connections = 1000

# Timeout
timeout = 120
graceful_timeout = 30

# Memory limits
max_requests = 10000  # Restart worker after N requests
max_requests_jitter = 1000  # Add randomness to avoid thundering herd
```

#### Database Connection Pooling

```python
from toolkit.database import DatabaseManager

# Connection pool sized for workers
db = DatabaseManager(
    url="postgresql://localhost/mydb",
    pool_size=20,  # Base connections
    max_overflow=10,  # Extra connections during spikes
    pool_timeout=30,  # Wait timeout
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connection before use
)
```

---

## Reference Architectures

### Prototype: < 100K requests/day (~1 RPS)

**Use Case:** MVP, POC, internal tools

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Single     │
│  App Server │  (2 CPU, 4GB RAM)
│  (FastAPI)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PostgreSQL │  (2 CPU, 8GB RAM)
└─────────────┘
```

**Specs:**
- 1 application server
- 1 database server
- No caching
- No load balancer

**Cost:** ~$100/month

**Implementation:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: password

volumes:
  pgdata:
```

---

### Startup: 100K - 1M requests/day (~10-12 RPS)

**Use Case:** Growing SaaS, active user base

```
        ┌─────────────┐
        │     CDN     │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │    Nginx    │  Load Balancer
        └──────┬──────┘
               │
     ┌─────────┼─────────┐
     ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│  App 1 │ │  App 2 │ │  App 3 │  (4 CPU, 8GB RAM each)
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┼──────────┘
               │
     ┌─────────┼─────────┐
     ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌──────────┐
│  Redis  │ │Postgres │ │Postgres  │
│  Cache  │ │ Primary │ │ Replica  │
└─────────┘ └─────────┘ └──────────┘
```

**Specs:**
- 3-5 application servers
- 1 PostgreSQL primary + 1 replica
- 1 Redis cache
- CDN for static assets
- Nginx load balancer

**Cost:** ~$500-800/month

**Configuration:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

  app:
    build: .
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      DATABASE_URL: postgresql://db-primary:5432/mydb
      REDIS_URL: redis://redis:6379
      READ_DATABASE_URL: postgresql://db-replica:5432/mydb

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data

  db-primary:
    image: postgres:15-alpine
    volumes:
      - db-primary-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: password
      # Replication setup
      POSTGRES_REPLICATION_MODE: master

  db-replica:
    image: postgres:15-alpine
    volumes:
      - db-replica-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: password
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_SERVICE: db-primary

volumes:
  redis-data:
  db-primary-data:
  db-replica-data:
```

---

### Growth: 1M - 10M requests/day (~12-120 RPS)

**Use Case:** Established SaaS, significant user base

```
              ┌─────────┐
              │   CDN   │
              └────┬────┘
                   │
         ┌─────────▼─────────┐
         │  Load Balancer    │  (AWS ALB / GCP LB)
         └─────────┬─────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ API    │ │ Worker │ │Admin   │  (Microservices)
   │Gateway │ │Service │ │Service │
   └───┬────┘ └───┬────┘ └───┬────┘
       │          │          │
       └──────────┼──────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Redis   │  │Postgres │  │  Kafka  │
│ Cluster │  │ Cluster │  │Streaming│
│(3 nodes)│  │(1P + 2R)│  │         │
└─────────┘  └─────────┘  └─────────┘
```

**Specs:**
- 10-20 microservices (auto-scaling)
- PostgreSQL cluster (1 primary, 2 replicas)
- Redis cluster (3 nodes)
- Kafka for event streaming
- Multi-region deployment

**Cost:** ~$2,000-5,000/month

---

### Enterprise: 10M+ requests/day (~120+ RPS)

**Use Case:** Large-scale SaaS, millions of users

```
                    ┌──────────┐
                    │Global CDN│
                    └─────┬────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
    ┌─────▼─────┐                  ┌──────▼──────┐
    │  Region 1 │                  │  Region 2   │
    │   (US)    │                  │   (EU)      │
    └─────┬─────┘                  └──────┬──────┘
          │                               │
    ┌─────▼──────────────┐         ┌─────▼──────────────┐
    │  Load Balancer     │         │  Load Balancer     │
    └─────┬──────────────┘         └─────┬──────────────┘
          │                               │
    ┌─────┼─────┐                   ┌─────┼─────┐
    ▼     ▼     ▼                   ▼     ▼     ▼
┌──────┐ ... ┌──────┐          ┌──────┐ ... ┌──────┐
│ Pod1 │     │ PodN │          │ Pod1 │     │ PodN │
│(K8s) │     │(K8s) │          │(K8s) │     │(K8s) │
└──┬───┘     └──┬───┘          └──┬───┘     └──┬───┘
   │            │                 │            │
   └────────────┼─────────────────┴────────────┘
                │
         ┌──────┼──────┐
         ▼      ▼      ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Redis  │ │Postgres│ │ Kafka  │
    │Cluster │ │Cluster │ │Cluster │
    │Multi-AZ│ │Multi-AZ│ │Multi-AZ│
    └────────┘ └────────┘ └────────┘
```

**Specs:**
- 50+ microservices across regions
- Kubernetes with auto-scaling (3-100+ pods per service)
- Multi-region PostgreSQL (active-active or primary-replica)
- Redis Cluster (6+ nodes, multi-AZ)
- Kafka Cluster (3+ brokers, multi-AZ)
- Service mesh (Istio/Linkerd)
- Observability stack (Prometheus, Grafana, Jaeger)

**Cost:** ~$10,000-50,000+/month

---

## Microservices Architecture

### Service Decomposition

```python
# Monolith → Microservices Migration

# Before: Monolithic application
class EcommerceApp:
    def create_order(self, user_id, items):
        # User validation
        user = self.users.get(user_id)

        # Inventory check
        for item in items:
            if not self.inventory.check_availability(item):
                raise OutOfStock()

        # Payment processing
        payment = self.payments.charge(user, total)

        # Order creation
        order = self.orders.create(user, items, payment)

        # Notification
        self.notifications.send_email(user, order)

        return order


# After: Microservices

# User Service
class UserService:
    async def get_user(self, user_id):
        return await self.db.users.find_one({"id": user_id})


# Inventory Service
class InventoryService:
    async def check_availability(self, item_id, quantity):
        stock = await self.db.inventory.find_one({"item_id": item_id})
        return stock["quantity"] >= quantity


# Payment Service
class PaymentService:
    async def charge(self, user_id, amount):
        # Process payment
        result = await stripe.charge(amount)
        await self.db.payments.insert_one(result)
        return result


# Order Service (Orchestrator)
class OrderService:
    def __init__(self):
        self.user_service = UserServiceClient()
        self.inventory_service = InventoryServiceClient()
        self.payment_service = PaymentServiceClient()
        self.notification_service = NotificationServiceClient()

    async def create_order(self, user_id, items):
        # Call user service
        user = await self.user_service.get_user(user_id)

        # Call inventory service
        for item in items:
            available = await self.inventory_service.check_availability(
                item["id"], item["quantity"]
            )
            if not available:
                raise OutOfStock(item["id"])

        # Call payment service
        payment = await self.payment_service.charge(user_id, total)

        # Create order
        order = await self.db.orders.insert_one({
            "user_id": user_id,
            "items": items,
            "payment_id": payment["id"],
            "status": "pending"
        })

        # Async notification (fire and forget)
        await self.notification_service.send_order_confirmation(user_id, order["id"])

        return order
```

### Service Communication Patterns

#### Synchronous (REST/gRPC)

```python
from toolkit.http import HTTPClient

class UserServiceClient:
    def __init__(self):
        self.client = HTTPClient(base_url="http://user-service:8001")

    async def get_user(self, user_id: str):
        response = await self.client.get(f"/users/{user_id}")
        return response.json()
```

#### Asynchronous (Message Queue)

```python
from toolkit.queue import QueueManager

class OrderService:
    def __init__(self):
        self.queue = QueueManager(backend="kafka")

    async def create_order(self, user_id, items):
        # Create order
        order = await self.save_order(user_id, items)

        # Publish event (async)
        await self.queue.publish(
            topic="orders.created",
            message={
                "order_id": order["id"],
                "user_id": user_id,
                "items": items,
                "timestamp": datetime.utcnow()
            }
        )

        return order


class NotificationService:
    def __init__(self):
        self.queue = QueueManager(backend="kafka")

    async def start_listener(self):
        # Subscribe to order events
        await self.queue.subscribe(
            topic="orders.created",
            callback=self.send_notification
        )

    async def send_notification(self, message):
        order_id = message["order_id"]
        user_id = message["user_id"]

        # Send email
        await self.email_service.send(user_id, f"Order {order_id} confirmed!")
```

---

## Event-Driven Architecture

### Event Sourcing Pattern

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Event:
    """Base event class."""
    event_id: str
    event_type: str
    timestamp: datetime
    data: dict


class OrderAggregate:
    """Order aggregate root with event sourcing."""

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.events: List[Event] = []
        self.state = {
            "status": "new",
            "items": [],
            "total": 0
        }

    def create_order(self, user_id: str, items: List[dict]):
        """Create new order (command)."""
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="OrderCreated",
            timestamp=datetime.utcnow(),
            data={
                "order_id": self.order_id,
                "user_id": user_id,
                "items": items
            }
        )

        self._apply_event(event)
        return event

    def add_payment(self, payment_id: str, amount: float):
        """Add payment (command)."""
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="PaymentAdded",
            timestamp=datetime.utcnow(),
            data={
                "payment_id": payment_id,
                "amount": amount
            }
        )

        self._apply_event(event)
        return event

    def _apply_event(self, event: Event):
        """Apply event to update state."""
        self.events.append(event)

        # Update state based on event type
        if event.event_type == "OrderCreated":
            self.state["status"] = "created"
            self.state["items"] = event.data["items"]

        elif event.event_type == "PaymentAdded":
            self.state["status"] = "paid"
            self.state["total"] = event.data["amount"]

    def rebuild_from_events(self, events: List[Event]):
        """Rebuild aggregate state from event history."""
        for event in events:
            self._apply_event(event)


# Event Store
class EventStore:
    """Store and retrieve events."""

    def __init__(self):
        self.db = DatabaseManager(url="postgresql://...")

    async def save_events(self, aggregate_id: str, events: List[Event]):
        """Save events to store."""
        for event in events:
            await self.db.execute(
                """
                INSERT INTO events (aggregate_id, event_id, event_type, timestamp, data)
                VALUES ($1, $2, $3, $4, $5)
                """,
                aggregate_id,
                event.event_id,
                event.event_type,
                event.timestamp,
                json.dumps(event.data)
            )

    async def get_events(self, aggregate_id: str) -> List[Event]:
        """Retrieve all events for aggregate."""
        rows = await self.db.fetch_all(
            """
            SELECT event_id, event_type, timestamp, data
            FROM events
            WHERE aggregate_id = $1
            ORDER BY timestamp ASC
            """,
            aggregate_id
        )

        return [
            Event(
                event_id=row["event_id"],
                event_type=row["event_type"],
                timestamp=row["timestamp"],
                data=json.loads(row["data"])
            )
            for row in rows
        ]
```

### CQRS (Command Query Responsibility Segregation)

```python
# Write Model (Commands)
class OrderWriteModel:
    """Handles commands (writes)."""

    def __init__(self):
        self.event_store = EventStore()
        self.event_bus = EventBus()

    async def create_order(self, order_id: str, user_id: str, items: List[dict]):
        # Create aggregate
        order = OrderAggregate(order_id)

        # Execute command
        event = order.create_order(user_id, items)

        # Save to event store
        await self.event_store.save_events(order_id, [event])

        # Publish to event bus
        await self.event_bus.publish("OrderCreated", event.data)

        return {"order_id": order_id}


# Read Model (Queries)
class OrderReadModel:
    """Handles queries (reads)."""

    def __init__(self):
        self.db = DatabaseManager(url="postgresql://...")

    async def get_order(self, order_id: str):
        """Get order details (from denormalized view)."""
        return await self.db.fetch_one(
            "SELECT * FROM order_views WHERE order_id = $1",
            order_id
        )

    async def get_user_orders(self, user_id: str):
        """Get all orders for user (optimized query)."""
        return await self.db.fetch_all(
            "SELECT * FROM order_views WHERE user_id = $1 ORDER BY created_at DESC",
            user_id
        )


# Projection (Event → Read Model)
class OrderProjection:
    """Project events into read model."""

    def __init__(self):
        self.db = DatabaseManager(url="postgresql://...")
        self.event_bus = EventBus()

    async def start(self):
        # Subscribe to events
        await self.event_bus.subscribe("OrderCreated", self.on_order_created)
        await self.event_bus.subscribe("PaymentAdded", self.on_payment_added)

    async def on_order_created(self, event_data):
        """Handle OrderCreated event."""
        await self.db.execute(
            """
            INSERT INTO order_views (order_id, user_id, items, status, created_at)
            VALUES ($1, $2, $3, 'created', NOW())
            """,
            event_data["order_id"],
            event_data["user_id"],
            json.dumps(event_data["items"])
        )

    async def on_payment_added(self, event_data):
        """Handle PaymentAdded event."""
        await self.db.execute(
            """
            UPDATE order_views
            SET status = 'paid', payment_id = $2
            WHERE order_id = $1
            """,
            event_data["order_id"],
            event_data["payment_id"]
        )
```

---

## Database Scaling

### Read Replicas

```python
from toolkit.database import DatabaseManager

# Primary for writes
db_primary = DatabaseManager(
    url="postgresql://primary:5432/mydb",
    pool_size=20
)

# Replica for reads
db_replica = DatabaseManager(
    url="postgresql://replica:5432/mydb",
    pool_size=50  # More connections for read-heavy workload
)

# Usage
async def get_user(user_id: str):
    # Read from replica
    return await db_replica.fetch_one(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )

async def create_user(user_data: dict):
    # Write to primary
    return await db_primary.execute(
        "INSERT INTO users (...) VALUES (...)",
        user_data
    )
```

### Sharding

```python
class ShardedDatabase:
    """Database sharding by user ID."""

    def __init__(self):
        # 4 shards
        self.shards = [
            DatabaseManager(url=f"postgresql://shard{i}:5432/mydb")
            for i in range(4)
        ]

    def get_shard(self, user_id: str) -> DatabaseManager:
        """Get shard for user ID."""
        # Hash user ID to shard number
        shard_num = hash(user_id) % len(self.shards)
        return self.shards[shard_num]

    async def get_user(self, user_id: str):
        """Get user from appropriate shard."""
        shard = self.get_shard(user_id)
        return await shard.fetch_one(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )

    async def create_user(self, user_id: str, user_data: dict):
        """Create user in appropriate shard."""
        shard = self.get_shard(user_id)
        return await shard.execute(
            "INSERT INTO users (...) VALUES (...)",
            user_id, user_data
        )
```

---

## Caching Strategies

### Multi-Level Caching

```python
from toolkit.cache import CacheManager
import functools

class MultiLevelCache:
    """L1 (memory) + L2 (Redis) cache."""

    def __init__(self):
        self.l1_cache = {}  # In-memory
        self.l2_cache = CacheManager(backend="redis")

    async def get(self, key: str):
        # Try L1 first (fastest)
        if key in self.l1_cache:
            return self.l1_cache[key]

        # Try L2 (Redis)
        value = await self.l2_cache.get(key)
        if value:
            # Populate L1
            self.l1_cache[key] = value
            return value

        return None

    async def set(self, key: str, value, ttl: int = 3600):
        # Set in both levels
        self.l1_cache[key] = value
        await self.l2_cache.set(key, value, ttl=ttl)


# Cache decorator
def cached(ttl: int = 3600):
    """Cache function results."""
    def decorator(func):
        cache = MultiLevelCache()

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache
            result = await cache.get(key)
            if result is not None:
                return result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Usage
@cached(ttl=600)
async def get_user_profile(user_id: str):
    # Expensive database query
    return await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
```

### Cache Invalidation Patterns

```python
# Time-based (TTL)
cache.set("key", value, ttl=3600)  # Expire after 1 hour

# Event-based
async def update_user(user_id: str, data: dict):
    # Update database
    await db.execute("UPDATE users SET ... WHERE id = $1", user_id, data)

    # Invalidate cache
    await cache.delete(f"user:{user_id}")

# Write-through
async def update_user_write_through(user_id: str, data: dict):
    # Update cache first
    await cache.set(f"user:{user_id}", data)

    # Then update database (async)
    await db.execute("UPDATE users SET ... WHERE id = $1", user_id, data)

# Cache-aside (lazy loading)
async def get_user_cache_aside(user_id: str):
    # Try cache first
    user = await cache.get(f"user:{user_id}")
    if user:
        return user

    # Cache miss - load from DB
    user = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)

    # Populate cache
    await cache.set(f"user:{user_id}", user, ttl=3600)

    return user
```

---

## Load Balancing

### Load Balancing Algorithms

| Algorithm | Use Case | Pros | Cons |
|-----------|----------|------|------|
| **Round Robin** | Equal servers | Simple, fair distribution | Ignores server load |
| **Least Connections** | Varying request times | Adapts to load | More complex |
| **IP Hash** | Sticky sessions | Session affinity | Uneven distribution |
| **Weighted** | Different server specs | Respects capacity | Manual configuration |
| **Random** | Large server pools | Simple, scales well | Less predictable |

### Health Checks

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """Liveness probe - is the app running?"""
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    """Readiness probe - can the app serve traffic?"""
    # Check dependencies
    db_ok = await check_database()
    redis_ok = await check_redis()

    if db_ok and redis_ok:
        return {"status": "ready"}
    else:
        return {"status": "not_ready", "details": {
            "database": db_ok,
            "redis": redis_ok
        }}, 503
```

---

## Monitoring & Auto-Scaling

### Metrics to Monitor

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
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

# System metrics
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

queue_depth = Gauge(
    'queue_depth',
    'Number of items in queue'
)
```

### Auto-Scaling Rules

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  # Scale on CPU
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Scale on memory
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Scale on custom metrics (e.g., queue depth)
  - type: Pods
    pods:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: "100"

  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Scale down max 50% at a time
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Double capacity if needed
        periodSeconds: 30
```

---

## Summary

| Traffic | Architecture | Key Strategies |
|---------|-------------|----------------|
| < 100K/day | Single server | Vertical scaling, basic optimization |
| 100K-1M/day | Load balanced | Horizontal scaling, Redis cache, read replicas |
| 1M-10M/day | Microservices | Service decomposition, distributed cache, sharding |
| 10M+/day | Distributed | Multi-region, event streaming, service mesh |

**Next Steps:**
- Implement observability (Phase 2.3)
- Set up auto-scaling policies
- Create disaster recovery plan
- Optimize database queries
- Implement rate limiting

---

**Phase 2.2: Scalability Guides** ✓ Complete

Next: Phase 2.3 - Observability Stack
