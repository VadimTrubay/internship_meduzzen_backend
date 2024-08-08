import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.result_repository import ResultRepository
from app.repository.user_repository import UserRepository
from app.schemas.results import ResultSchema, QuizRequest
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.result_service import ResultService

router = APIRouter(prefix="/results", tags=["result"])


async def get_answer_service(
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


@router.post("/create/{quiz_id}", response_model=ResultSchema)
async def create_result(
    quiz_id: uuid.UUID,
    quiz_request: QuizRequest,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_answer_service),
) -> ResultSchema:
    current_user_id = current_user.id
    return await result_service.create_result(
        quiz_id=quiz_id, current_user_id=current_user_id, quiz_request=quiz_request
    )


@router.get("/company/{company_id}/rating", response_model=float)
async def get_company_rating(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_answer_service),
) -> float:
    current_user_id = current_user.id
    return await result_service.get_company_rating(company_id, current_user_id)


@router.get("/global_rating", response_model=float)
async def get_global_rating(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_answer_service),
) -> float:
    current_user_id = current_user.id
    return await result_service.get_global_rating(current_user_id)
