"""
Tests for weekseries_downloader.infrastructure.cache_manager module
"""

import pytest
import time
from unittest.mock import patch
from weekseries_downloader.infrastructure.cache_manager import CacheManager, CacheEntry


class TestCacheEntry:
    """Tests for CacheEntry dataclass"""

    def test_cache_entry_creation(self):
        """Test CacheEntry creation"""
        entry = CacheEntry(value="test_value", timestamp=1000.0, ttl=300.0)

        assert entry.value == "test_value"
        assert entry.timestamp == 1000.0
        assert entry.ttl == 300.0

    @patch("time.time", return_value=1200.0)
    def test_cache_entry_not_expired(self, mock_time):
        """Test CacheEntry is_expired property when not expired"""
        entry = CacheEntry(value="test_value", timestamp=1000.0, ttl=300.0)  # Expires at 1300.0

        assert entry.is_expired is False

    @patch("time.time", return_value=1400.0)
    def test_cache_entry_expired(self, mock_time):
        """Test CacheEntry is_expired property when expired"""
        entry = CacheEntry(value="test_value", timestamp=1000.0, ttl=300.0)  # Expires at 1300.0

        assert entry.is_expired is True

    @patch("time.time", return_value=1300.0)
    def test_cache_entry_exactly_expired(self, mock_time):
        """Test CacheEntry is_expired property at exact expiration time"""
        entry = CacheEntry(value="test_value", timestamp=1000.0, ttl=300.0)  # Expires at 1300.0

        assert entry.is_expired is False  # Should not be expired at exact time


class TestCacheManager:
    """Tests for CacheManager class"""

    def test_cache_manager_creation(self):
        """Test CacheManager creation with default TTL"""
        cache = CacheManager()
        assert cache._default_ttl == 600  # 10 minutes default
        assert len(cache._cache) == 0

    def test_cache_manager_creation_custom_ttl(self):
        """Test CacheManager creation with custom TTL"""
        cache = CacheManager(default_ttl=600)
        assert cache._default_ttl == 600

    def test_cache_manager_set_and_get(self):
        """Test basic set and get operations"""
        cache = CacheManager()

        result = cache.set("key1", "value1")
        assert result is True

        value = cache.get("key1")
        assert value == "value1"

    def test_simple_cache_get_nonexistent_key(self):
        """Test get with nonexistent key"""
        cache = CacheManager()

        value = cache.get("nonexistent")
        assert value is None

    def test_simple_cache_set_empty_key(self):
        """Test set with empty key"""
        cache = CacheManager()

        result = cache.set("", "value")
        assert result is False

    def test_simple_cache_set_none_key(self):
        """Test set with None key"""
        cache = CacheManager()

        result = cache.set(None, "value")
        assert result is False

    def test_simple_cache_set_none_value(self):
        """Test set with None value"""
        cache = CacheManager()

        result = cache.set("key", None)
        assert result is False

    def test_simple_cache_get_empty_key(self):
        """Test get with empty key"""
        cache = CacheManager()

        value = cache.get("")
        assert value is None

    def test_simple_cache_get_none_key(self):
        """Test get with None key"""
        cache = CacheManager()

        value = cache.get(None)
        assert value is None

    @patch("time.time", return_value=1000.0)
    def test_simple_cache_set_custom_ttl(self, mock_time):
        """Test set with custom TTL"""
        cache = SimpleCache(default_ttl=300)

        result = cache.set("key1", "value1", ttl=600)
        assert result is True

        # Check that custom TTL was used
        entry = cache._cache["key1"]
        assert entry.ttl == 600

    @patch("time.time")
    def test_simple_cache_expiration(self, mock_time):
        """Test cache expiration behavior"""
        cache = SimpleCache(default_ttl=300)

        # Set initial time
        mock_time.return_value = 1000.0
        cache.set("key1", "value1")

        # Before expiration
        mock_time.return_value = 1200.0
        value = cache.get("key1")
        assert value == "value1"

        # After expiration
        mock_time.return_value = 1400.0
        value = cache.get("key1")
        assert value is None

        # Key should be removed from cache
        assert "key1" not in cache._cache

    def test_simple_cache_clear(self):
        """Test cache clear operation"""
        cache = CacheManager()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.size == 2

        cache.clear()
        assert cache.size == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    @patch("time.time")
    def test_simple_cache_cleanup_expired(self, mock_time):
        """Test cleanup of expired entries"""
        cache = SimpleCache(default_ttl=300)

        # Set initial time and add entries
        mock_time.return_value = 1000.0
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Move time forward to expire some entries
        mock_time.return_value = 1400.0  # key1, key2, key3 should be expired

        # Add a new entry that's not expired
        cache.set("key4", "value4")

        # Cleanup expired entries
        removed_count = cache.cleanup_expired()

        assert removed_count == 3  # key1, key2, key3 were removed
        assert len(cache._cache) == 1  # Only key4 remains
        assert cache.get("key4") == "value4"

    def test_cache_manager_size_property(self):
        """Test cache size property"""
        cache = CacheManager()

        assert len(cache._cache) == 0

        cache.set("key1", "value1")
        assert len(cache._cache) == 1

        cache.set("key2", "value2")
        assert len(cache._cache) == 2

        cache.clear()
        assert len(cache._cache) == 0

    def test_cache_manager_overwrite_existing_key(self):
        """Test overwriting existing key"""
        cache = CacheManager()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.set("key1", "new_value")
        assert cache.get("key1") == "new_value"
        assert len(cache._cache) == 1  # Size should remain 1


class TestCacheManagerIntegration:
    """Integration tests for CacheManager"""

    def test_cache_integration_workflow(self):
        """Test complete cache workflow"""
        cache = CacheManager()

        page_url = "https://www.weekseries.info/series/breaking-bad/temporada-5/episodio-16"
        stream_url = "https://cdn.example.com/breaking-bad/s05e16/stream.m3u8"

        # Initially no cache
        assert cache.get(page_url) is None

        # Cache the URL
        assert cache.set(page_url, stream_url) is True

        # Verify it's cached
        assert cache.get(page_url) == stream_url

        # Clear and verify
        cache.clear()
        assert cache.get(page_url) is None
        assert len(cache._cache) == 0
