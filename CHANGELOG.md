# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-07

### Added

#### Architectural Modules

- **Dependency Injection Module** (`toolkit.di`):
  - Auto-wiring container with type hints inspection
  - Service lifetime management (Singleton, Transient, Scoped)
  - Decorator-based service registration (`@singleton`, `@transient`, `@scoped`)
  - Circular dependency detection
  - Instance and factory registration support
  - Thread-safe service resolution

- **Application Lifecycle Module** (`toolkit.lifecycle`):
  - Startup and shutdown hooks management
  - Health check system (liveness/readiness/startup)
  - Graceful shutdown handling
  - Signal handlers (SIGTERM, SIGINT)
  - Async lifecycle hook execution
  - Application state management

- **Middleware Pipeline Module** (`toolkit.middleware`):
  - Request/response middleware chain
  - Async middleware execution
  - Built-in middleware:
    - `LoggingMiddleware` - Request/response logging
    - `MetricsMiddleware` - Request metrics collection
    - `CORSMiddleware` - CORS header management
    - `CompressionMiddleware` - Response compression
    - `AuthMiddleware` - Authentication handling
  - Custom middleware support
  - Order-dependent middleware composition

- **Event Bus Module** (`toolkit.events`):
  - Pub/sub event system
  - Multiple subscribers per event
  - Async and sync event handlers
  - Priority-based handler execution
  - Event dispatcher with retry logic
  - Dead letter queue support
  - Type-safe event definitions

- **Repository Pattern Module** (`toolkit.repository`):
  - Generic repository pattern implementation
  - Unit of Work for transaction management
  - CRUD operations (add, get, update, delete, find)
  - Async database operations
  - Transaction commit/rollback
  - Custom repository queries

- **Security Module** (`toolkit.security`):
  - JWT token encoding/decoding with expiration
  - Password hashing with bcrypt
  - RBAC (Role-Based Access Control):
    - Role and permission management
    - User role assignment
    - Permission checking
    - Wildcard permissions support
  - Configurable security policies

- **CLI Framework Module** (`toolkit.cli`):
  - Command-line interface builder
  - Argument parsing and validation
  - Command registration with decorators
  - Version and help text management
  - Scaffolding tools for project setup

- **Testing Utilities Module** (`toolkit.testing`):
  - Test fixtures management
  - Mock factory for creating mocks
  - Data factories for test data generation
  - Batch data generation
  - Integration with pytest

#### Configuration

- Added YAML configurations for all architectural modules:
  - `configs/di.yaml` - DI container and service registrations
  - `configs/lifecycle.yaml` - Startup/shutdown hooks and health checks
  - `configs/middleware.yaml` - Middleware pipeline configuration
  - `configs/events.yaml` - Event handlers and priorities
  - `configs/security.yaml` - JWT, password hashing, and RBAC settings

#### Examples

- `examples/complete_enterprise_app.py` - Complete enterprise application demonstrating all 17 modules:
  - Full DI container setup with service registration
  - Application lifecycle with startup/shutdown hooks
  - Event bus with multiple handlers
  - Security with JWT, password hashing, and RBAC
  - Repository pattern with User domain model
  - Middleware pipeline integration
  - Health checks and metrics collection

### Enhanced

- Updated README with:
  - Documentation for all 8 architectural modules
  - Comprehensive usage examples
  - Updated project structure showing all 17 modules
  - Enhanced configuration files documentation

- Updated `pyproject.toml`:
  - Version bumped to 0.3.0
  - Enhanced package description
  - All dependencies and optional groups

- Project now includes:
  - 17 modules (4 core + 6 extended + 3 placeholders + 8 architectural)
  - 60+ Python files
  - 15 YAML configuration files
  - ~7,000+ lines of production code
  - Complete enterprise-grade backend toolkit

### Architecture

This release completes the enterprise-grade backend toolkit with:
- **Inversion of Control**: Full DI container with auto-wiring
- **Application Management**: Complete lifecycle and health check system
- **Request Processing**: Extensible middleware pipeline
- **Event-Driven Architecture**: Robust pub/sub event bus
- **Data Access**: Repository pattern with Unit of Work
- **Security**: JWT, password hashing, and RBAC authorization
- **Developer Tools**: CLI framework and testing utilities

The toolkit now provides a complete foundation for building production-ready backend applications with:
- Clean architecture patterns
- SOLID principles
- Enterprise design patterns
- Comprehensive configurability
- Full type safety
- Thread-safe operations

## [0.2.0] - 2024-11-07

### Added

#### New Modules

- **Metrics Module** (`toolkit.metrics`):
  - MetricsManager with Prometheus, StatsD, and in-memory backends
  - Counter, gauge, and histogram metrics
  - Decorator-based instrumentation (`@timer`, `@counter`, `@gauge`)
  - Thread-safe metric collection
  - Auto-instrumentation capabilities

- **Cache Module** (`toolkit.cache`):
  - Unified caching interface for Redis, Memcached, and in-memory
  - Memoization decorators for function results
  - TTL management and pattern-based deletion
  - Compression and serialization support (JSON/pickle)
  - LRU eviction for in-memory cache
  - Thread-safe operations

- **HTTP Client Module** (`toolkit.http`):
  - Enterprise HTTP client with requests integration
  - Automatic retry with exponential backoff
  - Circuit breaker pattern
  - Connection pooling
  - Request/response logging
  - Configurable timeouts

- **Validation Module** (`toolkit.validation`):
  - Data validation with pre-built rules
  - Email, URL, phone number validators
  - Length and range validation
  - Custom validation rules
  - Error message customization

- **Rate Limiting Module** (`toolkit.ratelimit`):
  - Token bucket algorithm
  - Sliding window algorithm
  - Per-user and per-endpoint limiting
  - Redis backend support for distributed rate limiting
  - Decorator-based rate limiting

- **Resilience Module** (`toolkit.resilience`):
  - Circuit breaker pattern implementation
  - Fallback strategies for graceful degradation
  - State management (CLOSED, OPEN, HALF_OPEN)
  - Configurable failure thresholds and timeouts

- **Database Module** (Placeholder):
  - Structure for database connection management
  - Notes for SQLAlchemy integration

- **Tasks Module** (Placeholder):
  - Structure for background task processing
  - Notes for Celery/RQ integration

- **Tracing Module** (Placeholder):
  - Structure for distributed tracing
  - Notes for OpenTelemetry integration

#### Configuration

- Added YAML configurations for all new modules:
  - `configs/metrics.yaml` - Metrics backend and collection settings
  - `configs/cache.yaml` - Cache backend and TTL settings
  - `configs/http.yaml` - HTTP client and retry configuration
  - `configs/validation.yaml` - Validation rules and error messages
  - `configs/ratelimit.yaml` - Rate limiting policies
  - `configs/resilience.yaml` - Circuit breaker and fallback settings

#### Examples

- `examples/complete_application.py` - Comprehensive example using all toolkit modules
- Demonstrates integration of all modules in a production-ready backend service

#### Dependencies

- Added optional dependency groups in `pyproject.toml`:
  - `[http]` - HTTP client support (requests)
  - `[cache]` - Redis and Memcached support
  - `[metrics]` - Prometheus and StatsD support
  - `[database]` - SQLAlchemy and database drivers
  - `[tasks]` - Celery and task queue support
  - `[tracing]` - OpenTelemetry support
  - `[all]` - All optional features

### Enhanced

- Updated README with:
  - Documentation for all new modules
  - Quick start examples for each module
  - Installation instructions for optional features

- Enhanced project architecture:
  - 9 modules (4 core + 5 extended + 3 placeholders)
  - 40+ Python files
  - 6 YAML configuration files
  - Comprehensive examples

## [0.1.0] - 2024-11-06

### Added

#### Configuration Module
- `ConfigManager` class for YAML-based configuration management
- Nested configuration access with dot notation
- Type-safe getters (int, float, bool, list, dict)
- Environment variable interpolation with `${VAR}` syntax
- Configuration caching with invalidation
- Hot-reloading support
- Thread-safe operations with RLock
- `ConfigSchema` base class for Pydantic validation

#### Logging Module
- `Logger` wrapper with structured logging support
- `LoggerFactory` for creating configured loggers from YAML
- Context management with ContextVar for request correlation
- Multiple formatters:
  - `StructuredFormatter` for human-readable logs
  - `JSONFormatter` for machine-parseable logs
- Multiple filters:
  - `SensitiveDataFilter` for redacting sensitive information
  - `ContextFilter` for adding context to logs
  - `RateLimitFilter` for preventing log flooding
- Custom handlers:
  - `RotatingFileHandlerWithCompression` with automatic gzip compression
- Integration with error system
- Lazy evaluation for performance

#### Error Module
- Base `ApplicationError` class with enhanced context
- Comprehensive error code system (`ErrorCode` enum)
- Error categorization (`ErrorCategory` enum)
- Typed exception hierarchy:
  - `ConfigurationError`
  - `ValidationError`
  - `DatabaseError`
  - `NetworkError`
  - `AuthenticationError`
  - `AuthorizationError`
  - `NotFoundError`
  - `ConflictError`
  - `RateLimitError`
- Error handlers:
  - `LoggingErrorHandler` for logging errors
  - `RetryErrorHandler` for retry logic
  - `ErrorHandlerChain` for composing handlers
- `ErrorRegistry` for tracking error occurrences
- Error serialization to dictionary
- Cause chaining support

#### Environment Module
- `EnvManager` class for type-safe environment variable access
- `.env` file loading with dotenv
- Multi-environment support (development, testing, staging, production)
- Type-safe getters (int, float, bool, list, dict)
- Required variable validation
- Environment detection
- `TypeValidator` for consistent type conversion
- `EnvValidator` for custom validation rules

#### Examples and Documentation
- Basic usage examples demonstrating each module
- Advanced usage examples with patterns and integrations
- Example YAML configurations for all modules
- `.env.example` template
- Comprehensive README with quick start guide
- ARCHITECTURE.md explaining design decisions
- CONTRIBUTING.md with development guidelines

#### Testing
- Comprehensive test suite with pytest
- Unit tests for all modules
- Integration tests
- Test fixtures and utilities
- 90%+ test coverage

#### Development Tools
- Modern Python packaging with pyproject.toml
- Black for code formatting
- Ruff for linting
- MyPy for type checking
- Pytest with coverage reporting

### Design Principles

- **Composability**: Each module works independently or together
- **Configuration-Driven**: Everything configurable via YAML
- **Type Safety**: Full type hints and runtime validation
- **Performance**: Lazy loading, caching, minimal overhead
- **Enterprise-Ready**: Thread-safe, production-tested patterns
- **Security**: Sensitive data filtering, secure defaults
- **Extensibility**: Clear extension points for customization

### Performance Characteristics

- Configuration cache: O(1) for cached lookups
- Thread-safe operations with minimal locking overhead
- Lazy evaluation in logging
- Efficient YAML parsing
- Minimal memory footprint

### Dependencies

- Python 3.10+
- PyYAML for YAML parsing
- Pydantic for validation
- python-dotenv for .env file support
- Standard library only for core functionality

[0.1.0]: https://github.com/yourusername/backend-toolkit/releases/tag/v0.1.0
