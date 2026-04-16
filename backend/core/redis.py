"""
Redis Client Wrapper
--------------------
Handles Redis connection pooling and provides a unified interface for caching.

This module intentionally separates command traffic from long-lived pub/sub
connections so SSE subscribers cannot starve normal API/worker Redis commands.
"""

import os
from threading import Lock
from typing import Optional

import redis.asyncio as redis
from redis.asyncio.connection import BlockingConnectionPool

from app.config import settings
from core.redis_metrics import record_redis_call


class InstrumentedRedis(redis.Redis):
    async def execute_command(self, *args, **options):
        if args:
            record_redis_call(str(args[0]))
        return await super().execute_command(*args, **options)


class RedisClient:
    _instance: Optional[redis.Redis] = None
    _pubsub_instance: Optional[redis.Redis] = None
    _lock: Lock = Lock()

    @staticmethod
    def _redis_url() -> str:
        return getattr(settings, "REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    @staticmethod
    def _env_int(name: str, default: int, minimum: int = 1) -> int:
        try:
            return max(int(os.getenv(name, default)), minimum)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _env_float(name: str, default: float, minimum: float = 0.1) -> float:
        try:
            return max(float(os.getenv(name, default)), minimum)
        except (TypeError, ValueError):
            return default

    @classmethod
    def _build_client(cls, *, max_connections: int, instrumented: bool) -> redis.Redis:
        pool_timeout = cls._env_float("REDIS_POOL_TIMEOUT_SECONDS", 5.0)
        pool = BlockingConnectionPool.from_url(
            cls._redis_url(),
            encoding="utf-8",
            decode_responses=True,
            max_connections=max_connections,
            timeout=pool_timeout,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        client_cls = InstrumentedRedis if instrumented else redis.Redis
        return client_cls(connection_pool=pool)

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """Get or create the command Redis client instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    max_connections = cls._env_int("REDIS_MAX_CONNECTIONS", 50)
                    cls._instance = cls._build_client(max_connections=max_connections, instrumented=True)
        return cls._instance

    @classmethod
    def get_pubsub_instance(cls) -> redis.Redis:
        """Get or create the dedicated pub/sub Redis client instance."""
        if cls._pubsub_instance is None:
            with cls._lock:
                if cls._pubsub_instance is None:
                    max_connections = cls._env_int("REDIS_PUBSUB_MAX_CONNECTIONS", 50)
                    cls._pubsub_instance = cls._build_client(max_connections=max_connections, instrumented=False)
        return cls._pubsub_instance

    @classmethod
    async def _close_client(cls, client: Optional[redis.Redis]) -> None:
        if not client:
            return

        close_method = getattr(client, "aclose", None)
        if callable(close_method):
            await close_method()
        else:
            await client.close()

        pool = getattr(client, "connection_pool", None)
        if pool is not None:
            disconnect_method = getattr(pool, "disconnect", None)
            if callable(disconnect_method):
                maybe_awaitable = disconnect_method()
                if hasattr(maybe_awaitable, "__await__"):
                    await maybe_awaitable

    @classmethod
    async def close(cls):
        """Close all Redis clients."""
        await cls._close_client(cls._instance)
        cls._instance = None

        await cls._close_client(cls._pubsub_instance)
        cls._pubsub_instance = None


# Global helper to get command client.
async def get_redis() -> redis.Redis:
    return RedisClient.get_instance()


# Global helper to get pub/sub client.
async def get_redis_pubsub() -> redis.Redis:
    return RedisClient.get_pubsub_instance()
