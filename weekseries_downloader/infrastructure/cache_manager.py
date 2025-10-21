"""
Cache management system with TTL support
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging


@dataclass
class CacheEntry:
    """Cache entry with timestamp"""

    value: Any
    timestamp: float
    ttl: float  # Time to live in seconds

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() > (self.timestamp + self.ttl)


class CacheManager:
    """In-memory cache with TTL support"""

    def __init__(self, default_ttl: float = 600):
        """
        Initialize cache with TTL in seconds (default: 10 minutes)

        Args:
            default_ttl: Default time to live in seconds
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self.logger = logging.getLogger(__name__)

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if exists and not expired

        Args:
            key: Cache key

        Returns:
            Stored value or None if not found/expired
        """
        if not key:
            self._misses += 1
            return None

        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        if entry.is_expired:
            # Remove expired entry
            del self._cache[key]
            self._misses += 1
            self.logger.debug(f"Cache entry expired: {key}")
            return None

        self._hits += 1
        self.logger.debug(f"Cache hit: {key}")
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Store value in cache with TTL

        Args:
            key: Cache key
            value: Value to store
            ttl: Custom time to live (uses default if not specified)

        Returns:
            True if stored successfully
        """
        if not key:
            return False

        if value is None:
            return False

        effective_ttl = ttl or self._default_ttl

        self._cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=effective_ttl)

        self.logger.debug(f"Cache set: {key} (TTL: {effective_ttl}s)")
        return True

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self.logger.debug("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

        return len(expired_keys)

    @property
    def size(self) -> int:
        """
        Get number of entries in cache

        Returns:
            Number of cached entries
        """
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dict with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {"size": self.size, "hits": self._hits, "misses": self._misses, "hit_rate": f"{hit_rate:.2f}%"}
