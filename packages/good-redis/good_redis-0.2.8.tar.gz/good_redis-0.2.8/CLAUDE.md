# Good Redis Library

Redis client with dependency injection support and a custom prioritized stream data structure for advanced queue management.

## Package Overview

good-redis provides Redis clients with fast_depends integration and implements a sophisticated prioritized stream data structure using Lua scripts. This enables priority-based task queuing with expiration, gating, and threshold management.

## Key Components

### Redis Clients (`_client.py`)
- `Redis`: Synchronous Redis client
- `AsyncRedis`: Asynchronous Redis client
- `RedisProvider`/`AsyncRedisProvider`: Dependency injection providers
- Built on redis-py with connection pooling and retry logic

### DictProxy (`_dictproxy.py`)
- Dictionary-like interface to Redis
- Transparent key-value operations
- Useful for caching and session storage

### Prioritized Stream (Custom Data Structure)
A Redis-based priority queue implementation using Lua scripts for atomic operations:
- Items have priority scores that determine processing order
- Automatic expiration of stale items
- Gating mechanism to control item visibility
- Bulk operations for efficiency

## Prioritized Stream Operations

### Core Commands

#### `psadd` / `psaddmany`
Add items with priority scores:
```python
# Add single item
await redis.psadd("mystream", "item1", "data", priority=10)

# Add multiple items
items = [
    ("item1", "data1", 10),
    ("item2", "data2", 20),
    ("item3", "data3", 15)
]
await redis.psaddmany("mystream", items)
```

#### `pspull`
Retrieve items by priority with advanced options:
```python
# Get highest priority items
items = await redis.pspull("mystream", count=5)

# Purge items after pulling (remove from stream)
items = await redis.pspull("mystream", count=5, purge=True)

# Use gating (only return items with score >= gate)
items = await redis.pspull("mystream", count=5, gate=True)
```

#### `psincrement` / `psdecrement_all`
Adjust priorities:
```python
# Increment specific item's priority
await redis.psincrement("mystream", "item1", delta=5)

# Decrement all items' priorities
await redis.psdecrement_all("mystream", delta=1)
```

#### `psdeletebelowthreshold`
Remove low-priority items:
```python
# Delete items with priority < 0
deleted = await redis.psdeletebelowthreshold("mystream", threshold=0)
```

#### `psexpired`
Manage item expiration:
```python
# Get expired items
expired = await redis.psexpired("mystream", ttl=3600)  # 1 hour TTL

# Get and remove expired items
expired = await redis.psexpired("mystream", ttl=3600, purge=True)
```

## Usage Examples

### Basic Redis Operations
```python
from good_redis import AsyncRedisProvider
from fast_depends import inject

@inject
async def cache_data(
    redis: AsyncRedis = AsyncRedisProvider(
        host="localhost",
        port=6379,
        db=0
    )
):
    # Standard Redis operations
    await redis.set("key", "value")
    value = await redis.get("key")
    
    # Use pipelining
    async with redis.pipeline() as pipe:
        pipe.set("key1", "value1")
        pipe.set("key2", "value2")
        await pipe.execute()
```

### DictProxy Usage
```python
from good_redis import DictProxy

# Create a dict-like interface
cache = DictProxy(redis, prefix="cache:")

# Use like a dictionary
cache["user:123"] = {"name": "John", "age": 30}
user = cache["user:123"]

# Check existence
if "user:123" in cache:
    print("User exists")

# Delete
del cache["user:123"]
```

### Priority Queue Pattern
```python
# Task queue with priorities
async def add_task(redis, task_id, task_data, priority):
    await redis.psadd("task_queue", task_id, task_data, priority=priority)

async def get_tasks(redis, count=10):
    # Get highest priority tasks
    return await redis.pspull("task_queue", count=count, purge=True)

async def boost_task(redis, task_id, boost=10):
    # Increase task priority
    await redis.psincrement("task_queue", task_id, delta=boost)

async def cleanup_old_tasks(redis):
    # Remove tasks older than 24 hours
    expired = await redis.psexpired("task_queue", ttl=86400, purge=True)
    
    # Remove low priority tasks
    await redis.psdeletebelowthreshold("task_queue", threshold=0)
```

### Gate-Based Processing
```python
# Only process items that meet a threshold
async def process_ready_items(redis):
    # Gate ensures only items with score >= current gate value are returned
    items = await redis.pspull("task_queue", count=100, gate=True)
    
    for item in items:
        # Process item
        await process(item)
        
    # Decrease all priorities after processing
    await redis.psdecrement_all("task_queue", delta=1)
```

## Configuration

### Connection Options
```python
from good_redis import AsyncRedis

redis = AsyncRedis(
    host="localhost",
    port=6379,
    db=0,
    password="secret",
    ssl=True,
    ssl_certfile="/path/to/cert.pem",
    ssl_keyfile="/path/to/key.pem",
    max_connections=50,
    retry_on_timeout=True,
    socket_keepalive=True
)
```

### Using Redis Sentinel
```python
from good_redis import AsyncRedis

redis = AsyncRedis(
    sentinels=[("sentinel1", 26379), ("sentinel2", 26379)],
    sentinel_service_name="mymaster",
    password="secret"
)
```

## Implementation Details

### Lua Scripts
The prioritized stream uses Lua scripts for atomic operations:
- Ensures consistency in concurrent environments
- Reduces network round trips
- Complex operations in single atomic commands

### Data Structure
Items are stored in Redis sorted sets with:
- Member: `{id}:{data}:{timestamp}`
- Score: Priority value
- Gate value stored separately

## Best Practices

1. Use async client for better performance
2. Configure connection pooling appropriately
3. Use pipelining for batch operations
4. Set reasonable TTLs for prioritized stream items
5. Monitor and clean up low-priority items regularly
6. Use gates for controlled processing rates

## Testing

The library includes tests for all operations:
```bash
uv run pytest
```

## Dependencies

- `redis`: Official Redis Python client
- `good-common`: Shared utilities
- `fast-depends`: Dependency injection
- SSL support for secure connections