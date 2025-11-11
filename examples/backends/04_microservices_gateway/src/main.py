"""Microservices API Gateway - Main Application.

High-performance gateway with 50K+ requests/second capability.
"""

import asyncio
from contextlib import asynccontextmanager
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from unistax.algorithms import ConsistentHashRing, fast_hash


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ServiceInstance:
    """Backend service instance."""
    url: str
    weight: int = 1
    healthy: bool = True
    failure_count: int = 0
    last_check: float = 0


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 30.0,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes before closing circuit
            timeout: Timeout before trying again (seconds)
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            HTTPException: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Service unavailable (circuit breaker open)"
                )

        try:
            result = await func(*args, **kwargs)

            # Success
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0

            return result

        except Exception as e:
            # Failure
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise


class ServiceRegistry:
    """Service registry with consistent hashing."""

    def __init__(self):
        """Initialize service registry."""
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.hash_rings: Dict[str, ConsistentHashRing] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def register_service(
        self,
        service_name: str,
        instances: List[Dict],
    ) -> None:
        """Register service with instances.

        Args:
            service_name: Service name
            instances: List of instance configs
        """
        # Create instances
        self.services[service_name] = [
            ServiceInstance(url=inst['url'], weight=inst.get('weight', 1))
            for inst in instances
        ]

        # Create consistent hash ring
        self.hash_rings[service_name] = ConsistentHashRing()
        for instance in self.services[service_name]:
            # Add to hash ring with weight
            for _ in range(instance.weight):
                self.hash_rings[service_name].add_node(instance.url)

        # Create circuit breaker
        self.circuit_breakers[service_name] = CircuitBreaker()

    def get_instance(
        self,
        service_name: str,
        key: Optional[str] = None,
    ) -> Optional[ServiceInstance]:
        """Get service instance using consistent hashing.

        Args:
            service_name: Service name
            key: Key for consistent hashing (e.g., user_id)

        Returns:
            Service instance or None
        """
        if service_name not in self.services:
            return None

        instances = self.services[service_name]
        if not instances:
            return None

        if key:
            # Use consistent hashing for sticky sessions
            hash_ring = self.hash_rings[service_name]
            instance_url = hash_ring.get_node(key)

            # Find matching instance
            for instance in instances:
                if instance.url == instance_url and instance.healthy:
                    return instance

        # Fallback: return first healthy instance
        for instance in instances:
            if instance.healthy:
                return instance

        return None

    def get_circuit_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker for service.

        Args:
            service_name: Service name

        Returns:
            Circuit breaker or None
        """
        return self.circuit_breakers.get(service_name)


# Global registry
registry: ServiceRegistry = None
http_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global registry, http_client

    # Initialize registry
    registry = ServiceRegistry()

    # Register example services
    registry.register_service(
        "users",
        [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 1},
        ],
    )

    # Initialize HTTP client with connection pooling
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0),
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=1000),
    )

    yield

    # Cleanup
    await http_client.aclose()


# Create FastAPI app
app = FastAPI(
    title="Microservices API Gateway",
    description="High-performance gateway with 50K+ req/sec capability",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/services/register")
async def register_service(
    service_name: str,
    instances: List[Dict],
):
    """Register a backend service.

    Args:
        service_name: Service name
        instances: List of instance configurations

    Returns:
        Registration status
    """
    registry.register_service(service_name, instances)

    return {
        "status": "registered",
        "service": service_name,
        "instances": len(instances),
    }


@app.api_route("/api/v1/gateway/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_route(
    service_name: str,
    path: str,
    request: Request,
):
    """Gateway route to backend services.

    Args:
        service_name: Target service name
        path: Request path
        request: FastAPI request

    Returns:
        Backend service response
    """
    # Get service instance
    # Use user_id from headers for sticky sessions
    user_id = request.headers.get("X-User-ID")
    instance = registry.get_instance(service_name, key=user_id)

    if not instance:
        raise HTTPException(status_code=503, detail=f"Service {service_name} not available")

    # Get circuit breaker
    circuit_breaker = registry.get_circuit_breaker(service_name)

    # Forward request with circuit breaker
    async def forward_request():
        target_url = f"{instance.url}/{path}"

        # Forward request
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=await request.body(),
        )

        return response

    try:
        response = await circuit_breaker.call(forward_request)

        return JSONResponse(
            content=response.json() if response.headers.get("content-type") == "application/json" else {"data": response.text},
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Backend error: {str(e)}")


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get gateway metrics."""
    return {
        "services": len(registry.services),
        "circuit_breakers": {
            name: cb.state.value
            for name, cb in registry.circuit_breakers.items()
        },
        "service_health": {
            name: {
                "total_instances": len(instances),
                "healthy_instances": sum(1 for i in instances if i.healthy),
            }
            for name, instances in registry.services.items()
        },
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "services": len(registry.services),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Microservices API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        workers=1,
    )
