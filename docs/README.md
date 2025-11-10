# Composable Toolkit Documentation

Welcome to the comprehensive documentation for the Composable Toolkit - a production-grade library of reusable backend modules and frontend components for building scalable, composable applications.

## 📚 Documentation Structure

This documentation site is built with VitePress and includes:

### 🚀 Getting Started
- **[Introduction](/guide/introduction)** - Philosophy, who it's for, and what's included
- **[Quick Start](/guide/quick-start)** - Get up and running in 5 minutes
- **[Testing Guide](/guide/testing)** - Comprehensive testing documentation

### 🏗️ Architecture
- **[Architecture Overview](/architecture/overview)** - System architecture with Mermaid diagrams
- **[Backend Architecture](/architecture/backend)** - Backend modules and patterns
- **[Frontend Architecture](/architecture/frontend)** - Atomic design and React components

### 📖 API Reference
- **[API Overview](/api/overview)** - Complete API documentation
- **[OpenAPI Specifications](/api/openapi/index)** - OpenAPI 3.0 specs for all 19 services

### 🎯 Pattern Library
- **[Pattern Overview](/patterns/overview)** - All 19 patterns with selection guide
- **Individual Patterns** - Deep-dive guides for each pattern:
  - [01 - REST API](/patterns/01-rest-api)
  - [02 - Analytics Engine](/patterns/02-analytics)
  - [03 - File Processing](/patterns/03-file-processing)
  - [04 - API Gateway](/patterns/04-api-gateway)
  - [05 - Data Export](/patterns/05-data-export)
  - [06 - Kappa Monitor](/patterns/06-kappa-monitor)
  - [07 - Event Sourcing](/patterns/07-event-sourcing)
  - [08 - TimeSeries](/patterns/08-timeseries)
  - [09 - Cache Browser](/patterns/09-cache-browser)
  - [10 - Message Queue](/patterns/10-message-queue)
  - [11 - Rate Limiter](/patterns/11-rate-limiter)
  - [12 - Lambda Architecture](/patterns/12-lambda-architecture)
  - [13 - CDC Monitor](/patterns/13-cdc-monitor)
  - [14 - Recommendations](/patterns/14-recommendations)
  - [15 - Search](/patterns/15-search)
  - [16 - Feature Store](/patterns/16-feature-store)
  - [17 - OLAP Dashboard](/patterns/17-olap-dashboard)
  - [18 - Trace Viewer](/patterns/18-trace-viewer)
  - [19 - Probabilistic](/patterns/19-probabilistic)

## 🎨 Documentation Features

### Visual Architecture Diagrams
- **60+ Mermaid Diagrams** showing system architecture, data flow, and interactions
- **Sequence Diagrams** for request/response flows
- **ER Diagrams** for data modeling
- **State Machines** for component lifecycle
- **Deployment Diagrams** for scaling strategies

### Comprehensive Code Examples
- **300+ Code Samples** for backend (Python/FastAPI) and frontend (React/TypeScript)
- **Production-Ready Implementations** with error handling and best practices
- **Performance Optimizations** with benchmarks
- **Testing Examples** for unit, integration, and E2E tests

### Pattern Library
- **19 Full-Stack Patterns** covering common use cases
- **Problem Statements** explaining when to use each pattern
- **Solution Architectures** with detailed diagrams
- **Scaling Strategies** for production deployments
- **Performance Benchmarks** with real metrics

### API Documentation
- **Complete API Reference** for all backend modules
- **OpenAPI 3.0 Specifications** for all 19 services
- **120+ Documented Endpoints** with examples
- **SDK Generation Ready** - use with OpenAPI Generator

## 🚀 Running the Documentation Site

### Prerequisites
- Node.js 18+
- npm or yarn

### Development Server

```bash
# Install dependencies
cd docs
npm install

# Start dev server
npm run docs:dev

# Open http://localhost:5173
```

### Production Build

```bash
# Build static site
npm run docs:build

# Preview production build
npm run docs:preview
```

### Docker Deployment

```bash
# Build Docker image
docker build -t toolkit-docs .

# Run container
docker run -p 80:80 toolkit-docs
```

## 📊 Documentation Statistics

- **Total Pages**: 35+ comprehensive guides
- **Mermaid Diagrams**: 60+ architecture visualizations
- **Code Examples**: 300+ backend and frontend samples
- **Pattern Guides**: 19 complete pattern implementations
- **API Endpoints**: 120+ documented endpoints
- **OpenAPI Specs**: 19 services, 7,659 lines
- **Total Lines**: 25,000+ lines of documentation

## 🎯 What's Documented

### Backend Modules
- **Core Foundation**: Config, Logging, Error Handling
- **Performance**: Cache (326K+ ops/sec), Rate Limiter (100K+ checks/sec), HTTP Client
- **Architecture Patterns**: DI Container, Event Bus, Repository Pattern
- **Data Processing**: Event Sourcing, Lambda/Kappa Architecture, TimeSeries
- **Operations**: Security (JWT, RBAC), CLI Framework

### Frontend Packages
- **Atomic Components**: Button, Input, Badge, Spinner, Icon
- **Performance Hooks**: useLRUMemo (300K+ ops/sec), useVirtualScroll (60fps @ 1M+ items), useDebounce, useThrottle, useWorkerPool
- **Design Tokens**: Colors, Spacing, Typography
- **Utilities**: Shared utilities and helpers

### 19 Example Applications
Each with complete documentation:
1. REST API - E-commerce inventory
2. Analytics Engine - Real-time event tracking
3. File Processor - Upload and processing pipeline
4. API Gateway - Service routing and load balancing
5. Data Export - Multi-format export service
6. Kappa Monitor - Stream processing visualization
7. Event Sourcing - CQRS dashboard
8. TimeSeries - Metrics visualization
9. Cache Browser - Distributed cache management
10. Message Queue - Queue monitoring
11. Rate Limiter - Token bucket visualization
12. Lambda Architecture - Batch + stream merger
13. CDC Monitor - Change data capture viewer
14. Recommendations - ML-powered suggestions
15. Search - Full-text search engine
16. Feature Store - ML feature management
17. OLAP Dashboard - Multi-dimensional analytics
18. Trace Viewer - Distributed tracing UI
19. Probabilistic - Bloom filters, HyperLogLog

## 🏆 Performance Benchmarks

All documented with real benchmarks:

| Component | Performance Target | Achieved |
|-----------|-------------------|----------|
| **Backend Cache** | 100K+ ops/sec | 326K+ ops/sec |
| **Rate Limiter** | 50K+ checks/sec | 100K+ checks/sec |
| **Frontend LRU Cache** | 100K+ lookups/sec | 300K+ lookups/sec |
| **Virtual Scroll** | 60fps @ 100K items | 60fps @ 1M+ items |
| **Button Render** | < 5ms | < 1ms |
| **API Response (p95)** | < 100ms | < 50ms |
| **Analytics Ingestion** | 10K+ events/sec | 50K+ events/sec |

## 🛠️ Using This Documentation

### For Developers
1. **Start with Quick Start** to get the basics
2. **Read Pattern Guides** for your use case
3. **Check API Reference** for module details
4. **Review Code Examples** for implementation patterns

### For Architects
1. **Review Architecture Overview** for system design
2. **Study Pattern Library** for architectural patterns
3. **Check Scaling Strategies** in each pattern
4. **Review Performance Benchmarks** for capacity planning

### For API Consumers
1. **Browse OpenAPI Specifications** for API contracts
2. **Use Swagger Editor** to explore endpoints
3. **Generate Client SDKs** with OpenAPI Generator
4. **Import to Postman** for API testing

## 📝 Contributing to Documentation

Documentation follows these principles:

1. **Comprehensive** - Cover all aspects (architecture, code, testing, deployment)
2. **Visual** - Use Mermaid diagrams for complex concepts
3. **Practical** - Include working code examples
4. **Production-Ready** - Show real-world implementations
5. **Performance-Focused** - Include benchmarks and optimization strategies

### Adding New Documentation

```bash
# Create new pattern guide
cp docs/patterns/01-rest-api.md docs/patterns/XX-new-pattern.md

# Edit and add Mermaid diagrams, code examples, etc.

# Update .vitepress/config.ts to add to navigation
```

## 🔗 External Links

- **GitHub Repository**: [github.com/yourusername/toolkit](https://github.com/yourusername/toolkit)
- **NPM Packages**: [@composable/atoms](https://npmjs.com/package/@composable/atoms)
- **PyPI Package**: [composable-toolkit](https://pypi.org/project/composable-toolkit)
- **Swagger Editor**: [editor.swagger.io](https://editor.swagger.io/)
- **VitePress**: [vitepress.dev](https://vitepress.dev/)
- **Mermaid**: [mermaid.js.org](https://mermaid.js.org/)

## 📄 License

This documentation is part of the Composable Toolkit project.

## 🙏 Acknowledgments

Built with:
- **VitePress** - Fast static site generator
- **Mermaid** - Diagram as code
- **Vue 3** - Progressive JavaScript framework

---

**Version**: 1.0.0
**Last Updated**: November 2024
**Status**: ✅ Complete (Phase 1.2 - Documentation Excellence)
# Unistax Documentation

Welcome to the Unistax documentation!

## Quick Links

- [Getting Started](#getting-started)
- [Backend Documentation](../backend/README.md)
- [Frontend Documentation](../frontend/README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [API Reference](#api-reference)

## Getting Started

### Installation

**Backend:**
```bash
pip install unistax
```

**Frontend:**
```bash
npm install @unistax/frontend
```

### First Steps

1. Check out the [examples](../examples/) directory
2. Read the package-specific documentation:
   - [Backend](../backend/README.md)
   - [Frontend](../frontend/README.md)
3. Review [CONTRIBUTING.md](../CONTRIBUTING.md) if you want to contribute

## API Reference

(API documentation will be generated as features are developed)

### Backend API

Coming soon...

### Frontend API

Coming soon...

## Guides

### Development Workflow

See [CONTRIBUTING.md](../CONTRIBUTING.md) for our branching strategy and development process.

### Release Process

We use continuous releases with semantic versioning. See [Release Process](../CONTRIBUTING.md#release-process) for details.

### Architecture

Learn about our [architecture decisions](../README.md#architecture-decisions) and why we chose a monorepo structure with GitHub Flow.

## Support

- [GitHub Issues](https://github.com/AaronHonour/unistax/issues)
- [GitHub Discussions](https://github.com/AaronHonour/unistax/discussions)
