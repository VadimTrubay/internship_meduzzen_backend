from loguru import logger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/healthcheck")
def health_check():
    logger.info("Health check endpoint accessed")
    return JSONResponse(
        content={"status_code": 200, "detail": "ok", "result": "working"},
    )
