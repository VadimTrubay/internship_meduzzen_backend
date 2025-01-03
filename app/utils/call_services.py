from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.result_repository import ResultRepository
from app.repository.user_repository import UserRepository
from app.services.action_service import ActionService
from app.services.auth_service import AuthService
from app.services.company_service import CompanyService
from app.services.notification_service import NotificationService
from app.services.quiz_service import QuizService
from app.services.result_service import ResultService
from app.services.user_service import UserService


async def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    user_repository = UserRepository(session)

    return UserService(session=session, repository=user_repository)


async def get_result_service(
    session: AsyncSession = Depends(get_session),
) -> ResultService:
    result_repository = ResultRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)
    quizzes_repository = QuizRepository(session)

    return ResultService(
        session=session,
        result_repository=result_repository,
        company_repository=company_repository,
        user_repository=user_repository,
        quiz_repository=quizzes_repository,
    )


async def get_quizzes_service(
    session: AsyncSession = Depends(get_session),
) -> QuizService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    quiz_repository = QuizRepository(session)
    notification_repository = NotificationRepository(session)
    user_repository = UserRepository(session)

    return QuizService(
        session=session,
        quiz_repository=quiz_repository,
        action_repository=action_repository,
        company_repository=company_repository,
        notification_repository=notification_repository,
        user_repository=user_repository,
    )


async def get_company_service(
    session: AsyncSession = Depends(get_session),
) -> CompanyService:
    company_repository = CompanyRepository(session)

    return CompanyService(session=session, repository=company_repository)


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    user_repository = UserRepository(session)

    return AuthService(session=session, repository=user_repository)


async def get_action_service(
    session: AsyncSession = Depends(get_session),
) -> ActionService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)
    notification_repository = NotificationRepository(session)

    return ActionService(
        session=session,
        action_repository=action_repository,
        company_repository=company_repository,
        user_repository=user_repository,
        notification_repository=notification_repository,
    )


async def get_notification_service(
    session: AsyncSession = Depends(get_session),
) -> NotificationService:
    notification_repository = NotificationRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)

    return NotificationService(
        session=session,
        notification_repository=notification_repository,
        company_repository=company_repository,
        user_repository=user_repository,
    )
