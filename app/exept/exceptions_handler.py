from fastapi import status, Request, FastAPI
from fastapi.responses import JSONResponse

from app.services.action_service import (
    AlreadyInCompany,
    NotOwner,
    ActionNotFound,
    UserAlreadyInvited,
    ActionAlreadyAvailable,
    YouCanNotInviteYourSelf,
)
from app.services.company_service import CompanyNotFound
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
from app.utils.companies_utils import (
    UserNotRequested,
    UserNotInvited,
    UserNotInteractWithActions,
)


def register_exception_handler(app: FastAPI):
    @app.exception_handler(UserNotFound)
    async def not_found_exception_handler(request: Request, exc: NotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(UserNotFound)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyNotFound)
    async def company_not_found_exception_handler(
        request: Request, exc: CompanyNotFound
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyNotFound)
    async def action_not_found_exception_handler(request: Request, exc: ActionNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(UserNotFound)
    async def email_already_exists_exception_handler(
        request: Request, exc: EmailAlreadyExists
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExists
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(UserWithEmailNotFound)
    async def user_with_email_not_found_exception_handler(
        request: Request, exc: UserWithEmailNotFound
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(IncorrectPassword)
    async def incorrect_password_exception_handler(
        request: Request, exc: IncorrectPassword
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(UnAuthorized)
    async def unauthorized_exception_handler(request: Request, exc: UnAuthorized):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)}
        )

    @app.exception_handler(NotPermission)
    async def not_permission_exception_handler(request: Request, exc: NotPermission):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(AlreadyInCompany)
    async def already_in_company_exception_handler(
        request: Request, exc: AlreadyInCompany
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(NotOwner)
    async def not_owner_exception_handler(request: Request, exc: NotOwner):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(UserNotRequested)
    async def user_not_requested_exception_handler(
        request: Request, exc: UserNotRequested
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(UserNotInvited)
    async def user_not_invited_exception_handler(request: Request, exc: UserNotInvited):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(UserNotInteractWithActions)
    async def user_not_interact_with_actions_exception_handler(
        request: Request, exc: UserNotInteractWithActions
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(UserAlreadyInvited)
    async def user_already_invited_exception_handler(
        request: Request, exc: UserAlreadyInvited
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(ActionAlreadyAvailable)
    async def action_already_available_exception_handler(
        request: Request, exc: ActionAlreadyAvailable
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(YouCanNotInviteYourSelf)
    async def you_can_not_invite_exception_handler(
        request: Request, exc: ActionAlreadyAvailable
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )
