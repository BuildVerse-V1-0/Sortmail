"""
Redis Client Wrapper
--------------------
Handles Redis connection pooling and provides a unified interface for caching.
"""

import os
from typing import Optional
import redis.asyncio as redis
from app.config import settings
from core.redis_metrics import record_redis_call


class InstrumentedRedis(redis.Redis):
    async def execute_command(self, *args, **options):
        if args:
            record_redis_call(str(args[0]))
        return await super().execute_command(*args, **options)

class RedisClient:
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """Get or create the Redis client instance."""
        if cls._instance is None:
            # Parse Redis URL from settings or env
            redis_url = getattr(settings, "REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            
            cls._instance = InstrumentedRedis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", 20)),
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )
        return cls._instance

    @classmethod
    async def close(cls):
        """Close the Redis connection."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

# Global helper to get client
async def get_redis() -> redis.Redis:
    return RedisClient.get_instance()
