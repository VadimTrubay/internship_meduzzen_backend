from app.db.connection import engine


async def check_postgres_connection():
    async with engine.connect():
        return
