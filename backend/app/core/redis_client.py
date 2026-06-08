from typing import AsyncGenerator
import redis.asyncio as redis
from app.core.config import get_settings

_redis_pool: redis.ConnectionPool | None = None


async def get_redis_pool() -> redis.ConnectionPool:
    global _redis_pool
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_pool_size,
            decode_responses=True,
        )
    return _redis_pool


async def get_redis() -> redis.Redis:
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)


async def get_redis_dep() -> AsyncGenerator[redis.Redis, None]:
    pool = await get_redis_pool()
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.aclose()


class RedisKeys:
    @staticmethod
    def user_session(user_id: str) -> str:
        return f"session:user:{user_id}"

    @staticmethod
    def user_presence(user_id: str) -> str:
        return f"presence:user:{user_id}"

    @staticmethod
    def room_presence(room_id: str) -> str:
        return f"presence:room:{room_id}"

    @staticmethod
    def refresh_token(token_hash: str) -> str:
        return f"rtoken:{token_hash}"

    @staticmethod
    def rate_limit(identifier: str) -> str:
        return f"ratelimit:{identifier}"

    @staticmethod
    def message_cache(room_id: str) -> str:
        return f"messages:{room_id}"
