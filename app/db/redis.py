import redis.asyncio as redis
from app.conf.config import settings


redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

redis_connection = redis.from_url(redis_url, decode_responses=True)
