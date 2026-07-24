import redis.asyncio as aioredis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        _pool = aioredis.Redis(host="localhost", port=6379, decode_responses=True)
    return _pool


class RedisCache:
    """Async Redis cache for query results and metadata."""

    async def _r(self):
        return await get_redis()

    async def get(self, key: str) -> Optional[str]:
        try:
            r = await self._r()
            return await r.get(key)
        except Exception as e:
            logger.warning("Redis GET failed: %s", e)
            return None

    async def set(self, key: str, value: str, ttl: int = 300):
        try:
            r = await self._r()
            await r.set(key, value, ex=ttl)
        except Exception as e:
            logger.warning("Redis SET failed: %s", e)

    async def delete(self, key: str):
        try:
            r = await self._r()
            await r.delete(key)
        except Exception as e:
            logger.warning("Redis DELETE failed: %s", e)

    async def clear_pattern(self, pattern: str) -> int:
        try:
            r = await self._r()
            keys = []
            async for key in r.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await r.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.warning("Redis CLEAR failed: %s", e)
            return 0

    async def get_stats(self) -> dict:
        try:
            r = await self._r()
            info = await r.info("memory")
            keys_count = await r.dbsize()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "keys_count": keys_count,
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
