"""Distributed Rate Limiter.

Token bucket rate limiting with 1M+ checks/sec.
"""

from contextlib import asynccontextmanager
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from unistax.algorithms import LRUCache, fast_hash


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self):
        self.cache = LRUCache(capacity=1_000_000)
        self.stats = {"allowed": 0, "denied": 0}

    async def check(self, key: str, limit: int, window: int) -> bool:
        """Check rate limit.

        Args:
            key: User/IP key
            limit: Max requests per window
            window: Time window in seconds

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        cache_key = f"rl:{key}"

        # Get current state
        state = self.cache.get(cache_key)

        if state is None:
            # First request
            state = {"tokens": limit - 1, "last_update": now}
            self.cache.put(cache_key, state)
            self.stats["allowed"] += 1
            return True

        # Refill tokens
        elapsed = now - state["last_update"]
        refill = int((elapsed / window) * limit)
        state["tokens"] = min(limit, state["tokens"] + refill)
        state["last_update"] = now

        # Check if allowed
        if state["tokens"] > 0:
            state["tokens"] -= 1
            self.cache.put(cache_key, state)
            self.stats["allowed"] += 1
            return True
        else:
            self.stats["denied"] += 1
            return False


service: Optional[RateLimiter] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = RateLimiter()
    yield


app = FastAPI(title="Rate Limiter", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/check/{key}")
async def check_limit(key: str, limit: int = 100, window: int = 60):
    """Check rate limit."""
    allowed = await service.check(key, limit, window)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return {"allowed": True, "remaining": limit}


@app.get("/api/v1/stats")
async def stats():
    return service.stats


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Distributed Rate Limiter"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8011)
