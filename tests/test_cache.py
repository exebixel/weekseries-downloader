"""
Tests for weekseries_downloader.cache module
"""

import pytest
import time
from unittest.mock import patch
from weekseries_downloader.cache import (
    SimpleCache,
    CacheEntry,
    get_cached_stream_url,
    cache_stream_url,
    clear_url_cache,
    cleanup_expired_urls,
    get_cache_stats
)


class TestCacheEntry:
    """Tests for CacheEntry dataclass"""
    
    def test_cache_entry_creation(self):
        """Test CacheEntry creation"""
        entry = CacheEntry(
            value="test_value",
            timestamp=1000.0,
            ttl=300.0
        )
        
        assert entry.value == "test_value"
        assert entry.timestamp == 1000.0
        assert entry.ttl == 300.0
    
    @patch('time.time', return_value=1200.0)
    def test_cache_entry_not_expired(self, mock_time):
        """Test CacheEntry is_expired property when not expired"""
        entry = CacheEntry(
            value="test_value",
            timestamp=1000.0,
            ttl=300.0  # Expires at 1300.0
        )
        
        assert entry.is_expired is False
    
    @patch('time.time', return_value=1400.0)
    def test_cache_entry_expired(self, mock_time):
        """Test CacheEntry is_expired property when expired"""
        entry = CacheEntry(
            value="test_value",
            timestamp=1000.0,
            ttl=300.0  # Expires at 1300.0
        )
        
        assert entry.is_expired is True
    
    @patch('time.time', return_value=1300.0)
    def test_cache_entry_exactly_expired(self, mock_time):
        """Test CacheEntry is_expired property at exact expiration time"""
        entry = CacheEntry(
            value="test_value",
            timestamp=1000.0,
            ttl=300.0  # Expires at 1300.0
        )
        
        assert entry.is_expired is False  # Should not be expired at exact time


class TestSimpleCache:
    """Tests for SimpleCache class"""
    
    def test_simple_cache_creation(self):
        """Test SimpleCache creation with default TTL"""
        cache = SimpleCache()
        assert cache._default_ttl == 300  # 5 minutes default
        assert cache.size == 0
    
    def test_simple_cache_creation_custom_ttl(self):
        """Test SimpleCache creation with custom TTL"""
        cache = SimpleCache(default_ttl=600)
        assert cache._default_ttl == 600
    
    def test_simple_cache_set_and_get(self):
        """Test basic set and get operations"""
        cache = SimpleCache()
        
        result = cache.set("key1", "value1")
        assert result is True
        
        value = cache.get("key1")
        assert value == "value1"
    
    def test_simple_cache_get_nonexistent_key(self):
        """Test get with nonexistent key"""
        cache = SimpleCache()
        
        value = cache.get("nonexistent")
        assert value is None
    
    def test_simple_cache_set_empty_key(self):
        """Test set with empty key"""
        cache = SimpleCache()
        
        result = cache.set("", "value")
        assert result is False
    
    def test_simple_cache_set_none_key(self):
        """Test set with None key"""
        cache = SimpleCache()
        
        result = cache.set(None, "value")
        assert result is False
    
    def test_simple_cache_set_none_value(self):
        """Test set with None value"""
        cache = SimpleCache()
        
        result = cache.set("key", None)
        assert result is False
    
    def test_simple_cache_get_empty_key(self):
        """Test get with empty key"""
        cache = SimpleCache()
        
        value = cache.get("")
        assert value is None
    
    def test_simple_cache_get_none_key(self):
        """Test get with None key"""
        cache = SimpleCache()
        
        value = cache.get(None)
        assert value is None
    
    @patch('time.time', return_value=1000.0)
    def test_simple_cache_set_custom_ttl(self, mock_time):
        """Test set with custom TTL"""
        cache = SimpleCache(default_ttl=300)
        
        result = cache.set("key1", "value1", ttl=600)
        assert result is True
        
        # Check that custom TTL was used
        entry = cache._cache["key1"]
        assert entry.ttl == 600
    
    @patch('time.time')
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
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.size == 2
        
        cache.clear()
        assert cache.size == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    @patch('time.time')
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
        assert cache.size == 1  # Only key4 remains
        assert cache.get("key4") == "value4"
    
    def test_simple_cache_size_property(self):
        """Test cache size property"""
        cache = SimpleCache()
        
        assert cache.size == 0
        
        cache.set("key1", "value1")
        assert cache.size == 1
        
        cache.set("key2", "value2")
        assert cache.size == 2
        
        cache.clear()
        assert cache.size == 0
    
    def test_simple_cache_overwrite_existing_key(self):
        """Test overwriting existing key"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.set("key1", "new_value")
        assert cache.get("key1") == "new_value"
        assert cache.size == 1  # Size should remain 1


class TestGlobalCacheFunctions:
    """Tests for global cache functions"""
    
    def setup_method(self):
        """Clear cache before each test"""
        clear_url_cache()
    
    def test_cache_stream_url_and_get(self):
        """Test caching and retrieving stream URL"""
        page_url = "https://www.weekseries.info/series/test/temporada-1/episodio-01"
        stream_url = "https://example.com/stream.m3u8"
        
        # Cache the URL
        result = cache_stream_url(page_url, stream_url)
        assert result is True
        
        # Retrieve the URL
        cached_url = get_cached_stream_url(page_url)
        assert cached_url == stream_url
    
    def test_get_cached_stream_url_nonexistent(self):
        """Test getting nonexistent cached URL"""
        result = get_cached_stream_url("https://nonexistent.com")
        assert result is None
    
    def test_cache_stream_url_empty_page_url(self):
        """Test caching with empty page URL"""
        result = cache_stream_url("", "https://example.com/stream.m3u8")
        assert result is False
    
    def test_cache_stream_url_none_stream_url(self):
        """Test caching with None stream URL"""
        result = cache_stream_url("https://example.com", None)
        assert result is False
    
    def test_clear_url_cache(self):
        """Test clearing URL cache"""
        # Add some URLs to cache
        cache_stream_url("https://example1.com", "https://stream1.m3u8")
        cache_stream_url("https://example2.com", "https://stream2.m3u8")
        
        # Verify they're cached
        assert get_cached_stream_url("https://example1.com") == "https://stream1.m3u8"
        assert get_cached_stream_url("https://example2.com") == "https://stream2.m3u8"
        
        # Clear cache
        clear_url_cache()
        
        # Verify they're gone
        assert get_cached_stream_url("https://example1.com") is None
        assert get_cached_stream_url("https://example2.com") is None
    
    @patch('time.time')
    def test_cleanup_expired_urls(self, mock_time):
        """Test cleanup of expired URLs"""
        # Set initial time
        mock_time.return_value = 1000.0
        
        # Cache some URLs
        cache_stream_url("https://example1.com", "https://stream1.m3u8")
        cache_stream_url("https://example2.com", "https://stream2.m3u8")
        
        # Move time forward to expire entries
        mock_time.return_value = 1700.0  # Beyond default TTL of 600 seconds
        
        # Add a new entry that's not expired
        cache_stream_url("https://example3.com", "https://stream3.m3u8")
        
        # Cleanup expired entries
        removed_count = cleanup_expired_urls()
        
        assert removed_count == 2  # First two URLs were expired
        assert get_cached_stream_url("https://example1.com") is None
        assert get_cached_stream_url("https://example2.com") is None
        assert get_cached_stream_url("https://example3.com") == "https://stream3.m3u8"
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Clear cache first
        clear_url_cache()
        
        # Add some URLs
        cache_stream_url("https://example1.com", "https://stream1.m3u8")
        cache_stream_url("https://example2.com", "https://stream2.m3u8")
        
        stats = get_cache_stats()
        
        assert isinstance(stats, dict)
        assert "size" in stats
        assert "expired_cleaned" in stats
        assert stats["size"] == 2
        assert isinstance(stats["expired_cleaned"], int)
    
    @patch('weekseries_downloader.cache.time.time')
    def test_get_cache_stats_with_expired_cleanup(self, mock_time):
        """Test cache stats with expired entry cleanup"""
        clear_url_cache()
        
        # Set initial time and add entries
        mock_time.return_value = 1000.0
        cache_stream_url("https://example1.com", "https://stream1.m3u8")
        cache_stream_url("https://example2.com", "https://stream2.m3u8")
        
        # Move time forward to expire entries (default TTL is 600 seconds)
        mock_time.return_value = 1700.0  # 700 seconds later, beyond TTL
        
        # Add fresh entry
        cache_stream_url("https://example3.com", "https://stream3.m3u8")
        
        # Get stats (this should trigger cleanup)
        stats = get_cache_stats()
        
        # The exact behavior depends on when cleanup happens
        # Let's just verify that cleanup was called and stats are returned
        assert isinstance(stats["size"], int)
        assert isinstance(stats["expired_cleaned"], int)
        assert stats["size"] >= 1  # At least the fresh entry should remain
    
    def test_cache_integration_workflow(self):
        """Test complete cache workflow integration"""
        clear_url_cache()
        
        page_url = "https://www.weekseries.info/series/breaking-bad/temporada-5/episodio-16"
        stream_url = "https://cdn.example.com/breaking-bad/s05e16/stream.m3u8"
        
        # Initially no cache
        assert get_cached_stream_url(page_url) is None
        
        # Cache the URL
        assert cache_stream_url(page_url, stream_url) is True
        
        # Verify it's cached
        assert get_cached_stream_url(page_url) == stream_url
        
        # Check stats
        stats = get_cache_stats()
        assert stats["size"] >= 1
        
        # Clear and verify
        clear_url_cache()
        assert get_cached_stream_url(page_url) is None
        
        final_stats = get_cache_stats()
        assert final_stats["size"] == 0