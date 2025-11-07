"""
Complete application example using all toolkit modules.

Demonstrates how to build a production-ready backend service using
the complete toolkit.
"""

from toolkit.config import ConfigManager
from toolkit.logging import LoggerFactory
from toolkit.errors import ApplicationError, ValidationError
from toolkit.env import EnvManager
from toolkit.metrics import MetricsManager
from toolkit.cache import CacheManager
from toolkit.http import HTTPClient
from toolkit.validation import Validator, ValidationRules
from toolkit.ratelimit import RateLimiter
from toolkit.resilience import CircuitBreaker, Fallback


class BackendService:
    """
    Complete backend service demonstrating all toolkit features.

    Showcases:
    - Configuration management
    - Structured logging
    - Error handling
    - Metrics collection
    - Caching
    - HTTP requests
    - Validation
    - Rate limiting
    - Resilience patterns
    """

    def __init__(self, config_path: str = "configs/config.yaml"):
        # Initialize all toolkit components
        print("=" * 60)
        print("Initializing Backend Service with Enterprise Toolkit")
        print("=" * 60)

        # 1. Configuration
        print("\n[1/9] Loading configuration...")
        self.config = ConfigManager.from_yaml(config_path)
        print(f"✓ Config loaded: {self.config.get('app.name')}")

        # 2. Environment
        print("\n[2/9] Setting up environment...")
        self.env = EnvManager(environment=self.config.get("environment"))
        print(f"✓ Environment: {self.env.get_environment().value}")

        # 3. Logging
        print("\n[3/9] Configuring logging...")
        self.logger = LoggerFactory.from_yaml("configs/logging.yaml")
        self.logger.set_context(
            service=self.config.get("app.name"),
            environment=self.env.get_environment().value,
        )
        self.logger.info("Logging system initialized")
        print("✓ Logging configured")

        # 4. Metrics
        print("\n[4/9] Setting up metrics...")
        self.metrics = MetricsManager(backend="memory", prefix="backend")
        self.metrics.counter("service.startup", labels={"status": "success"})
        print("✓ Metrics system ready")

        # 5. Cache
        print("\n[5/9] Initializing cache...")
        self.cache = CacheManager(backend="memory")
        print("✓ Cache initialized")

        # 6. HTTP Client
        print("\n[6/9] Setting up HTTP client...")
        try:
            self.http = HTTPClient(
                base_url=self.config.get("api.base_url", "https://api.example.com"),
                timeout=10.0,
                max_retries=3,
            )
            print("✓ HTTP client ready")
        except ImportError:
            self.http = None
            print("⚠ HTTP client unavailable (install: pip install requests)")

        # 7. Validation
        print("\n[7/9] Configuring validation...")
        self.validator = Validator()
        self.validator.add_rule("email", ValidationRules.email, "Invalid email")
        self.validator.add_rule("username", lambda x: 3 <= len(x) <= 50, "Invalid username length")
        print("✓ Validation rules loaded")

        # 8. Rate Limiting
        print("\n[8/9] Setting up rate limiting...")
        self.rate_limiter = RateLimiter(rate=100, period=60)  # 100 req/min
        print("✓ Rate limiter configured")

        # 9. Resilience
        print("\n[9/9] Configuring resilience patterns...")
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
        self.fallback = Fallback(default_value={"status": "unavailable"})
        print("✓ Circuit breaker and fallback ready")

        print("\n" + "=" * 60)
        print("✓ All systems initialized successfully!")
        print("=" * 60)

    def process_user_request(self, user_id: int, email: str, username: str):
        """
        Process user request demonstrating all features.

        Args:
            user_id: User ID
            email: User email
            username: Username
        """
        print(f"\n{'='*60}")
        print(f"Processing Request: User {user_id}")
        print(f"{'='*60}")

        # Start timing
        with self.metrics.timer("request.duration"):
            try:
                # 1. Rate Limiting
                print("\n[1] Checking rate limit...")
                if not self.rate_limiter.is_allowed(f"user:{user_id}"):
                    self.logger.warning("Rate limit exceeded", extra={"user_id": user_id})
                    raise Exception("Rate limit exceeded")
                print("✓ Rate limit OK")

                # 2. Validation
                print("\n[2] Validating input...")
                is_valid = self.validator.validate(
                    {"email": email, "username": username}
                )
                if not is_valid:
                    errors = self.validator.get_errors()
                    self.logger.error("Validation failed", extra={"errors": errors})
                    raise ValidationError("Invalid input", details=errors)
                print(f"✓ Validation passed")

                # 3. Check Cache
                print("\n[3] Checking cache...")
                cache_key = f"user:{user_id}"
                cached_data = self.cache.get(cache_key)

                if cached_data:
                    self.metrics.counter("cache.hits")
                    self.logger.info("Cache hit", extra={"key": cache_key})
                    print(f"✓ Cache HIT: {cached_data}")
                    return cached_data

                self.metrics.counter("cache.misses")
                print("⚠ Cache MISS")

                # 4. Fetch Data (with Circuit Breaker)
                print("\n[4] Fetching data (with circuit breaker)...")

                @self.circuit_breaker.protected(fallback=lambda: {"fallback": True})
                def fetch_user_data():
                    # Simulate API call
                    print("  → Making API call...")
                    user_data = {
                        "user_id": user_id,
                        "email": email,
                        "username": username,
                        "status": "active",
                    }
                    return user_data

                data = fetch_user_data()
                print(f"✓ Data fetched: {data}")

                # 5. Store in Cache
                print("\n[5] Storing in cache...")
                self.cache.set(cache_key, data, ttl=3600)
                print("✓ Cached for 1 hour")

                # 6. Log Success
                self.logger.info(
                    "Request processed successfully",
                    extra={
                        "user_id": user_id,
                        "email": email,
                        "username": username,
                    },
                )

                # 7. Update Metrics
                self.metrics.counter("requests.success")
                print("\n✓ Request completed successfully!")

                return data

            except ValidationError as e:
                self.metrics.counter("requests.validation_error")
                self.logger.error(f"Validation error: {e.message}", extra=e.details)
                print(f"\n✗ Validation error: {e.message}")
                raise

            except Exception as e:
                self.metrics.counter("requests.error")
                self.logger.exception("Request processing failed")
                print(f"\n✗ Error: {str(e)}")
                raise

    def get_metrics_summary(self):
        """Get metrics summary."""
        print(f"\n{'='*60}")
        print("Metrics Summary")
        print(f"{'='*60}")

        metrics = self.metrics.get_metrics()

        print("\nCounters:")
        for name, value in metrics.get("counters", {}).items():
            print(f"  {name}: {value}")

        print("\nGauges:")
        for name, value in metrics.get("gauges", {}).items():
            print(f"  {name}: {value}")

        print("\nHistograms:")
        for name, stats in metrics.get("histograms", {}).items():
            print(f"  {name}:")
            print(f"    count: {stats['count']}")
            print(f"    mean: {stats['mean']:.3f}s")
            print(f"    min: {stats['min']:.3f}s")
            print(f"    max: {stats['max']:.3f}s")


def main():
    """Run complete application example."""
    try:
        # Initialize service
        service = BackendService()

        # Process some requests
        print("\n\n" + "🚀" * 30)
        print("Processing Sample Requests")
        print("🚀" * 30)

        # Valid request
        service.process_user_request(
            user_id=123,
            email="john.doe@example.com",
            username="johndoe",
        )

        # Same request (should hit cache)
        print("\n\n" + "-" * 60)
        print("Same request (testing cache)...")
        print("-" * 60)
        service.process_user_request(
            user_id=123,
            email="john.doe@example.com",
            username="johndoe",
        )

        # Invalid email
        print("\n\n" + "-" * 60)
        print("Testing validation (invalid email)...")
        print("-" * 60)
        try:
            service.process_user_request(
                user_id=456,
                email="invalid-email",
                username="janedoe",
            )
        except ValidationError:
            print("✓ Validation correctly rejected invalid email")

        # Show metrics
        service.get_metrics_summary()

        print("\n\n" + "✅" * 30)
        print("Complete Application Example Finished Successfully!")
        print("✅" * 30)

    except Exception as e:
        print(f"\n❌ Application error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
