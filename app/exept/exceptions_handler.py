from fastapi import status, Request
from fastapi.responses import JSONResponse

from app.services.auth_service import (
    UserWithEmailNotFound,
    IncorrectPassword,
    UnAuthorized,
)

from app.services.user_service import (
    UserNotFound,
    UserAlreadyExists,
    EmailAlreadyExists,
    NotFound,
    NotPermission,
)


async def not_found_exception_handler(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def email_already_exists_exception_handler(
    request: Request, exc: EmailAlreadyExists
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


async def user_already_exists_exception_handler(
    request: Request, exc: UserAlreadyExists
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


async def user_with_email_not_found_exception_handler(
    request: Request, exc: UserWithEmailNotFound
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def incorrect_password_exception_handler(
    request: Request, exc: IncorrectPassword
):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
    )


async def unauthorized_exception_handler(request: Request, exc: UnAuthorized):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)}
    )


async def not_permission_exception_handler(request: Request, exc: NotPermission):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
    )