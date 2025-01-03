import uuid
from typing import Dict, List

from fastapi import APIRouter, Depends

from app.schemas.results import (
    UserQuizResultSchema,
    CompanyMemberResultSchema,
    QuizResultSchema,
)
from app.schemas.results import UserQuizResultSchema
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.result_service import ResultService
from app.utils.call_services import get_result_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/company/{company_id}/members_results", response_model=CompanyMemberResultSchema
)
async def get_company_results(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_result_service),
) -> CompanyMemberResultSchema:
    current_user_id = current_user.id

    return await result_service.company_members_results(current_user_id, company_id)


@router.get("/my/quizzes/results", response_model=List[UserQuizResultSchema])
async def get_my_quizzes_latest_results(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_result_service),
) -> List[UserQuizResultSchema]:
    current_user_id = current_user.id

    return await result_service.get_my_quizzes(current_user_id)


@router.get("/my/quiz/{quiz_id}", response_model=QuizResultSchema)
async def get_my_quiz_results(
    quiz_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_result_service),
) -> QuizResultSchema:
    current_user_id = current_user.id

    return await result_service.my_quiz_results(
        current_user_id=current_user_id, quiz_id=quiz_id
    )


@router.get(
    "/company/{company_id}/member/{company_member_id}/results",
    response_model=CompanyMemberResultSchema,
)
async def get_company_results_one_user(
    company_id: uuid.UUID,
    company_member_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_result_service),
) -> CompanyMemberResultSchema:
    current_user_id = current_user.id

    return await result_service.company_member_results(
        company_id, company_member_id, current_user_id
    )


@router.get(
    "/company/{company_id}/member_result_last", response_model=CompanyMemberResultSchema
)
async def get_company_result_last(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    result_service: ResultService = Depends(get_result_service),
) -> CompanyMemberResultSchema:
    current_user_id = current_user.id

    return await result_service.company_members_result_last(company_id, current_user_id)
