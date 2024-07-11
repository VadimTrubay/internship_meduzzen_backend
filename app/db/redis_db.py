import asyncio_redis
from app.conf.config import settings


async def check_redis_connection():
    try:
        connection = await asyncio_redis.Connection.create(
            host=settings.redis_host, port=settings.redis_port
        )
        await connection.ping()
        connection.close()

    except Exception as error:
        return error
