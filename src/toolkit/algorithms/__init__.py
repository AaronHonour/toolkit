"""High-performance algorithms and data structures module.

Optimized for 100K RPS with p99 < 100ms latency requirements.
All structures use __slots__ for memory efficiency and speed.
"""

from toolkit.algorithms.datastructures import (
    RingBuffer,
    LRUCache,
    BloomFilter,
    FastDict,
)
from toolkit.algorithms.hashing import (
    fast_hash,
    fast_hash_str,
    consistent_hash,
    xxhash_fast,
    hash_combine,
    FastHasher,
)
from toolkit.algorithms.serialization import (
    fast_serialize,
    fast_deserialize,
    SerializationFormat,
    FastSerializer,
    serialize_for_cache,
    deserialize_from_cache,
    serialize_for_api,
)
from toolkit.algorithms.compression import (
    fast_compress,
    fast_decompress,
    CompressionAlgorithm,
    CompressionLevel,
    FastCompressor,
    compress_for_storage,
    decompress_from_storage,
    compress_for_network,
    AdaptiveCompressor,
)
from toolkit.algorithms.pooling import (
    ObjectPool,
    PooledObject,
    BufferPool,
    ObjectPoolManager,
    PoolConfig,
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
]
