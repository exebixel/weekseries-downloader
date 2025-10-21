"""
Cache management system with TTL support
"""

import time
from typing import Optional, Dict, Any
import logging

from weekseries_downloader.models import CacheEntry


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
            return None

        if key not in self._cache:
            return None

        entry = self._cache[key]

        if entry.is_expired:
            # Remove expired entry
            del self._cache[key]
            self.logger.debug(f"Cache entry expired: {key}")
            return None

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
