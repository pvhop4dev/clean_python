import redis.asyncio as redis
from app.infrastructure.config import get_settings

settings = get_settings()

class RedisClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._instance

    @classmethod
    async def get_redis(cls):
        if cls._client is None:
            cls()
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
            cls._instance = None

# Dependency
def get_redis():
    return RedisClient()
