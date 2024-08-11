import uuid

from fastapi import APIRouter, Depends

from app.schemas.quizzes import (
    QuizSchema,
    QuizUpdateSchema,
    QuizzesListResponse,
    QuizByIdSchema,
)
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.quiz_service import QuizService
from app.utils.call_services import get_quizzes_service

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/company/{company_id}", response_model=QuizzesListResponse)
async def get_quizzes(
    company_id: uuid.UUID,
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizzesListResponse:
    quizzes = await quiz_service.get_quizzes(company_id)
    total_count = await quiz_service.get_total_count(company_id)
    return QuizzesListResponse(quizzes=quizzes, total_count=total_count)


@router.post("/company/{company_id}", response_model=QuizSchema)
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


@router.patch("/quiz/{quiz_id}", response_model=QuizUpdateSchema)
async def update_quiz(
    quiz_data: QuizUpdateSchema,
    quiz_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizByIdSchema:
    current_user_id = current_user.id
    return await quiz_service.update_quiz(
        quiz_data=quiz_data, quiz_id=quiz_id, current_user_id=current_user_id
    )


@router.delete("/quiz/{quiz_id}", response_model=dict)
async def delete_quiz(
    quiz_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> dict:
    current_user_id = current_user.id
    return await quiz_service.delete_quiz(
        quiz_id=quiz_id, current_user_id=current_user_id
    )


@router.get("/quiz/{quiz_id}", response_model=QuizByIdSchema)
async def get_quiz_by_id(
    quiz_id: uuid.UUID,
    quiz_service: QuizService = Depends(get_quizzes_service),
) -> QuizByIdSchema:
    return await quiz_service.get_quiz_by_id(quiz_id)
