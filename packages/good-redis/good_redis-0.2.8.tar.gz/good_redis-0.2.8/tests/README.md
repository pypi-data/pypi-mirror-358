# good-redis Test Suite

## Overview

The good-redis test suite is designed to work with both fakeredis (for basic operations) and real Redis instances (for advanced features like Lua scripts). Tests are marked appropriately to allow flexible test execution.

## Test Categories

### `@pytest.mark.fakeredis`
Tests that can run with fakeredis - no Redis server required:
- Basic Redis operations (get, set, delete)
- Provider functionality and dependency injection
- DictProxy basic operations
- Error handling and fallback mechanisms

### `@pytest.mark.redis`
Tests that require a real Redis instance:
- Prioritized Stream (PS) operations (use Lua scripts)
- Advanced Redis features
- Real connection testing
- Performance-sensitive operations

## Running Tests

### Quick Start

```bash
# Run all tests (will skip Redis tests if no server available)
uv run pytest

# Run only fakeredis tests (no Redis required)
uv run pytest -m "fakeredis"

# Run only real Redis tests
uv run pytest -m "redis"

# Run both types
uv run pytest -m "fakeredis or redis"
```

### With Docker

The test suite can automatically spin up a Redis container:

```bash
# Install docker dependency
uv sync

# Run tests (will use Docker if available)
uv run pytest -v
```

### With Local Redis

If you have Redis running locally:

```bash
# Check if Redis is available
redis-cli ping

# Run tests
uv run pytest -v
```

### Test Coverage

```bash
# Run with coverage report
uv run pytest --cov=good_redis --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Environment Variables

The test suite respects these environment variables:

- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_DB`: Test database number (default: 15)

## CI/CD Integration

For GitHub Actions, add this to your workflow:

```yaml
services:
  redis:
    image: redis:latest
    ports:
      - 6379:6379
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Test Isolation

- Tests use database 15 by default to avoid conflicts
- Each test clears the database before and after execution
- Docker containers are removed after test sessions
- Environment variables are restored after each test

## Debugging Tests

```bash
# Run specific test file
uv run pytest tests/good_redis/test_client.py -v

# Run specific test
uv run pytest tests/good_redis/test_client.py::TestRedisClient::test_basic_operations -v

# Show print statements
uv run pytest -s

# Stop on first failure
uv run pytest -x
```

## fast-depends 3.0+ Compatibility

The test suite ensures compatibility with fast-depends 3.0+:

- Tests for new `Annotated` pattern
- Tests for deprecated patterns (with warnings)
- Provider caching and initialization tests
- Both sync and async provider patterns

## Adding New Tests

When adding new tests:

1. Determine if the test needs real Redis (Lua scripts, specific Redis features)
2. Add appropriate marker: `@pytest.mark.fakeredis` or `@pytest.mark.redis`
3. Use the appropriate fixture: `mock_redis_connection` or `real_redis`
4. Ensure proper cleanup in teardown

Example:

```python
@pytest.mark.redis
def test_new_feature(self, real_redis):
    """Test that requires real Redis."""
    redis = Redis(connection_pool=real_redis.connection_pool)
    # Your test code here
```