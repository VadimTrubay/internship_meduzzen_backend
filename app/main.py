import time
import uvicorn
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.conf.config import settings

from app.routers import (
    healthcheck,
    users,
    auth,
    db_healthcheck,
    companies,
    actions,
    quizzes,
    results,
)
from app.exept.exceptions_handler import register_exception_handler

app = FastAPI()

logger.add("app.log", rotation="250 MB", compression="zip", level="INFO")

register_exception_handler(app)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


origins = ["*"]
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
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
app.include_router(companies.router)
app.include_router(actions.router)
app.include_router(quizzes.router)
app.include_router(results.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
