import pytest
import datetime
from unittest.mock import Mock, patch
from typing import Annotated

from good_redis import Redis, RedisProvider, AsyncRedis, AsyncRedisProvider
from fast_depends import inject


class TestRedisClient:
    """Test the Redis client functionality."""
    
    @pytest.mark.fakeredis
    def test_basic_operations(self, mock_redis_connection):
        """Test basic Redis operations."""
        redis = Redis(connection_pool=mock_redis_connection.connection_pool)
        
        # Test set/get
        redis.set("test_key", "test_value")
        assert redis.get("test_key") == b"test_value"
        
        # Test delete
        redis.delete("test_key")
        assert redis.get("test_key") is None
    
    @pytest.mark.redis
    def test_basic_operations_real(self, real_redis):
        """Test basic Redis operations with real Redis."""
        redis = Redis(connection_pool=real_redis.connection_pool)
        
        # Test set/get
        redis.set("test_key", "test_value")
        assert redis.get("test_key") == b"test_value"
        
        # Test delete
        redis.delete("test_key")
        assert redis.get("test_key") is None
    
    @pytest.mark.redis
    def test_prioritized_stream_add(self, real_redis):
        """Test psadd functionality with real Redis (requires Lua scripts)."""
        redis = Redis(connection_pool=real_redis.connection_pool)
        
        # Clean up any existing data
        redis.psdelete("test_stream")
        
        # Test single add
        score = redis.psadd("test_stream", "key1", "value1", score=10)
        assert score == 10
        
        # Test with readd
        score = redis.psadd("test_stream", "key1", "value2", score=5, readd=True)
        # Score should be incremented (ZINCRBY adds to existing score)
        assert score == 15
        
    @pytest.mark.redis
    def test_prioritized_stream_add_many(self, real_redis):
        """Test psaddmany functionality with real Redis."""
        redis = Redis(connection_pool=real_redis.connection_pool)
        
        # Clean up any existing data
        redis.psdelete("test_stream")
        
        items = [
            ("key1", "value1", 10),
            ("key2", "value2", 20),
            ("key3", "value3", 15)
        ]
        
        results = redis.psaddmany("test_stream", items)
        assert len(results) == len(items)
        
        # Verify items were added
        assert redis.pslen("test_stream") == 3
    
    @pytest.mark.redis
    def test_prioritized_stream_pull(self, real_redis):
        """Test pspull functionality with real Redis."""
        redis = Redis(connection_pool=real_redis.connection_pool)
        
        # Clean up any existing data
        redis.psdelete("test_stream")
        
        # Add items
        redis.psadd("test_stream", "key1", "value1", 10)
        redis.psadd("test_stream", "key2", "value2", 20)
        
        # Pull with default options (should get highest score first)
        result = redis.pspull("test_stream", count=1)
        assert len(result) == 1
        # Handle both bytes and string keys
        assert b"key2" in result or "key2" in result  # Highest score
        if b"key2" in result:
            assert result[b"key2"] == b"value2"
        else:
            assert result["key2"] == b"value2"
        
        # Add item back and test purge=False
        redis.psadd("test_stream", "key2", "value2", 20, readd=True)
        result = redis.pspull("test_stream", count=1, purge=False)
        assert len(result) == 1
        # Item should still exist
        assert redis.pslen("test_stream") == 2
        
        # Test gate=True
        result = redis.pspull("test_stream", count=1, gate=True)
        assert len(result) == 1
    
    @pytest.mark.redis
    def test_prioritized_stream_operations(self, real_redis):
        """Test various PS operations with real Redis."""
        redis = Redis(connection_pool=real_redis.connection_pool)
        
        # Clean up any existing data
        redis.psdelete("test_stream")
        
        # Add items
        redis.psadd("test_stream", "key1", "value1", 10)
        redis.psadd("test_stream", "key2", "value2", 5)
        
        # Test pskeys
        keys = redis.pskeys("test_stream")
        assert len(keys) == 2
        assert b"key1" in keys or "key1" in keys
        assert b"key2" in keys or "key2" in keys
        
        # Test psvalues
        values = redis.psvalues("test_stream")
        assert len(values) == 2
        # psvalues returns a dict with keys, not values
        assert "key1" in values or b"key1" in values
        
        # Test pslen
        length = redis.pslen("test_stream")
        assert length == 2
        
        # Test psget
        value = redis.psget("test_stream", "key1")
        assert value == b"value1"
        
        # Test psincrement
        new_score = redis.psincrement("test_stream", "key1", 5)
        assert new_score == 15
        
        # Test psdecrementall
        redis.psdecrement_all("test_stream", 2)
        
        # Test psdeletebelowthreshold
        deleted = redis.psdeletebelowthreshold("test_stream", 10)
        assert len(deleted) >= 1  # key2 should be deleted
        
        # Test psdelete
        redis.psdelete("test_stream")
        assert redis.pslen("test_stream") == 0
    
    @pytest.mark.fakeredis
    def test_hashset_operations(self, mock_redis_connection):
        """Test hashset operations."""
        redis = Redis(connection_pool=mock_redis_connection.connection_pool)
        
        # Test add with hashable types
        redis.hashset_add("test_set", "value1")
        redis.hashset_add("test_set", 12345)
        redis.hashset_add("test_set", 3.14)
        redis.hashset_add("test_set", True)
        
        # Test contains
        assert redis.hashset_contains("test_set", "value1")
        assert redis.hashset_contains("test_set", 12345)
        assert not redis.hashset_contains("test_set", "nonexistent")
        
        # Test unhashable types should raise TypeError
        with pytest.raises(TypeError):
            redis.hashset_add("test_set", {"key": "value"})
        
        with pytest.raises(TypeError):
            redis.hashset_add("test_set", ["list", "value"])
        
        # Test remove
        redis.hashset_remove("test_set", "value1")
        assert not redis.hashset_contains("test_set", "value1")
        
        # Test clear
        redis.hashset_clear("test_set")
    
    @pytest.mark.redis
    def test_hashset_operations_real(self, real_redis):
        """Test hashset operations with real Redis."""
        redis = Redis(connection_pool=real_redis.connection_pool)
        
        # Clean up any existing data
        redis.hashset_clear("test_set")
        
        # Test add with hashable types
        redis.hashset_add("test_set", "string_value")
        redis.hashset_add("test_set", 12345)
        redis.hashset_add("test_set", 3.14)
        redis.hashset_add("test_set", True)
        
        # Test contains
        assert redis.hashset_contains("test_set", "string_value")
        assert redis.hashset_contains("test_set", 12345)
        assert redis.hashset_contains("test_set", 3.14)
        assert redis.hashset_contains("test_set", True)
        assert not redis.hashset_contains("test_set", "nonexistent")
        
        # Test unhashable types should raise TypeError
        with pytest.raises(TypeError):
            redis.hashset_add("test_set", {"key": "value"})
        
        with pytest.raises(TypeError):
            redis.hashset_add("test_set", ["list", "value"])
        
        # Test remove
        redis.hashset_remove("test_set", "string_value")
        assert not redis.hashset_contains("test_set", "string_value")
        
        # Test clear
        redis.hashset_clear("test_set")
        assert not redis.hashset_contains("test_set", 12345)


class TestAsyncRedisClient:
    """Test the AsyncRedis client functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_basic_operations(self, mock_async_redis_connection):
        """Test basic async Redis operations."""
        redis = AsyncRedis(connection_pool=mock_async_redis_connection.connection_pool)
        
        # Test set/get
        await redis.set("test_key", "test_value")
        value = await redis.get("test_key")
        assert value == b"test_value"
        
        # Test delete
        await redis.delete("test_key")
        value = await redis.get("test_key")
        assert value is None
        
        await redis.aclose()
    
    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_basic_operations_real(self, real_async_redis):
        """Test basic async Redis operations with real Redis."""
        redis = AsyncRedis(connection_pool=real_async_redis.connection_pool)
        
        # Test set/get
        await redis.set("test_key", "test_value")
        value = await redis.get("test_key")
        assert value == b"test_value"
        
        # Test delete
        await redis.delete("test_key")
        value = await redis.get("test_key")
        assert value is None
        
        await redis.aclose()
    
    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_prioritized_stream_operations(self, real_async_redis):
        """Test async PS operations with real Redis."""
        redis = AsyncRedis(connection_pool=real_async_redis.connection_pool)
        
        # Clean up any existing data
        await redis.psdelete("test_stream")
        await redis.hashset_clear("test_set")
        
        # Test psadd with decay
        score = await redis.psadd("test_stream", "key1", "value1", score=10, with_decay=True)
        assert score[0] == 1  # Returns pipeline execution result count
        
        # Test psaddmany
        items = [("key2", "value2", 20), ("key3", "value3", 15)]
        results = await redis.psaddmany("test_stream", items, with_decay=True)
        assert len(results) >= len(items)
        
        # Test pspull
        result = await redis.pspull("test_stream", count=2)
        assert len(result) <= 2
        # Should get highest scores first
        keys = list(result.keys())
        if len(keys) >= 1:
            # Handle both bytes and string keys
            assert b"key2" == keys[0] or "key2" == keys[0]  # Highest score
        
        # Test other operations
        keys = await redis.pskeys("test_stream")
        assert len(keys) >= 1
        
        values = await redis.psvalues("test_stream")
        assert len(values) >= 1
        
        names = await redis.psnames()
        assert b"test_stream" in names or "test_stream" in names
        
        decay_names = await redis.psdecay()
        assert b"test_stream" in decay_names or "test_stream" in decay_names
        
        await redis.psincrement("test_stream", "key1", 5)
        await redis.psdecrement_all("test_stream", 2)
        
        # Test hashset operations
        await redis.hashset_add("test_set", "value1", "value2")
        contains = await redis.hashset_contains("test_set", "value1")
        assert contains
        
        await redis.aclose()
    
    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_psexpire(self, real_async_redis):
        """Test PS expire functionality with real Redis."""
        redis = AsyncRedis(connection_pool=real_async_redis.connection_pool)
        
        # Clean up any existing data
        await redis.psdelete("test_stream")
        
        # Add items with short expiration (already expired)
        expire_at = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=1)
        await redis.psadd("test_stream", "key1", "value1")
        
        # Manually add to expiration set with past timestamp
        await redis.zadd(f"test_stream:exp", {"key1": int(expire_at.timestamp())})
        
        # Run expiration
        await redis.psexpire()
        
        # Key should be removed
        value = await redis.psget("test_stream", "key1")
        assert value is None
        
        await redis.aclose()