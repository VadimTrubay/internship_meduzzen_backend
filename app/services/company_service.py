import functools
import uuid
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.detail import Messages
from app.exept.custom_exceptions import NotPermission, NotFound, CompanyNotFound
from app.repository.company_repository import CompanyRepository
from app.schemas.companies import (
    CompanySchema,
    CompaniesListResponse,
)


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.session = session
        self.repository = repository

    # IS VISIBLE TO USER
    @staticmethod
    def _is_visible_to_user(company: CompanySchema, user_id: uuid.UUID) -> bool:
        return company.visible or user_id == company.owner_id

    # CHECK COMPANY OWNER
    @staticmethod
    async def check_company_owner(user_id: uuid.UUID, company_owner_id) -> None:
        if user_id != company_owner_id:
            logger.info(Messages.NOT_PERMISSION)
            raise NotPermission()
        return

    # GET TOTAL COUNT
    async def get_total_count(self):
        count = await self.repository.get_count()
        logger.info(Messages.SUCCESS_GET_TOTAL_COUNT)
        return count

    # GET COMPANY OR RAISE
    async def _get_company_or_raise(self, company_id: uuid.UUID) -> CompanySchema:
        company = await self.repository.get_one(id=company_id)
        if not company:
            logger.info(Messages.COMPANY_NOT_FOUND)
            raise CompanyNotFound()
        return company

    # GET COMPANIES
    async def get_companies(
        self, skip, limit, user_id: uuid.UUID = None
    ) -> CompaniesListResponse:
        companies = await self.repository.get_many(skip=skip, limit=limit)
        if not companies:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()

        logger.info(Messages.SUCCESS_GET_COMPANIES)
        total_count = await self.get_total_count()
        visible_companies = [
            CompanySchema(
                id=company.id,
                name=company.name,
                description=company.description,
                visible=self._is_visible_to_user(company, user_id),
                owner_id=company.owner_id,
            )
            for company in companies
        ]
        return CompaniesListResponse(
            companies=visible_companies, total_count=total_count
        )

    # GET COMPANY BY ID
    async def get_company_by_id(
        self, company_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[CompanySchema]:
        company = await self._get_company_or_raise(company_id)
        if not self._is_visible_to_user(company, user_id):
            logger.info(Messages.NOT_PERMISSION)
            raise NotPermission()
        return company

    # REQUIRE COMPANY OWNER
    def require_company_owner(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            company_id = kwargs.get("company_id")
            company = await self._get_company_or_raise(company_id)
            if user_id != company.owner_id:
                raise NotPermission()
            return await func(*args, **kwargs)
        return wrapper

    # CREATE COMPANY
    async def create_company(
        self, data: dict, current_user_id: uuid.UUID
    ) -> CompanySchema:
        data["owner_id"] = current_user_id
        return await self.repository.create_one(data=data)

    # EDIT COMPANY
    async def update_company(
        self, data: dict, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        await self.check_company_owner(current_user_id, company.owner_id)
        return await self.repository.update_one(company_id, data)

    # DELETE COMPANY
    async def delete_company(
        self, company_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        await self.check_company_owner(current_user_id, company.owner_id)
        return await self.repository.delete_one(company_id)
