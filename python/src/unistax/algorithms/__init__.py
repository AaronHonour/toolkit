"""High-performance algorithms and data structures module.

Optimized for 100K RPS with p99 < 100ms latency requirements.
All structures use __slots__ for memory efficiency and speed.
"""

from unistax.algorithms.compression import (
    AdaptiveCompressor,
    CompressionAlgorithm,
    CompressionLevel,
    FastCompressor,
    compress_for_network,
    compress_for_storage,
    decompress_from_storage,
    fast_compress,
    fast_decompress,
)
from unistax.algorithms.datastructures import (
    BloomFilter,
    FastDict,
    LRUCache,
    RingBuffer,
)
from unistax.algorithms.graph import (
    BlastRadiusResult,
    CircularDependency,
    CriticalityScore,
    calculate_blast_radius,
    calculate_service_criticality,
    compute_betweenness_centrality,
    compute_pagerank,
    detect_circular_dependencies,
    find_critical_path,
    tarjan_scc,
    topological_sort,
)
from unistax.algorithms.hashing import (
    ConsistentHashRing,
    FastHasher,
    consistent_hash,
    fast_hash,
    fast_hash_str,
    hash_combine,
    xxhash_fast,
)
from unistax.algorithms.pooling import (
    BufferPool,
    ObjectPool,
    ObjectPoolManager,
    PoolConfig,
    PooledObject,
)
from unistax.algorithms.serialization import (
    FastSerializer,
    SerializationFormat,
    deserialize_from_cache,
    fast_deserialize,
    fast_serialize,
    serialize_for_api,
    serialize_for_cache,
)

__all__ = [
    # Data structures
    "RingBuffer",
    "LRUCache",
    "BloomFilter",
    "FastDict",
    # Hashing
    "fast_hash",
    "fast_hash_str",
    "consistent_hash",
    "xxhash_fast",
    "hash_combine",
    "FastHasher",
    "ConsistentHashRing",
    # Serialization
    "fast_serialize",
    "fast_deserialize",
    "SerializationFormat",
    "FastSerializer",
    "serialize_for_cache",
    "deserialize_from_cache",
    "serialize_for_api",
    # Compression
    "fast_compress",
    "fast_decompress",
    "CompressionAlgorithm",
    "CompressionLevel",
    "FastCompressor",
    "compress_for_storage",
    "decompress_from_storage",
    "compress_for_network",
    "AdaptiveCompressor",
    # Pooling
    "ObjectPool",
    "PooledObject",
    "BufferPool",
    "ObjectPoolManager",
    "PoolConfig",
    # Graph algorithms
    "detect_circular_dependencies",
    "calculate_blast_radius",
    "compute_pagerank",
    "calculate_service_criticality",
    "compute_betweenness_centrality",
    "topological_sort",
    "find_critical_path",
    "CircularDependency",
    "BlastRadiusResult",
    "CriticalityScore",
    "tarjan_scc",
]
