import redis

from app.conf.config import settings


class RedisService:
    def __init__(self):
        self.redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        self.redis_client = redis.asyncio.from_url(
            self.redis_url, decode_responses=True
        )

    async def get(self, key):
        return await self.redis_client.get(key)

    async def set(self, key, value):
        return await self.redis_client.set(key, value)
