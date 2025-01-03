import uuid
from typing import Dict

from fastapi import APIRouter, Depends

from app.schemas.companies import (
    CompanySchema,
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompaniesListResponse,
    CompanyResponseSchema,
)
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.company_service import CompanyService
from app.utils.call_services import get_company_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=CompaniesListResponse)
async def get_all_companies(
    skip: int = 1,
    limit: int = 10,
    company_service: CompanyService = Depends(get_company_service),
    current_user: UserSchema = Depends(AuthService.get_current_user),
):
    companies = await company_service.get_companies(skip, limit, current_user)
    total_count = await company_service.get_total_count()
    result = [CompanySchema.from_orm(company) for company in companies]

    return CompaniesListResponse(companies=result, total_count=total_count)


@router.get("/{company_id}", response_model=CompanySchema)
async def get_company_by_id(
    company_id: uuid.UUID,
    company_service: CompanyService = Depends(get_company_service),
    current_user: UserSchema = Depends(AuthService.get_current_user),
):

    return await company_service.get_company_by_id(company_id, current_user)


@router.post("/", response_model=CompanySchema)
async def create_company(
    company_data: CompanyCreateRequest,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    current_user_id = current_user.id

    return await company_service.create_company(
        company_data.model_dump(), current_user_id
    )


@router.patch("/{company_id}", response_model=CompanySchema)
async def update_company(
    company_id: uuid.UUID,
    company_data: CompanyUpdateRequest,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    current_user_id = current_user.id

    return await company_service.update_company(
        company_data.model_dump(), current_user_id, company_id
    )


@router.delete("/{company_id}", response_model=CompanyResponseSchema)
async def delete_company(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyResponseSchema:
    current_user_id = current_user.id

    return await company_service.delete_company(company_id, current_user_id)
