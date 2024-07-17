import time
import uvicorn
from loguru import logger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.conf.config import settings
from app.routers import healthcheck, users, auth
from app.routers import db_healthcheck
from app.exept import exceptions_handler

app = FastAPI()

logger.add("app.log", rotation="250 MB", compression="zip", level="INFO")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


origins = ["http://localhost", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


app.include_router(healthcheck.router)
app.include_router(db_healthcheck.router)
app.include_router(users.router)
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
