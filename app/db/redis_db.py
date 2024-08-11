import redis.asyncio as redis
from app.conf.config import settings


async def check_redis_connection():
    try:
        connection = await redis.Connection.create(
            host=settings.redis_host, port=settings.redis_port
        )
        await connection.ping()
        connection.close()

    except Exception as error:
        return error
