import pytest
import os
from typing import Annotated
from unittest.mock import patch, Mock

from good_redis import (
    Redis, RedisProvider, AsyncRedis, AsyncRedisProvider,
    AsyncRedisClient, AsyncRedisClientProvider
)
from fast_depends import inject


class TestRedisProvider:
    """Test RedisProvider with fast-depends 3.0+ compatibility."""
    
    @pytest.mark.fakeredis
    def test_provider_basic(self, mock_redis_connection):
        """Test basic provider functionality."""
        provider = RedisProvider()
        redis = provider.provide()
        assert isinstance(redis, Redis)
    
    @pytest.mark.fakeredis
    def test_provider_caching(self, mock_redis_connection):
        """Test that provider caches instances."""
        # Clear cache first
        RedisProvider.instance_cache.clear()
        
        provider1 = RedisProvider()
        redis1 = provider1.provide(host="localhost", port=6379)
        redis2 = provider1.provide(host="localhost", port=6379)
        
        assert redis1 is redis2  # Same instance
        
        # Different parameters should create new instance
        redis3 = provider1.provide(host="localhost", port=6380)
        assert redis1 is not redis3
    
    @pytest.mark.fakeredis
    def test_provider_environment_variables(self):
        """Test provider reads from environment variables."""
        RedisProvider.instance_cache.clear()
        
        os.environ['REDIS_HOST'] = 'test-host'
        os.environ['REDIS_PORT'] = '6380'
        os.environ['REDIS_DB'] = '1'
        os.environ['REDIS_USERNAME'] = 'testuser'
        os.environ['REDIS_PASSWORD'] = 'testpass'
        os.environ['REDIS_SECURE'] = 'TRUE'
        
        provider = RedisProvider()
        # Just verify it returns a Redis instance - actual connection testing
        # is done in integration tests
        redis = provider.provide()
        assert isinstance(redis, Redis)
        
        # Clean up environment
        for key in ['REDIS_HOST', 'REDIS_PORT', 'REDIS_DB', 'REDIS_USERNAME', 'REDIS_PASSWORD', 'REDIS_SECURE']:
            if key in os.environ:
                del os.environ[key]
    
    @pytest.mark.fakeredis
    def test_provider_ssl_configuration(self):
        """Test SSL configuration."""
        RedisProvider.instance_cache.clear()
        
        # Test with use_ssl=True
        provider = RedisProvider()
        redis = provider.provide(use_ssl=True)
        assert isinstance(redis, Redis)
    
    @pytest.mark.fakeredis
    def test_provider_with_inject_annotated(self, mock_redis_connection):
        """Test provider with new Annotated pattern (fast-depends 3.0+)."""
        RedisProvider.instance_cache.clear()
        
        @inject
        def my_function(redis: Annotated[Redis, RedisProvider()]):
            return redis
        
        redis = my_function()
        assert isinstance(redis, Redis)
    
    @pytest.mark.fakeredis
    def test_provider_with_inject_deprecated(self, mock_redis_connection):
        """Test provider with old deprecated pattern."""
        RedisProvider.instance_cache.clear()
        
        @inject
        def my_function(redis: Redis = RedisProvider()):
            return redis
        
        # Should work but may show deprecation warning
        with pytest.warns(DeprecationWarning):
            redis = my_function()
            assert isinstance(redis, Redis)
    
    @pytest.mark.fakeredis
    def test_provider_custom_args(self):
        """Test provider with custom arguments."""
        RedisProvider.instance_cache.clear()
        
        @inject
        def my_function(
            redis: Annotated[Redis, RedisProvider(host="custom-host", port=7000)]
        ):
            return redis
        
        redis = my_function()
        assert isinstance(redis, Redis)
    
    @pytest.mark.redis
    def test_provider_real_connection(self, real_redis):
        """Test provider with real Redis connection."""
        RedisProvider.instance_cache.clear()
        
        # Get connection info from fixture
        host = real_redis.connection_pool.connection_kwargs.get('host', 'localhost')
        port = real_redis.connection_pool.connection_kwargs.get('port', 6379)
        
        provider = RedisProvider()
        redis = provider.provide(host=host, port=port, db=15)
        
        # Test basic operation
        redis.set("provider_test", "value")
        assert redis.get("provider_test") == b"value"
        redis.delete("provider_test")


class TestAsyncRedisProvider:
    """Test AsyncRedisProvider functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_async_provider_basic(self, mock_async_redis_connection):
        """Test basic async provider functionality."""
        provider = AsyncRedisProvider()
        redis = provider.provide()
        assert isinstance(redis, AsyncRedis)
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_async_provider_caching(self, mock_async_redis_connection):
        """Test async provider caching."""
        AsyncRedisProvider.instance_cache.clear()
        
        provider = AsyncRedisProvider()
        redis1 = provider.provide(host="localhost")
        redis2 = provider.provide(host="localhost")
        assert redis1 is redis2
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_async_provider_with_inject(self, mock_async_redis_connection):
        """Test async provider with inject."""
        AsyncRedisProvider.instance_cache.clear()
        
        @inject
        async def my_async_function(
            redis: Annotated[AsyncRedis, AsyncRedisProvider()]
        ):
            return redis
        
        redis = await my_async_function()
        assert isinstance(redis, AsyncRedis)
    
    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_async_provider_real_connection(self, real_async_redis):
        """Test async provider with real Redis connection."""
        AsyncRedisProvider.instance_cache.clear()
        
        # Get connection info from fixture
        host = real_async_redis.connection_pool.connection_kwargs.get('host', 'localhost')
        port = real_async_redis.connection_pool.connection_kwargs.get('port', 6379)
        
        provider = AsyncRedisProvider()
        redis = provider.provide(host=host, port=port, db=15)
        
        # Test basic operation
        await redis.set("async_provider_test", "value")
        value = await redis.get("async_provider_test")
        assert value == b"value"
        await redis.delete("async_provider_test")
        await redis.aclose()


class TestAsyncRedisClientProvider:
    """Test AsyncRedisClientProvider functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_client_provider_basic(self, mock_async_redis_connection):
        """Test basic client provider functionality."""
        provider = AsyncRedisClientProvider()
        client = provider.provide()
        assert isinstance(client, AsyncRedisClient)
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_client_provider_context_manager(self, mock_async_redis_connection):
        """Test client provider with context manager."""
        AsyncRedisClientProvider.instance_cache.clear()
        
        provider = AsyncRedisClientProvider()
        client = provider.provide()
        
        async with client as redis:
            assert isinstance(redis, AsyncRedis)
            await redis.set("test", "value")
    
    @pytest.mark.asyncio
    @pytest.mark.fakeredis
    async def test_client_provider_close(self, mock_async_redis_connection):
        """Test closing all connections."""
        AsyncRedisClientProvider.instance_cache.clear()
        
        provider = AsyncRedisClientProvider()
        client1 = provider.provide(host="host1")
        client2 = provider.provide(host="host2")
        
        # Close all connections
        result = await AsyncRedisClientProvider.close()
        assert result is True
        assert len(AsyncRedisClientProvider.instance_cache) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_client_provider_real_connection(self, real_async_redis):
        """Test client provider with real Redis connection."""
        AsyncRedisClientProvider.instance_cache.clear()
        
        # Get connection info from fixture
        host = real_async_redis.connection_pool.connection_kwargs.get('host', 'localhost')
        port = real_async_redis.connection_pool.connection_kwargs.get('port', 6379)
        
        provider = AsyncRedisClientProvider()
        client = provider.provide(host=host, port=port, db=15)
        
        async with client as redis:
            # Test basic operation
            await redis.set("client_provider_test", "value")
            value = await redis.get("client_provider_test")
            assert value == b"value"
            await redis.delete("client_provider_test")
        
        # Clean up
        await AsyncRedisClientProvider.close()