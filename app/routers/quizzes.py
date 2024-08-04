import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.schemas.quizzes import (
    QuizSchema,
    QuizUpdateSchema,
    QuestionSchema,
    QuizResponseSchema,
    QuizzesListResponse,
)
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


async def get_quizzes_service(
    session: AsyncSession = Depends(get_session),
) -> QuizService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    quiz_repository = QuizRepository(session)
    return QuizService(
        session=session,
        quiz_repository=quiz_repository,
        action_repository=action_repository,
        company_repository=company_repository,
    )


@router.get("/company/{company_id}", response_model=QuizzesListResponse)
async def get_quizzes(
    company_id: uuid.UUID,
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizzesListResponse:
    quizzes = await quiz_service.get_quizzes(company_id)
    total_count = await quiz_service.get_total_count()
    return QuizzesListResponse(quizzes=quizzes, total_count=total_count)


@router.post("/company/{company_id}/create", response_model=QuizSchema)
async def create_quiz(
    quiz_data: QuizSchema,
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizSchema:
    current_user_id = current_user.id
    return await quiz_service.create_quiz(
        quiz_data=quiz_data, current_user_id=current_user_id, company_id=company_id
    )


@router.patch("/quiz/{quiz_id}/update", response_model=QuizUpdateSchema)
async def update_quiz(
    quiz_data: QuizUpdateSchema,
    quiz_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizUpdateSchema:
    current_user_id = current_user.id
    return await quiz_service.update_quiz(
        quiz_data=quiz_data, quiz_id=quiz_id, current_user_id=current_user_id
    )


@router.delete("/quiz/{quiz_id}/delete", response_model=QuizResponseSchema)
async def delete_quiz(
    quiz_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizResponseSchema:
    current_user_id = current_user.id
    return await quiz_service.delete_quiz(
        quiz_id=quiz_id, current_user_id=current_user_id
    )


@router.post("/quiz/{quiz_id}/question/create", response_model=QuestionSchema)
async def create_question(
    question_data: QuestionSchema,
    quiz_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuestionSchema:
    current_user_id = current_user.id
    return await quiz_service.add_question(
        question_data, quiz_id, current_user_id=current_user_id
    )


@router.delete("/question/{question_id}/delete", response_model=QuestionSchema)
async def delete_quiz_question(
    question_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuestionSchema:
    current_user_id = current_user.id
    return await quiz_service.delete_question(
        question_id, current_user_id=current_user_id
    )
