from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.db.postgres_db import check_postgres_connection
from app.db.redis_db import check_redis_connection

router = APIRouter()


@router.get("/test_postgres")
async def check_postgres():
    try:
        await check_postgres_connection()
        return JSONResponse(
            content={"postgres_status": "Postgres connection test successful"}
        )
    except Exception as error:
        return error


@router.get("/test_redis")
async def check_redis():
    try:
        await check_redis_connection()
        return JSONResponse(
            content={"redis_status": "Redis connection test successful"}
        )

    except Exception as error:
        return error
