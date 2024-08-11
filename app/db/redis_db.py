import redis.asyncio as redis
from app.conf.config import settings


redis_connection = redis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True
)


async def check_redis_connection():
    try:
        connection = await redis.Connection.create(
            host=settings.redis_host, port=settings.redis_port
        )
        await connection.ping()
        connection.close()

    except Exception as error:
        return error
