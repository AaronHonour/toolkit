"""Probabilistic Data Structures Service.

All-in-one API for space-efficient probabilistic algorithms.
"""

from contextlib import asynccontextmanager
from collections import defaultdict
from typing import Dict, List, Optional, Set
import math

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from unistax.algorithms import BloomFilter, fast_hash


class CountMinSketch:
    """Count-Min Sketch for frequency estimation."""

    def __init__(self, width: int = 1000, depth: int = 5):
        """Initialize Count-Min Sketch.

        Args:
            width: Width of each array
            depth: Number of hash functions
        """
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]

    def add(self, item: str, count: int = 1) -> None:
        """Add item to sketch.

        Args:
            item: Item to add
            count: Count to add (default 1)
        """
        for i in range(self.depth):
            # Use fast_hash with different seeds (886K+ ops/sec)
            hash_val = fast_hash(f"{i}:{item}") % self.width
            self.table[i][hash_val] += count

    def estimate(self, item: str) -> int:
        """Estimate frequency of item.

        Args:
            item: Item to estimate

        Returns:
            Estimated frequency
        """
        estimates = []
        for i in range(self.depth):
            hash_val = fast_hash(f"{i}:{item}") % self.width
            estimates.append(self.table[i][hash_val])

        # Return minimum (conservative estimate)
        return min(estimates)


class HyperLogLog:
    """HyperLogLog for cardinality estimation."""

    def __init__(self, precision: int = 14):
        """Initialize HyperLogLog.

        Args:
            precision: Precision parameter (4-16)
        """
        self.precision = precision
        self.m = 1 << precision  # 2^precision
        self.registers = [0] * self.m

    def add(self, item: str) -> None:
        """Add item to HLL.

        Args:
            item: Item to add
        """
        # Hash item (886K+ ops/sec)
        hash_val = fast_hash(item)

        # Get register index (first p bits)
        j = hash_val & (self.m - 1)

        # Get leading zeros + 1 in remaining bits
        w = hash_val >> self.precision
        leading_zeros = self._leading_zeros(w) + 1

        # Update register
        if leading_zeros > self.registers[j]:
            self.registers[j] = leading_zeros

    def _leading_zeros(self, val: int) -> int:
        """Count leading zeros."""
        if val == 0:
            return 64
        count = 0
        mask = 1 << 63
        while (val & mask) == 0:
            count += 1
            mask >>= 1
        return count

    def cardinality(self) -> int:
        """Estimate cardinality.

        Returns:
            Estimated cardinality
        """
        # HLL estimation formula
        raw_estimate = self._alpha_m(self.m) * (self.m ** 2) / sum(2 ** (-x) for x in self.registers)

        # Apply corrections for small/large ranges
        if raw_estimate <= 2.5 * self.m:
            # Small range correction
            zeros = self.registers.count(0)
            if zeros != 0:
                return int(self.m * math.log(self.m / zeros))

        return int(raw_estimate)

    def _alpha_m(self, m: int) -> float:
        """Get alpha constant."""
        if m >= 128:
            return 0.7213 / (1 + 1.079 / m)
        elif m >= 64:
            return 0.709
        elif m >= 32:
            return 0.697
        elif m >= 16:
            return 0.673
        return 0.5


class ProbabilisticService:
    """Probabilistic data structures service."""

    def __init__(self):
        """Initialize service."""
        # Bloom filters
        self.bloom_filters: Dict[str, BloomFilter] = {}

        # Count-Min Sketches
        self.cm_sketches: Dict[str, CountMinSketch] = {}

        # HyperLogLogs
        self.hyperloglogs: Dict[str, HyperLogLog] = {}

    def get_or_create_bloom(self, name: str, size: int = 1_000_000) -> BloomFilter:
        """Get or create Bloom filter.

        Args:
            name: Filter name
            size: Expected elements

        Returns:
            Bloom filter
        """
        if name not in self.bloom_filters:
            self.bloom_filters[name] = BloomFilter(
                expected_elements=size,
                false_positive_rate=0.01
            )
        return self.bloom_filters[name]

    def get_or_create_cms(self, name: str) -> CountMinSketch:
        """Get or create Count-Min Sketch.

        Args:
            name: Sketch name

        Returns:
            Count-Min Sketch
        """
        if name not in self.cm_sketches:
            self.cm_sketches[name] = CountMinSketch()
        return self.cm_sketches[name]

    def get_or_create_hll(self, name: str) -> HyperLogLog:
        """Get or create HyperLogLog.

        Args:
            name: HLL name

        Returns:
            HyperLogLog
        """
        if name not in self.hyperloglogs:
            self.hyperloglogs[name] = HyperLogLog()
        return self.hyperloglogs[name]


service: Optional[ProbabilisticService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = ProbabilisticService()
    yield


app = FastAPI(
    title="Probabilistic Data Structures Service",
    description="Space-efficient probabilistic algorithms",
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


# Bloom Filter endpoints
@app.post("/api/v1/bloom/{name}/add")
async def bloom_add(name: str, item: str):
    """Add item to Bloom filter."""
    bloom = service.get_or_create_bloom(name)
    bloom.add(item)
    return {"status": "ok"}


@app.get("/api/v1/bloom/{name}/contains")
async def bloom_contains(name: str, item: str):
    """Check if item in Bloom filter."""
    bloom = service.get_or_create_bloom(name)
    contains = bloom.contains(item)
    return {"item": item, "probably_contains": contains}


# Count-Min Sketch endpoints
@app.post("/api/v1/cms/{name}/add")
async def cms_add(name: str, item: str, count: int = 1):
    """Add item to Count-Min Sketch."""
    cms = service.get_or_create_cms(name)
    cms.add(item, count)
    return {"status": "ok"}


@app.get("/api/v1/cms/{name}/estimate")
async def cms_estimate(name: str, item: str):
    """Estimate frequency from Count-Min Sketch."""
    cms = service.get_or_create_cms(name)
    freq = cms.estimate(item)
    return {"item": item, "estimated_frequency": freq}


# HyperLogLog endpoints
@app.post("/api/v1/hll/{name}/add")
async def hll_add(name: str, item: str):
    """Add item to HyperLogLog."""
    hll = service.get_or_create_hll(name)
    hll.add(item)
    return {"status": "ok"}


@app.get("/api/v1/hll/{name}/cardinality")
async def hll_cardinality(name: str):
    """Get cardinality estimate from HyperLogLog."""
    hll = service.get_or_create_hll(name)
    card = hll.cardinality()
    return {"estimated_cardinality": card}


@app.get("/api/v1/stats")
async def stats():
    """Get service statistics."""
    return {
        "bloom_filters": len(service.bloom_filters),
        "count_min_sketches": len(service.cm_sketches),
        "hyperloglogs": len(service.hyperloglogs),
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Probabilistic Data Structures Service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8019)
