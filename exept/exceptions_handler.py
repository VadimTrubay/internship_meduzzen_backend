from app.main import app
from fastapi import status, Request
from fastapi.responses import JSONResponse
from app.services.user_service import (
    UserNotFound,
    UserAlreadyExists,
    EmailAlreadyExists,
)


@app.exception_handler(UserNotFound)
async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


@app.exception_handler(EmailAlreadyExists)
async def email_already_exists_exception_handler(request: Request, exc: EmailAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


@app.exception_handler(UserAlreadyExists)
async def user_already_exists_exception_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )
