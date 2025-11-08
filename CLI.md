# create-composable-app

**Zero-to-production scaffolding tool** for the Composable Toolkit.

Generate production-ready applications in less than 5 minutes with best practices built-in.

## Quick Start

```bash
# Interactive mode (recommended)
npx create-composable-app my-app

# With options
npx create-composable-app my-app \
  --template monorepo \
  --framework fastapi \
  --patterns cache,database,auth,metrics
```

## Features

✅ **19 Production Patterns** - Cache, Database, Rate Limiting, Auth, Metrics, Tracing, and more
✅ **4 Frameworks** - FastAPI, Django, Flask, NestJS
✅ **3 Templates** - Monorepo, Microservices, Serverless
✅ **Cloud-Ready** - AWS, GCP, Azure deployment configs
✅ **Complete CI/CD** - GitHub Actions workflows included
✅ **Observability** - Prometheus, Grafana, Jaeger pre-configured
✅ **Docker & K8s** - Production-ready containers
✅ **100% Type-Safe** - Full TypeScript/Python typing
✅ **Zero Config** - Works out of the box

## Usage

### Interactive Mode

```bash
npx create-composable-app my-app
```

You'll be prompted for:
1. **Project template** - Monorepo, Microservices, or Serverless
2. **Framework** - FastAPI, Django, Flask, or NestJS
3. **Patterns** - Select from 19 production patterns
4. **Configuration** - Docker, CI/CD, Observability, Tests

### CLI Mode

```bash
npx create-composable-app my-app \
  --template microservices \
  --framework fastapi \
  --patterns cache,database,ratelimit,auth,metrics,tracing
```

### Options

| Option | Description | Values |
|--------|-------------|--------|
| `--template` | Project template | `monorepo`, `microservices`, `serverless` |
| `--framework` | Web framework | `fastapi`, `django`, `flask`, `nestjs` |
| `--patterns` | Comma-separated patterns | See [Patterns](#patterns) below |
| `--skip-install` | Skip dependency installation | Flag |
| `--skip-git` | Skip git initialization | Flag |

## Templates

### Monorepo

Single repository with shared toolkit and multiple services.

```
my-app/
├── shared/           # Shared toolkit components
│   └── src/toolkit/  # Pattern implementations
├── services/         # Service implementations
│   └── api/         # Main API service
├── tests/           # Test suites
├── docs/            # Documentation
└── docker-compose.yml
```

**Use when:**
- Starting a new project
- All services in one language
- Shared dependencies
- Simplified CI/CD

### Microservices

Distributed services architecture with independent deployments.

```
my-app/
├── services/        # Independent microservices
│   ├── api/        # API Gateway
│   ├── cache/      # Cache service
│   ├── auth/       # Auth service
│   └── ...
├── infrastructure/ # Kubernetes/Terraform
└── docker-compose.yml
```

**Use when:**
- Large teams
- Independent scaling
- Different languages per service
- Polyglot persistence

### Serverless

AWS Lambda / GCP Cloud Functions ready.

```
my-app/
├── functions/      # Lambda functions
├── layers/        # Lambda layers (toolkit)
├── infrastructure/# SAM/Terraform
└── tests/
```

**Use when:**
- Variable/unpredictable traffic
- Pay-per-use pricing
- Minimal ops overhead
- Event-driven architecture

## Frameworks

### FastAPI (Python)

```bash
npx create-composable-app my-app --framework fastapi
```

**Includes:**
- Async/await support
- Automatic OpenAPI docs
- Pydantic validation
- High performance (Starlette + Uvicorn)

### Django (Python)

```bash
npx create-composable-app my-app --framework django
```

**Includes:**
- Django REST Framework
- Admin panel
- ORM migrations
- Battle-tested ecosystem

### Flask (Python)

```bash
npx create-composable-app my-app --framework flask
```

**Includes:**
- Lightweight and flexible
- Extensions ecosystem
- Simple and Pythonic
- Perfect for microservices

### NestJS (TypeScript)

```bash
npx create-composable-app my-app --framework nestjs
```

**Includes:**
- TypeScript-first
- Dependency injection
- Modular architecture
- Enterprise-ready

## Patterns

### Recommended Patterns (Auto-selected)

| Pattern | Description | Dependencies |
|---------|-------------|--------------|
| **cache** | Redis + in-memory caching | Redis |
| **database** | PostgreSQL with migrations | PostgreSQL |
| **ratelimit** | Token bucket rate limiting | - |
| **auth** | JWT + OAuth2 authentication | - |

### Infrastructure Patterns

| Pattern | Description | Dependencies |
|---------|-------------|--------------|
| **gateway** | Reverse proxy + routing | - |
| **events** | Pub/sub event system | Kafka |
| **queue** | Task queue with workers | Kafka, Redis |
| **storage** | S3-compatible file storage | - |
| **search** | Full-text search | Elasticsearch |

### Feature Patterns

| Pattern | Description | Dependencies |
|---------|-------------|--------------|
| **notifications** | Email/SMS/Push notifications | - |
| **features** | Dynamic feature toggles | - |
| **audit** | Audit trail for compliance | - |
| **webhooks** | Webhook delivery system | - |
| **scheduler** | Cron-like job scheduler | - |

### API Patterns

| Pattern | Description | Dependencies |
|---------|-------------|--------------|
| **graphql** | GraphQL API layer | - |
| **pagination** | Cursor + offset pagination | - |
| **multitenant** | Multi-tenancy support | - |

### Observability Patterns

| Pattern | Description | Dependencies |
|---------|-------------|--------------|
| **metrics** | Prometheus metrics | Prometheus |
| **tracing** | Distributed tracing | Jaeger |

## Generated Structure

### What You Get

Every generated project includes:

#### Core Files
```
my-app/
├── README.md               # Getting started guide
├── Makefile                # Common commands
├── pyproject.toml          # Python dependencies
├── .gitignore              # Git configuration
└── .env.example            # Environment variables
```

#### Docker Configuration
```
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Local development
└── .dockerignore
```

#### CI/CD Workflows
```
.github/workflows/
├── ci.yml                  # Tests, linting, security
├── deploy.yml              # Cloud deployment
└── benchmarks.yml          # Performance tracking
```

#### Documentation
```
docs/
├── README.md               # Project overview
├── ARCHITECTURE.md         # System design
├── DEVELOPMENT.md          # Dev guide
└── DEPLOYMENT.md           # Deploy instructions
```

#### Tests
```
tests/
├── test_api.py             # API tests
├── test_integration.py     # Integration tests
├── benchmarks/             # Performance tests
└── conftest.py             # Pytest configuration
```

#### Observability (if selected)
```
observability/
├── prometheus/
│   ├── prometheus.yml      # Scrape config
│   └── rules/alerts.yml    # Alert rules
├── grafana/
│   ├── datasources/        # Data sources
│   └── dashboards/         # Pre-built dashboards
└── loki/                   # Log aggregation
```

## Quick Commands

After generation, your project has these commands:

```bash
# Development
make install          # Install dependencies
make dev              # Start development environment
make test             # Run tests
make lint             # Run linters
make format           # Format code

# Docker
make docker-build     # Build images
make docker-up        # Start all services
make docker-down      # Stop all services
make docker-logs      # View logs

# Production
make build            # Build for production
make deploy           # Deploy (after configuring cloud provider)

# Performance
make benchmarks       # Run performance tests
```

## Examples

### Startup Backend (Monorepo + FastAPI)

```bash
npx create-composable-app startup-api \
  --template monorepo \
  --framework fastapi \
  --patterns cache,database,auth,metrics
```

**Result:** Production-ready API with authentication, caching, database, and monitoring in < 5 minutes.

### Enterprise Microservices (Django)

```bash
npx create-composable-app enterprise-platform \
  --template microservices \
  --framework django \
  --patterns database,cache,auth,queue,events,metrics,tracing,audit
```

**Result:** Scalable microservices platform with comprehensive observability and compliance.

### Serverless API (AWS Lambda)

```bash
npx create-composable-app serverless-api \
  --template serverless \
  --framework fastapi \
  --patterns cache,database,auth
```

**Result:** Auto-scaling serverless API with SAM deployment configuration.

## Customization

### Adding Custom Patterns

```bash
# After generation, add patterns from main toolkit
cd my-app/shared/src/toolkit
cp -r /path/to/toolkit/src/toolkit/notifications .
```

### Modifying Templates

The generator uses EJS templates. Fork and customize:

```bash
git clone https://github.com/composable-toolkit/cli
cd cli/templates
# Edit templates as needed
npm run build
```

## Cloud Deployment

### AWS

```bash
# ECS Deployment
make deploy-aws

# Serverless (SAM)
cd my-app
sam deploy --guided
```

### GCP

```bash
# Cloud Run
make deploy-gcp

# Cloud Functions
gcloud functions deploy my-app \
  --runtime python311 \
  --trigger-http
```

### Azure

```bash
# App Service
make deploy-azure

# Functions
func azure functionapp publish my-app
```

## Troubleshooting

### Build Fails

```bash
# Clear and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Permission Denied

```bash
# Make CLI executable
chmod +x dist/index.js
```

### Template Not Found

```bash
# Ensure templates directory exists
ls -la templates/
```

## Comparison

### vs. create-react-app
- ✅ Backend-focused (FastAPI, Django, Flask)
- ✅ Production patterns included
- ✅ Observability built-in
- ✅ Cloud deployment configs

### vs. cookiecutter
- ✅ Interactive CLI
- ✅ Modern TypeScript tooling
- ✅ Composable patterns
- ✅ Live-tested code

### vs. Manual Setup
- ⚡ **10x faster** - 5 minutes vs 2-3 days
- ✅ **Best practices** - Pre-configured for production
- ✅ **Complete** - Testing, CI/CD, observability included
- ✅ **Maintained** - Regular updates with toolkit

## Requirements

- **Node.js** 16+ (for CLI)
- **Python** 3.10+ (for Python projects)
- **Docker** (optional, for containerization)
- **Git** (for version control)

## Development

```bash
# Clone repository
git clone https://github.com/composable-toolkit/cli
cd cli

# Install dependencies
npm install

# Build
npm run build

# Link locally
npm link

# Test
create-composable-app test-app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add/modify templates
4. Test generation
5. Submit a pull request

## Roadmap

- [ ] More frameworks (Go, Rust, Java)
- [ ] Pattern marketplace
- [ ] Custom template registry
- [ ] VS Code extension
- [ ] Project upgrade command

## License

MIT

## Support

- **Documentation**: https://composable-toolkit.dev
- **Issues**: https://github.com/composable-toolkit/cli/issues
- **Discord**: https://discord.gg/composable-toolkit

---

**Built with ❤️ for developers who ship fast.**
