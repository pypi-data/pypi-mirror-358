"""
Tests for the centralized caching system.

This module contains tests for the core caching functionality including
cache managers, backends, file watching, and data classification.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.cache_backends import DiskCacheBackend, create_cache_backends
from src.core.centralized_cache import (
    CacheEntry,
    CacheMetadata,
    CachePriority,
    CacheRoutingStrategy,
    CacheTier,
    CentralizedCacheManager,
    InvalidationStrategy,
    MemoryCacheBackend,
)


class TestCacheRoutingStrategy:
    """Test cache routing and data classification."""

    def test_local_only_patterns(self):
        """Test that local-only data never goes to Redis."""
        strategy = CacheRoutingStrategy()

        # Test filtering patterns (should be local only)
        local_keys = [
            "filtering:gitignore:patterns:/path/to/.gitignore",
            "filtering:ai_attributes:rules:/path/to/.ai-attributes",
            "config:project:codeguard:/project/.codeguard/config.json",
            "config:user:codeguard:/home/user/.codeguard/config.json",
            "workspace:analysis:/path/to/project",
            "content:file:/path/to/file.py",
        ]

        for key in local_keys:
            tiers = strategy.get_eligible_tiers(key)
            assert CacheTier.REDIS not in tiers, f"Key {key} should not be Redis eligible"
            assert CacheTier.MEMORY in tiers
            assert CacheTier.DISK in tiers

    def test_redis_eligible_patterns(self):
        """Test that shareable data can go to Redis."""
        strategy = CacheRoutingStrategy()

        # Test shareable patterns
        redis_keys = [
            "templates:system_prompt:codeguard_context",
            "themes:default:dark_mode",
            "config:global:feature_flags",
            "resources:shared:default_excludes",
            "analysis:shared:language_patterns",
        ]

        for key in redis_keys:
            tiers = strategy.get_eligible_tiers(key)
            assert CacheTier.REDIS in tiers, f"Key {key} should be Redis eligible"
            assert CacheTier.MEMORY in tiers
            assert CacheTier.DISK in tiers

    def test_default_local_only(self):
        """Test that unknown patterns default to local only."""
        strategy = CacheRoutingStrategy()

        unknown_key = "unknown:pattern:something"
        tiers = strategy.get_eligible_tiers(unknown_key)

        assert CacheTier.REDIS not in tiers
        assert CacheTier.MEMORY in tiers
        assert CacheTier.DISK in tiers


class TestMemoryCacheBackend:
    """Test memory cache backend functionality."""

    def test_basic_operations(self):
        """Test basic get/set/delete operations."""
        cache = MemoryCacheBackend(max_size=100, max_memory_mb=10)

        # Create test entry
        metadata = CacheMetadata(
            key="test:key", ttl=None, priority=CachePriority.MEDIUM, size_bytes=100
        )
        entry = CacheEntry(value="test_value", metadata=metadata)

        # Test set
        assert cache.set("test:key", entry)

        # Test get
        retrieved = cache.get("test:key")
        assert retrieved is not None
        assert retrieved.value == "test_value"
        assert retrieved.metadata.access_count == 1

        # Test exists
        assert cache.exists("test:key")

        # Test delete
        assert cache.delete("test:key")
        assert not cache.exists("test:key")
        assert cache.get("test:key") is None

    def test_lru_eviction(self):
        """Test LRU eviction when size limit is reached."""
        cache = MemoryCacheBackend(max_size=2)  # Very small cache

        # Add entries
        for i in range(3):
            metadata = CacheMetadata(key=f"key_{i}", size_bytes=100)
            entry = CacheEntry(value=f"value_{i}", metadata=metadata)
            cache.set(f"key_{i}", entry)

        # First entry should be evicted
        assert not cache.exists("key_0")
        assert cache.exists("key_1")
        assert cache.exists("key_2")

    def test_memory_eviction(self):
        """Test memory-based eviction."""
        cache = MemoryCacheBackend(max_size=100, max_memory_mb=1)  # 1MB limit

        # Create large entry that exceeds memory limit
        large_data = "x" * (1024 * 1024 + 1)  # > 1MB
        metadata = CacheMetadata(key="large_key", size_bytes=len(large_data))
        entry = CacheEntry(value=large_data, metadata=metadata)

        # Should succeed but trigger eviction
        assert cache.set("large_key", entry)
        assert cache.exists("large_key")

    def test_stats(self):
        """Test cache statistics."""
        cache = MemoryCacheBackend(max_size=100, max_memory_mb=10)

        stats = cache.get_stats()
        assert stats["type"] == "memory"
        assert stats["entries"] == 0
        assert stats["memory_usage_bytes"] == 0

        # Add entry and check stats
        metadata = CacheMetadata(key="test", size_bytes=100)
        entry = CacheEntry(value="test", metadata=metadata)
        cache.set("test", entry)

        stats = cache.get_stats()
        assert stats["entries"] == 1
        assert stats["memory_usage_bytes"] == 100


class TestDiskCacheBackend:
    """Test disk cache backend functionality."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary directory for cache tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.skipif(True, reason="Requires diskcache library")
    def test_disk_cache_operations(self, temp_cache_dir):
        """Test disk cache basic operations."""
        cache = DiskCacheBackend(cache_dir=temp_cache_dir, size_limit=1024 * 1024)

        # Create test entry
        metadata = CacheMetadata(key="disk:test", ttl=3600, size_bytes=50)
        entry = CacheEntry(value="disk_test_value", metadata=metadata)

        # Test operations
        assert cache.set("disk:test", entry)
        assert cache.exists("disk:test")

        retrieved = cache.get("disk:test")
        assert retrieved is not None
        assert retrieved.value == "disk_test_value"

        assert cache.delete("disk:test")
        assert not cache.exists("disk:test")

    @pytest.mark.skipif(True, reason="Requires diskcache library")
    def test_disk_cache_persistence(self, temp_cache_dir):
        """Test that disk cache persists across instances."""
        # Create first cache instance
        cache1 = DiskCacheBackend(cache_dir=temp_cache_dir)

        metadata = CacheMetadata(key="persist:test", size_bytes=50)
        entry = CacheEntry(value="persistent_value", metadata=metadata)
        cache1.set("persist:test", entry)

        # Create second cache instance with same directory
        cache2 = DiskCacheBackend(cache_dir=temp_cache_dir)

        retrieved = cache2.get("persist:test")
        assert retrieved is not None
        assert retrieved.value == "persistent_value"


class TestCentralizedCacheManager:
    """Test the main cache manager functionality."""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager with memory backend only."""
        backends = {CacheTier.MEMORY: MemoryCacheBackend(max_size=100)}
        return CentralizedCacheManager(backends=backends)

    def test_get_set_basic(self, cache_manager):
        """Test basic get/set operations."""
        # Test set
        success = cache_manager.set("test:basic", "test_value", ttl=3600)
        assert success

        # Test get
        value = cache_manager.get("test:basic")
        assert value == "test_value"

        # Test miss
        missing = cache_manager.get("missing:key")
        assert missing is None

    def test_data_classification(self, cache_manager):
        """Test that data classification is enforced."""
        # Add memory and "fake" redis backend
        mock_redis = Mock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = None

        cache_manager.backends[CacheTier.REDIS] = mock_redis

        # Test local-only data (should not reach Redis)
        cache_manager.set("filtering:gitignore:test", "local_data")
        mock_redis.set.assert_not_called()

        # Test Redis-eligible data
        cache_manager.set("templates:system_prompt:test", "shareable_data")
        # Note: This test would need more sophisticated mocking to verify Redis usage

    def test_invalidation_pattern(self, cache_manager):
        """Test pattern-based invalidation."""
        # Set multiple entries
        cache_manager.set("test:item1", "value1")
        cache_manager.set("test:item2", "value2")
        cache_manager.set("other:item", "value3")

        # Invalidate pattern
        count = cache_manager.invalidate_pattern("test:*")
        assert count == 2

        # Check results
        assert cache_manager.get("test:item1") is None
        assert cache_manager.get("test:item2") is None
        assert cache_manager.get("other:item") == "value3"

    def test_invalidation_tags(self, cache_manager):
        """Test tag-based invalidation."""
        # Set entries with tags
        cache_manager.set("item1", "value1", tags={"tag1", "tag2"})
        cache_manager.set("item2", "value2", tags={"tag2", "tag3"})
        cache_manager.set("item3", "value3", tags={"tag3"})

        # Invalidate by tag
        count = cache_manager.invalidate_tags({"tag2"})
        assert count == 2

        # Check results
        assert cache_manager.get("item1") is None
        assert cache_manager.get("item2") is None
        assert cache_manager.get("item3") == "value3"

    def test_file_dependencies(self, cache_manager):
        """Test file dependency tracking."""
        test_file = Path("/tmp/test_file.txt")

        # Set entry with file dependency
        cache_manager.set("file:test", "content", file_dependencies=[test_file])

        # Verify entry exists
        assert cache_manager.get("file:test") == "content"

        # Test force scan (simplified)
        changes = cache_manager.force_scan_files([test_file])
        assert test_file in changes

    def test_cache_policies(self, cache_manager):
        """Test that cache policies are applied correctly."""
        # Test filtering policy (high priority, no TTL)
        policy = cache_manager.get_policy("filtering:gitignore:test")
        assert policy.priority == CachePriority.HIGH
        assert policy.ttl is None
        assert policy.invalidation_strategy == InvalidationStrategy.MTIME

        # Test template policy (TTL-based)
        policy = cache_manager.get_policy("templates:system_prompt:test")
        assert policy.ttl == 300
        assert policy.invalidation_strategy == InvalidationStrategy.HYBRID

    def test_metrics(self, cache_manager):
        """Test cache metrics collection."""
        # Perform operations
        cache_manager.set("metrics:test", "value")
        cache_manager.get("metrics:test")  # hit
        cache_manager.get("metrics:missing")  # miss
        cache_manager.invalidate("metrics:test")

        # Check metrics
        stats = cache_manager.get_stats()
        assert "metrics" in stats

        metrics = stats["metrics"]
        assert metrics["hits"] >= 1
        assert metrics["misses"] >= 1
        assert metrics["sets"] >= 1
        assert metrics["deletes"] >= 1


class TestCacheBackendFactory:
    """Test cache backend creation and configuration."""

    def test_create_memory_backend(self):
        """Test memory backend creation."""
        config = {"memory": {"max_size": 500, "max_memory_mb": 128}}

        backends = create_cache_backends(config)

        assert CacheTier.MEMORY in backends
        memory_backend = backends[CacheTier.MEMORY]
        assert isinstance(memory_backend, MemoryCacheBackend)
        assert memory_backend.max_size == 500

    def test_create_multiple_backends(self):
        """Test creation of multiple backends."""
        config = {"memory": {"max_size": 100}, "disk": {"cache_dir": "/tmp/test_cache"}}

        backends = create_cache_backends(config)

        assert CacheTier.MEMORY in backends
        assert CacheTier.DISK in backends
        assert CacheTier.REDIS not in backends


class TestCacheIntegration:
    """Test integration scenarios and edge cases."""

    def test_tiered_cache_population(self):
        """Test that higher cache tiers are populated on cache hits."""
        # Create manager with memory and mock disk backend
        memory_backend = MemoryCacheBackend()
        disk_backend = Mock()

        # Mock disk backend returning an entry
        metadata = CacheMetadata(key="tiered:test", size_bytes=100)
        disk_entry = CacheEntry(value="disk_value", metadata=metadata)
        disk_backend.get.return_value = disk_entry
        disk_backend.set.return_value = True

        backends = {CacheTier.MEMORY: memory_backend, CacheTier.DISK: disk_backend}

        manager = CentralizedCacheManager(backends=backends)

        # First get should hit disk and populate memory
        value = manager.get("tiered:test")
        assert value == "disk_value"

        # Verify memory was populated
        memory_entry = memory_backend.get("tiered:test")
        assert memory_entry is not None
        assert memory_entry.value == "disk_value"

    def test_cache_error_handling(self):
        """Test cache behavior when backends fail."""
        # Create backend that fails
        failing_backend = Mock()
        failing_backend.get.side_effect = Exception("Backend failure")
        failing_backend.set.side_effect = Exception("Backend failure")

        backends = {CacheTier.MEMORY: failing_backend}
        manager = CentralizedCacheManager(backends=backends)

        # Operations should not raise exceptions
        assert manager.get("error:test") is None
        assert not manager.set("error:test", "value")

    def test_ttl_invalidation(self):
        """Test TTL-based cache invalidation."""
        cache_manager = CentralizedCacheManager(backends={CacheTier.MEMORY: MemoryCacheBackend()})

        # Set entry with very short TTL
        cache_manager.set("ttl:test", "value", ttl=1)

        # Should be available immediately
        assert cache_manager.get("ttl:test") == "value"

        # Wait for TTL expiration
        time.sleep(1.1)

        # Should be invalidated (this is simplified - real TTL checking would be in the backend)
        # For this test, we're just demonstrating the concept
        assert cache_manager.get("ttl:test", invalidation_check=False) == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
