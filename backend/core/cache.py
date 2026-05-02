from __future__ import annotations

import json
import time
from typing import Any

from loguru import logger

try:
    import redis.asyncio as aioredis

    _REDIS_AVAILABLE = True
except ImportError:
    aioredis = None  # type: ignore
    _REDIS_AVAILABLE = False

from config import settings

_MEMORY_MAX_ENTRIES = 256  # evict oldest when limit is reached


class RedisCache:
    """
    Async Redis cache layer for analysis results.
    Falls back to in-memory dict (with TTL) when Redis is unavailable.
    """

    def __init__(self) -> None:
        self._client: Any = None
        # In-memory store maps key -> (serialized_value, expiry_epoch)
        self._memory: dict[str, tuple[str, float]] = {}
        self._available = False

    async def connect(self) -> None:
        if not _REDIS_AVAILABLE:
            logger.warning("redis package not available — using in-memory cache")
            return
        try:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=3,
            )
            await self._client.ping()
            self._available = True
            logger.info("Redis connected successfully")
        except Exception as exc:
            logger.warning(f"Redis unavailable ({exc}) — using in-memory cache")
            self._client = None

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._available = False

    async def get(self, key: str) -> Any | None:
        try:
            if self._available and self._client:
                raw = await self._client.get(key)
                return json.loads(raw) if raw else None
            # In-memory: check TTL
            entry = self._memory.get(key)
            if entry is None:
                return None
            value_str, expiry = entry
            if time.monotonic() > expiry:
                del self._memory[key]
                return None
            return json.loads(value_str)
        except Exception as exc:
            logger.debug(f"Cache get error for {key!r}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            serialized = json.dumps(value, default=str)
            if self._available and self._client:
                await self._client.set(key, serialized, ex=ttl)
            else:
                # Evict oldest entry when at capacity
                if len(self._memory) >= _MEMORY_MAX_ENTRIES:
                    oldest_key = next(iter(self._memory))
                    del self._memory[oldest_key]
                self._memory[key] = (serialized, time.monotonic() + ttl)
        except Exception as exc:
            logger.debug(f"Cache set error for {key!r}: {exc}")

    async def delete(self, key: str) -> None:
        try:
            if self._available and self._client:
                await self._client.delete(key)
            else:
                self._memory.pop(key, None)
        except Exception as exc:
            logger.debug(f"Cache delete error for {key!r}: {exc}")

    @property
    def is_available(self) -> bool:
        return self._available


# Singleton — imported from other modules
cache = RedisCache()
