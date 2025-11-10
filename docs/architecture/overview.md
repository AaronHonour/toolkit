# Architecture Overview

The Composable Toolkit is designed with **composability**, **performance**, and **scalability** as core principles. This document provides a high-level overview of the system architecture.

## System Architecture

The toolkit follows a modular, composable architecture where each component can work independently or together.

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React Applications<br/>19 Example Apps]
        B[Atomic Components<br/>Button, Input, Badge]
        C[Performance Hooks<br/>useLRUMemo, useDebounce]
        D[Design Tokens<br/>Colors, Spacing, Typography]
    end

    subgraph "Backend Layer"
        E[Core Modules<br/>Config, Logging, Errors]
        F[Performance Modules<br/>Cache, Rate Limit, Metrics]
        G[Architecture Modules<br/>DI, Events, Repository]
        H[Data Modules<br/>Event Sourcing, TimeSeries]
    end

    subgraph "Infrastructure"
        I[Docker Containers]
        J[CI/CD Pipeline]
        K[Monitoring<br/>Prometheus, Grafana]
    end

    A --> B
    A --> C
    B --> D
    C --> D

    A -.HTTP.-> E
    A -.HTTP.-> F

    E --> G
    F --> G
    G --> H

    E --> I
    F --> I
    H --> I

    I --> J
    I --> K
```

## Component Layers

### 1. Frontend Layer

The frontend is built with **React**, **TypeScript**, and **Vite**, following atomic design principles.

**Components**:
- **Atoms**: Basic UI building blocks (Button, Input, Badge, etc.)
- **Design Tokens**: Centralized design system
- **Performance Hooks**: Optimized React hooks mirroring backend patterns

**Key Principles**:
- 🎯 Atomic Design Pattern
- ⚡ Performance-first (< 1ms render targets)
- 📦 Composable and reusable
- 🎨 Consistent design system

### 2. Backend Layer

The backend is built with **Python 3.10+**, emphasizing composability and performance.

**Modules**:
- **Core**: Foundation modules (Config, Logging, Errors, Environment)
- **Performance**: High-performance utilities (Cache, Rate Limit, Metrics)
- **Architecture**: Enterprise patterns (DI, Events, Repository, Middleware)
- **Data**: Data processing patterns (Event Sourcing, Lambda/Kappa, TimeSeries)

**Key Principles**:
- 🧩 Modular and composable
- ⚡ Performance-optimized (100K+ ops/sec)
- 🔒 Type-safe with full type hints
- ⚙️ Configuration-driven

### 3. Infrastructure Layer

**Docker-First**:
- Multi-stage builds for optimization
- Multi-arch support (amd64, arm64)
- Docker Compose for local development

**CI/CD**:
- Automated testing (90%+ coverage)
- Performance regression detection
- Security scanning
- Automated releases

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant C as Cache
    participant RL as Rate Limiter
    participant DB as Database
    participant E as Event Bus

    U->>F: User Action
    F->>API: HTTP Request
    API->>RL: Check Rate Limit
    RL-->>API: Allowed/Denied

    alt Request Allowed
        API->>C: Check Cache
        alt Cache Hit
            C-->>API: Cached Data
        else Cache Miss
            API->>DB: Query Database
            DB-->>API: Data
            API->>C: Store in Cache
        end

        API->>E: Publish Event
        E-->>API: Event Acknowledged

        API-->>F: Response
        F-->>U: Update UI
    else Request Denied
        API-->>F: 429 Too Many Requests
        F-->>U: Show Error
    end
```

## Module Dependencies

```mermaid
graph LR
    A[Config Manager] --> B[Logging]
    A --> C[Error Handler]
    B --> D[Metrics]
    C --> D

    E[Cache Manager] --> A
    E --> D

    F[Rate Limiter] --> A
    F --> D

    G[DI Container] --> A
    G --> B

    H[Event Bus] --> B
    H --> D

    I[Repository] --> A
    I --> B
    I --> C
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX / ALB]
    end

    subgraph "Frontend Tier"
        F1[Frontend App 1]
        F2[Frontend App 2]
        F3[Frontend App N]
    end

    subgraph "Backend Tier"
        B1[Backend Service 1]
        B2[Backend Service 2]
        B3[Backend Service N]
    end

    subgraph "Data Tier"
        R[(Redis<br/>Cache)]
        P[(PostgreSQL<br/>Database)]
        M[(MongoDB<br/>Documents)]
    end

    subgraph "Monitoring"
        PM[Prometheus]
        GR[Grafana]
        JA[Jaeger]
    end

    LB --> F1
    LB --> F2
    LB --> F3

    F1 --> B1
    F2 --> B2
    F3 --> B3

    B1 --> R
    B2 --> R
    B3 --> R

    B1 --> P
    B2 --> M
    B3 --> P

    B1 -.metrics.-> PM
    B2 -.metrics.-> PM
    B3 -.metrics.-> PM

    PM --> GR
    B1 -.traces.-> JA
    B2 -.traces.-> JA
    B3 -.traces.-> JA
```

## Scalability Strategy

### Horizontal Scaling

```mermaid
graph LR
    subgraph "Scale Out"
        S1[Service Instance 1]
        S2[Service Instance 2]
        S3[Service Instance 3]
        SN[Service Instance N]
    end

    LB[Load Balancer] --> S1
    LB --> S2
    LB --> S3
    LB --> SN

    S1 --> SC[Shared Cache]
    S2 --> SC
    S3 --> SC
    SN --> SC

    S1 --> SD[(Shared DB)]
    S2 --> SD
    S3 --> SD
    SN --> SD
```

**Characteristics**:
- Stateless services
- Shared cache (Redis)
- Session affinity optional
- Auto-scaling capable

### Vertical Scaling

**Optimization Targets**:
- **Memory**: LRU cache with configurable limits
- **CPU**: Optimized algorithms (< 10μs operations)
- **I/O**: Connection pooling, async operations

## Performance Architecture

### Backend Performance

```mermaid
graph TB
    R[Request] --> RL{Rate Limiter<br/>100K checks/sec}
    RL -->|Allowed| C{Cache<br/>326K ops/sec}
    RL -->|Denied| RE[Reject]

    C -->|Hit| RS[Response]
    C -->|Miss| DB[(Database)]
    DB --> CC[Update Cache]
    CC --> RS
```

**Performance Targets**:
- Rate Limiter: **100K+ checks/sec**
- LRU Cache: **326K+ operations/sec**
- Token Bucket: **< 10μs latency**

### Frontend Performance

```mermaid
graph LR
    U[User Input] --> D[Debounce<br/>300ms]
    D --> M[Memoization<br/>LRU Cache]
    M --> V[Virtual Scroll<br/>60fps with 1M items]
    V --> R[Render<br/>< 1ms]
```

**Performance Targets**:
- Button Render: **< 1ms**
- Debounce Accuracy: **±10ms**
- Virtual Scroll: **60fps with 1M+ items**
- Hook Memoization: **300K+ ops/sec**

## Security Architecture

```mermaid
graph TB
    R[Request] --> A[Authentication<br/>JWT Validation]
    A --> AZ[Authorization<br/>RBAC Check]
    AZ --> RL[Rate Limiting<br/>Anti-DDoS]
    RL --> V[Input Validation<br/>Sanitization]
    V --> B[Business Logic]
    B --> AL[Audit Logging]
    AL --> RS[Response]
```

**Security Layers**:
1. **Authentication**: JWT token validation
2. **Authorization**: Role-based access control (RBAC)
3. **Rate Limiting**: DDoS protection
4. **Input Validation**: XSS, SQL injection prevention
5. **Audit Logging**: Complete activity trail

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Frameworks**: FastAPI (optional)
- **Type System**: Python type hints + mypy
- **Testing**: pytest, hypothesis
- **Code Quality**: black, ruff

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Testing**: Vitest, Playwright
- **Code Quality**: ESLint, Prettier

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Docker Compose (local), Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Tracing**: OpenTelemetry, Jaeger

## Design Principles

### 1. Composability
Every module can work independently or compose with others.

### 2. Performance First
Benchmarked and optimized for production scale.

### 3. Type Safety
Full type coverage in Python and TypeScript.

### 4. Configuration-Driven
All behavior configurable via YAML/ENV.

### 5. Deployment Agnostic
Docker-first, runs anywhere (cloud or on-premise).

## Next Steps

- [Backend Architecture →](/architecture/backend)
- [Frontend Architecture →](/architecture/frontend)
- [Data Flow Details →](/architecture/data-flow)
- [Deployment Guide →](/architecture/deployment)
