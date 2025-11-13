# Unistax Documentation

Welcome to the comprehensive documentation for **Unistax** - a production-grade library of reusable backend modules and frontend components for building scalable, composable applications.

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
- **[OpenAPI Specifications](/api/openapi/index)** - OpenAPI 3.0 specs for all 20 services

### 🎯 Pattern Library
- **[Pattern Overview](/patterns/overview)** - All 20 patterns with selection guide
- **Individual Patterns** - Deep-dive guides for each pattern (01-20)

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
- **20 Full-Stack Patterns** covering common use cases
- **Problem Statements** explaining when to use each pattern
- **Solution Architectures** with detailed diagrams
- **Scaling Strategies** for production deployments
- **Performance Benchmarks** with real metrics

### API Documentation
- **Complete API Reference** for all backend modules
- **OpenAPI 3.0 Specifications** for all 20 services
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
docker build -t unistax-docs .

# Run container
docker run -p 80:80 unistax-docs
```

## 📊 Documentation Statistics

- **Total Pages**: 35+ comprehensive guides
- **Mermaid Diagrams**: 60+ architecture visualizations
- **Code Examples**: 300+ backend and frontend samples
- **Pattern Guides**: 20 complete pattern implementations
- **API Endpoints**: 120+ documented endpoints
- **OpenAPI Specs**: 20 services, 7,659+ lines
- **Total Lines**: 25,000+ lines of documentation

## 🎯 What's Documented

### Backend Modules
- **Core Foundation**: Config, Logging, Error Handling
- **Performance**: Cache (326K+ ops/sec), Rate Limiter (100K+ checks/sec), HTTP Client
- **Architecture Patterns**: DI Container, Event Bus, Repository Pattern
- **Data Processing**: Event Sourcing, Lambda/Kappa Architecture, TimeSeries
- **Graph & Analysis**: Dependency graphs, graph algorithms, impact analysis
- **Operations**: Security (JWT, RBAC), CLI Framework

### Frontend Packages
- **Atomic Components**: Button, Input, Badge, Spinner, Icon
- **Performance Hooks**: useLRUMemo (300K+ ops/sec), useVirtualScroll (60fps @ 1M+ items), useDebounce, useThrottle, useWorkerPool
- **Design Tokens**: Colors, Spacing, Typography
- **Utilities**: Shared utilities and helpers

### 20 Example Applications
Each with complete documentation including the new Service Dependency Graph Builder.

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

## 🔗 Links

- **GitHub Repository**: [github.com/AaronHonour/unistax](https://github.com/AaronHonour/unistax)
- **NPM Packages**: [@unistax/*](https://npmjs.com/org/unistax)
- **PyPI Package**: [unistax](https://pypi.org/project/unistax)

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- **VitePress** - Fast static site generator
- **Mermaid** - Diagram as code
- **Vue 3** - Progressive JavaScript framework

---

**Version**: 1.0.0
**Last Updated**: November 2024
**Status**: ✅ Production Ready
