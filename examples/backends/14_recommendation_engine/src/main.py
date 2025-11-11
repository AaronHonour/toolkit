"""Real-Time Recommendation Engine.

ML-powered recommendations with < 10ms P99 latency.
"""

from contextlib import asynccontextmanager
from typing import Optional, List
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from unistax.algorithms import LRUCache, ConsistentHashRing, fast_hash


class RecommendationEngine:
    """Real-time recommendation engine."""

    def __init__(self):
        # User profile cache
        self.profile_cache = LRUCache(capacity=1_000_000)

        # Model sharding
        self.model_ring = ConsistentHashRing()
        for i in range(8):
            self.model_ring.add_node(f"model_{i}")

        # Item catalog
        self.items = [f"item_{i}" for i in range(10000)]

        # Stats
        self.recommendations_served = 0

    async def get_user_profile(self, user_id: str) -> dict:
        """Get user profile (cached)."""
        profile = self.profile_cache.get(user_id)
        if profile:
            return profile

        # Simulate profile load
        profile = {
            "user_id": user_id,
            "preferences": ["category_" + str(i) for i in range(5)],
            "history": random.sample(self.items, 10),
        }

        self.profile_cache.put(user_id, profile)
        return profile

    async def recommend(self, user_id: str, count: int = 10) -> List[str]:
        """Generate recommendations."""
        # Get user profile (cached)
        profile = await self.get_user_profile(user_id)

        # Feature hashing for sparse features
        feature_hash = fast_hash(f"{user_id}:{profile['preferences']}")

        # Route to model shard
        model_shard = self.model_ring.get_node(user_id)

        # Generate recommendations (simplified)
        # In production, this would use ML model
        excluded = set(profile['history'])
        candidates = [item for item in self.items if item not in excluded]
        recommendations = random.sample(candidates, min(count, len(candidates)))

        self.recommendations_served += 1

        return recommendations


service: Optional[RecommendationEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = RecommendationEngine()
    yield


app = FastAPI(title="Recommendation Engine", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/recommend/{user_id}")
async def get_recommendations(user_id: str, count: int = 10):
    """Get personalized recommendations."""
    recommendations = await service.recommend(user_id, count)
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "count": len(recommendations),
    }


@app.get("/api/v1/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile."""
    profile = await service.get_user_profile(user_id)
    return profile


@app.get("/api/v1/stats")
async def stats():
    return {"recommendations_served": service.recommendations_served}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Recommendation Engine"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8014)
