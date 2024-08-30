import uuid
from typing import Optional, List, Dict

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.detail import Messages
from app.exept.custom_exceptions import (
    NotPermission,
    NotFound,
    CompanyNotFound,
    NotOwner,
)
from app.repository.company_repository import CompanyRepository
from app.schemas.companies import (
    CompanySchema,
    CompanyResponseSchema,
)


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.session = session
        self.repository = repository

    # GET COMPANY OR RAISE
    async def _get_company_or_raise(self, company_id: uuid.UUID) -> CompanySchema:
        company = await self.repository.get_one(id=company_id)
        if not company:
            logger.info(Messages.COMPANY_NOT_FOUND)
            raise CompanyNotFound()

        return company

    # VALIDATE COMPANY
    async def validate_company(
        self, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        if not await self.repository.is_user_company_owner(current_user_id, company_id):
            logger.info(Messages.NOT_OWNER_COMPANY)
            raise NotOwner()

        return company

    # GET TOTAL COUNT
    async def get_total_count(self):
        count = await self.repository.get_count()

        return count

    # GET COMPANIES
    async def get_companies(self, skip, limit) -> List[CompanySchema]:
        companies = await self.repository.get_many(skip=skip, limit=limit)

        return [CompanySchema.model_validate(company) for company in companies]

    # GET COMPANY BY ID
    async def get_company_by_id(self, company_id: uuid.UUID) -> Optional[CompanySchema]:
        company = await self._get_company_or_raise(company_id)

        return company

    # CREATE COMPANY
    async def create_company(
        self, data: Dict, current_user_id: uuid.UUID
    ) -> CompanySchema:
        data["owner_id"] = current_user_id

        return await self.repository.create_company_with_owner(
            data=data, owner_id=current_user_id
        )

    # EDIT COMPANY
    async def update_company(
        self, data: Dict, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> CompanySchema:
        await self.validate_company(current_user_id, company_id)

        return await self.repository.update_one(company_id, data)

    # DELETE COMPANY
    async def delete_company(
        self, company_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> CompanyResponseSchema:
        company = await self.validate_company(current_user_id, company_id)
        await self.repository.delete_company(company_id)

        return CompanyResponseSchema(
            id=company.id,
            name=company.name,
            description=company.description,
        )
