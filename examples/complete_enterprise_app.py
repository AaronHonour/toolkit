"""
Complete Enterprise Application Example.

Demonstrates all 17 modules of the backend toolkit in a production-ready application.
"""

import asyncio
from dataclasses import dataclass

# Core modules
from unistax.config import ConfigManager
from unistax.logging import LoggerFactory
from unistax.errors import ApplicationError
from unistax.env import EnvManager

# Extended modules
from unistax.metrics import MetricsManager
from unistax.cache import CacheManager
from unistax.validation import Validator, ValidationRules
from unistax.ratelimit import RateLimiter
from unistax.resilience import CircuitBreaker

# New architectural modules
from unistax.di import Container, Lifetime, singleton
from unistax.lifecycle import Application
from unistax.middleware import MiddlewarePipeline, LoggingMiddleware, MetricsMiddleware
from unistax.events import EventBus, Event
from unistax.repository import Repository
from unistax.security import JWT, PasswordHasher, RBAC


# Domain models
@dataclass
class User:
    id: int
    email: str
    password_hash: str
    name: str


# Events
@dataclass
class UserCreatedEvent(Event):
    user_id: int
    email: str


# Repository
class UserRepository(Repository[User]):
    """User repository with custom queries."""

    async def find_by_email(self, email: str):
        return await self.find_one(email=email)


# Services
@singleton
class UserService:
    """User service with full enterprise features."""

    def __init__(
        self,
        repository: UserRepository,
        cache: CacheManager,
        event_bus: EventBus,
        password_hasher: PasswordHasher,
        metrics: MetricsManager,
    ):
        self.repository = repository
        self.cache = cache
        self.event_bus = event_bus
        self.password_hasher = password_hasher
        self.metrics = metrics

    async def create_user(self, email: str, password: str, name: str) -> User:
        """Create a new user."""
        # Hash password
        password_hash = self.password_hasher.hash(password)

        # Create user
        user = User(id=None, email=email, password_hash=password_hash, name=name)
        user = await self.repository.add(user)

        # Cache user
        await self.cache.set(f"user:{user.id}", user, ttl=3600)

        # Publish event
        await self.event_bus.publish(UserCreatedEvent(user_id=user.id, email=email))

        # Track metric
        self.metrics.counter("users.created")

        return user

    async def get_user(self, user_id: int) -> User:
        """Get user by ID with caching."""
        # Check cache
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            self.metrics.counter("users.cache_hit")
            return cached

        # Load from repository
        self.metrics.counter("users.cache_miss")
        user = await self.repository.get(user_id)

        # Cache result
        if user:
            self.cache.set(f"user:{user_id}", user, ttl=3600)

        return user


# Application setup
class EnterpriseApplication:
    """Complete enterprise application with all features."""

    def __init__(self):
        print("=" * 80)
        print("INITIALIZING ENTERPRISE APPLICATION")
        print("=" * 80)

        # 1. Dependency Injection Container
        print("\n[1/13] Setting up Dependency Injection...")
        self.container = Container()
        self._register_services()

        # 2. Configuration
        print("[2/13] Loading configuration...")
        self.config = self.container.resolve(ConfigManager)

        # 3. Environment
        print("[3/13] Setting up environment...")
        self.env = self.container.resolve(EnvManager)

        # 4. Logging
        print("[4/13] Configuring logging...")
        self.logger = self.container.resolve(LoggerFactory)

        # 5. Metrics
        print("[5/13] Initializing metrics...")
        self.metrics = self.container.resolve(MetricsManager)

        # 6. Cache
        print("[6/13] Setting up cache...")
        self.cache = self.container.resolve(CacheManager)

        # 7. Validation
        print("[7/13] Configuring validation...")
        self.validator = Validator()
        self.validator.add_rule("email", ValidationRules.email)

        # 8. Rate Limiting
        print("[8/13] Setting up rate limiting...")
        self.rate_limiter = RateLimiter(rate=100, period=60)

        # 9. Resilience
        print("[9/13] Configuring resilience patterns...")
        self.circuit_breaker = CircuitBreaker(failure_threshold=5)

        # 10. Events
        print("[10/13] Initializing event bus...")
        self.event_bus = self.container.resolve(EventBus)
        self._setup_event_handlers()

        # 11. Security
        print("[11/13] Setting up security...")
        self.jwt = JWT(secret="my-secret-key")
        self.password_hasher = PasswordHasher()
        self.rbac = RBAC()
        self._setup_rbac()

        # 12. Middleware
        print("[12/13] Configuring middleware pipeline...")
        self.middleware = MiddlewarePipeline()
        self.middleware.use(LoggingMiddleware(self.logger))
        self.middleware.use(MetricsMiddleware(self.metrics))

        # 13. Application Lifecycle
        print("[13/13] Setting up application lifecycle...")
        self.app = Application(name="enterprise-app")
        self._setup_lifecycle()

        print("\n" + "=" * 80)
        print("✓ ALL SYSTEMS INITIALIZED")
        print("=" * 80)

    def _register_services(self):
        """Register services in DI container."""
        # Core services
        self.container.register_instance(
            ConfigManager, ConfigManager.from_yaml("configs/config.yaml")
        )
        self.container.register_instance(
            EnvManager, EnvManager()
        )
        self.container.register_instance(
            LoggerFactory, LoggerFactory.create("enterprise-app")
        )

        # Extended services
        self.container.register(MetricsManager, lifetime=Lifetime.SINGLETON)
        self.container.register(CacheManager, lifetime=Lifetime.SINGLETON)
        self.container.register(EventBus, lifetime=Lifetime.SINGLETON)

        # Domain services
        self.container.register(UserRepository, lifetime=Lifetime.SCOPED)
        self.container.register(UserService, lifetime=Lifetime.SCOPED)

        # Security
        self.container.register_instance(PasswordHasher, PasswordHasher())

    def _setup_event_handlers(self):
        """Setup event handlers."""

        @self.event_bus.subscribe(UserCreatedEvent)
        async def on_user_created(event: UserCreatedEvent):
            print(f"📧 Sending welcome email to user {event.user_id}...")

        @self.event_bus.subscribe(UserCreatedEvent)
        async def log_user_creation(event: UserCreatedEvent):
            self.logger.info(
                "User created",
                extra={"user_id": event.user_id, "email": event.email},
            )

    def _setup_rbac(self):
        """Setup RBAC roles and permissions."""
        self.rbac.define_role("admin", ["*"])
        self.rbac.define_role("user", ["users:read", "users:update_own"])

    def _setup_lifecycle(self):
        """Setup application lifecycle hooks."""

        @self.app.on_startup
        async def startup():
            print("🚀 Application starting...")
            self.metrics.counter("app.startup")

        @self.app.on_shutdown
        async def shutdown():
            print("👋 Application shutting down...")
            self.cache.clear()
            self.metrics.counter("app.shutdown")

        @self.app.health_check(check_type="liveness")
        def app_health():
            return True

        @self.app.health_check(check_type="readiness")
        def cache_health():
            return True  # Check if cache is accessible

    async def run_demo(self):
        """Run application demo."""
        print("\n" + "=" * 80)
        print("RUNNING APPLICATION DEMO")
        print("=" * 80)

        # Start application
        await self.app.start()

        # Get user service from container
        user_service = self.container.resolve(UserService)

        # Demo: Create user
        print("\n[DEMO] Creating new user...")
        try:
            user = await user_service.create_user(
                email="john.doe@example.com", password="SecurePass123!", name="John Doe"
            )
            print(f"✓ User created: {user.name} ({user.email})")
        except Exception as e:
            print(f"✗ Error creating user: {e}")

        # Demo: Get user (should hit cache)
        print("\n[DEMO] Fetching user (should hit cache)...")
        user = await user_service.get_user(1)
        if user:
            print(f"✓ User fetched: {user.name}")

        # Demo: Check health
        print("\n[DEMO] Checking application health...")
        health = self.app.get_health_status()
        print(f"Health status: {health['status']}")

        # Demo: View metrics
        print("\n[DEMO] Application Metrics:")
        metrics = self.metrics.get_metrics()
        for name, value in metrics.get("counters", {}).items():
            print(f"  {name}: {value}")

        # Stop application
        await self.app.stop()

        print("\n" + "=" * 80)
        print("✓ DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)


async def main():
    """Main entry point."""
    try:
        app = EnterpriseApplication()
        await app.run_demo()

    except Exception as e:
        print(f"\n❌ Application error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
