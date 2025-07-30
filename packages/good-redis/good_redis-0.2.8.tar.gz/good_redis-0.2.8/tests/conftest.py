import asyncio
import os
import pytest
import pytest_asyncio
import subprocess
import time
import redis
from redis.asyncio import Redis as AsyncRedisBase
from fakeredis import FakeRedis, FakeAsyncRedis
from unittest.mock import patch
from contextlib import contextmanager
from typing import Generator, Optional

# Try to import docker, but make it optional
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

# Check if Docker is available and running
def docker_available():
    """Check if Docker is available and running."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        client = docker.from_env()
        client.ping()
        return True
    except:
        return False

# Check if Redis server is available
def redis_available(host="localhost", port=6379):
    """Check if a Redis server is available."""
    try:
        r = redis.Redis(host=host, port=port, socket_connect_timeout=1, socket_timeout=1)
        r.ping()
        r.close()
        return True
    except:
        return False

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def redis_docker():
    """Spin up a Redis Docker container for the test session."""
    if not docker_available():
        pytest.skip("Docker not available")
    
    client = docker.from_env()
    container = None
    
    try:
        # Pull Redis image if not available
        try:
            client.images.get("redis:latest")
        except docker.errors.ImageNotFound:
            print("Pulling Redis Docker image...")
            client.images.pull("redis:latest")
        
        # Start Redis container
        container = client.containers.run(
            "redis:latest",
            detach=True,
            ports={'6379/tcp': None},  # Random port
            remove=True,
            name=f"test-redis-{os.getpid()}"
        )
        
        # Get the assigned port
        container.reload()
        port = int(container.ports['6379/tcp'][0]['HostPort'])
        
        # Wait for Redis to be ready
        max_retries = 30
        for i in range(max_retries):
            if redis_available("localhost", port):
                break
            time.sleep(0.1)
        else:
            raise TimeoutError("Redis container did not start in time")
        
        yield {"host": "localhost", "port": port, "container": container}
        
    finally:
        if container:
            try:
                container.stop()
                container.remove(force=True)
            except:
                pass

@pytest.fixture
def real_redis(request, redis_docker):
    """Provide a real Redis connection with cleanup."""
    # Check if we should use Docker or existing Redis
    if hasattr(request, "param") and request.param.get("use_existing"):
        # Try to use existing Redis server
        if not redis_available():
            pytest.skip("No Redis server available")
        connection_info = {"host": "localhost", "port": 6379}
    else:
        # Use Docker Redis
        connection_info = redis_docker
    
    # Create Redis client
    r = redis.Redis(
        host=connection_info["host"],
        port=connection_info["port"],
        decode_responses=False,
        db=15  # Use db 15 for tests to avoid conflicts
    )
    
    # Clear the test database
    r.flushdb()
    
    yield r
    
    # Cleanup after test
    try:
        r.flushdb()
        r.close()
    except:
        pass

@pytest.fixture
async def real_async_redis(request, redis_docker):
    """Provide a real async Redis connection with cleanup."""
    # Check if we should use Docker or existing Redis
    if hasattr(request, "param") and request.param.get("use_existing"):
        # Try to use existing Redis server
        if not redis_available():
            pytest.skip("No Redis server available")
        connection_info = {"host": "localhost", "port": 6379}
    else:
        # Use Docker Redis
        connection_info = redis_docker
    
    # Create async Redis client
    r = AsyncRedisBase(
        host=connection_info["host"],
        port=connection_info["port"],
        decode_responses=False,
        db=15  # Use db 15 for tests to avoid conflicts
    )
    
    # Clear the test database
    await r.flushdb()
    
    yield r
    
    # Cleanup after test
    try:
        await r.flushdb()
        await r.aclose()
    except:
        pass

# Existing fakeredis fixtures
@pytest.fixture
def fake_redis():
    """Provide a fake Redis instance for testing."""
    return FakeRedis(decode_responses=False)

@pytest.fixture
def fake_async_redis():
    """Provide a fake async Redis instance for testing."""
    return FakeAsyncRedis(decode_responses=False)

@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    env_vars = [
        'REDIS_HOST', 'REDIS_URL', 'REDIS_PORT', 'REDIS_DB',
        'REDIS_USERNAME', 'REDIS_PASSWORD', 'REDIS_SECURE', 'REDIS_USE_SSL'
    ]
    original = {var: os.environ.get(var) for var in env_vars}
    
    yield
    
    # Restore original values
    for var, value in original.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value

@pytest.fixture
def mock_redis_connection(monkeypatch, fake_redis):
    """Mock Redis connection to use FakeRedis."""
    def mock_connection_pool(**kwargs):
        # Return a mock that fake_redis can use
        return fake_redis.connection_pool
    
    monkeypatch.setattr("redis.ConnectionPool", mock_connection_pool)
    return fake_redis

@pytest.fixture
def mock_async_redis_connection(monkeypatch, fake_async_redis):
    """Mock AsyncRedis connection to use FakeAsyncRedis."""
    def mock_connection_pool(**kwargs):
        return fake_async_redis.connection_pool
    
    monkeypatch.setattr("redis.asyncio.ConnectionPool", mock_connection_pool)
    return fake_async_redis

# Add a custom mark to skip Redis tests if no Redis available
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Markers are already defined in pyproject.toml
    pass

def pytest_collection_modifyitems(config, items):
    """Skip Redis tests if no Redis is available and not in CI."""
    skip_redis = pytest.mark.skip(reason="No Redis instance available")
    
    # Check if we have Redis available (either local or can use Docker)
    has_redis = redis_available() or docker_available()
    
    for item in items:
        if "redis" in item.keywords and not has_redis:
            item.add_marker(skip_redis)