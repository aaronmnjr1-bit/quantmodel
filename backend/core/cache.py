from __future__ import annotations

import json
from typing import Any

from loguru import logger

try:
    import redis.asyncio as aioredis

    _REDIS_AVAILABLE = True
except ImportError:
    aioredis = None  # type: ignore
    _REDIS_AVAILABLE = False

from config import settings


class RedisCache:
    """
    Async Redis cache layer for analysis results.
    Falls back to in-memory dict when Redis is unavailable.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._memory: dict[str, str] = {}
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
            else:
                raw = self._memory.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.debug(f"Cache get error for {key!r}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            serialized = json.dumps(value, default=str)
            if self._available and self._client:
                await self._client.set(key, serialized, ex=ttl)
            else:
                self._memory[key] = serialized
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
