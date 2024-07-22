import uuid

from sqlalchemy import select, delete

from app.conf.invite import MemberStatus
from app.models.company_member import CompanyMember
from app.repository.base_repository import BaseRepository
from app.models.company_model import Company
from app.schemas.actions import CompanyMemberSchema
from app.schemas.companies import CompanySchema


class CompanyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Company)

    async def create_company_with_owner(
        self, data: dict, owner_id: uuid.UUID
    ) -> CompanySchema:
        company = await self.create_one(data=data)
        company_member_data = {
            "user_id": owner_id,
            "company_id": company.id,
            "role": MemberStatus.OWNER,
        }
        await self.create_company_member(company_member_data)

        return company

    async def create_company_member(self, data: dict) -> CompanyMemberSchema:
        company_member = CompanyMember(**data)
        self.session.add(company_member)
        await self.session.commit()
        company_member_schema = CompanyMemberSchema.from_orm(company_member)

        return company_member_schema

    async def is_user_company_owner(self, user_id: uuid.UUID, company_id: uuid.UUID) -> bool:
        query = select(CompanyMember).filter(
            CompanyMember.user_id == user_id,
            CompanyMember.company_id == company_id,
            CompanyMember.role == MemberStatus.OWNER,
        )
        company_owner = await self.session.execute(query)
        return company_owner.scalar()

    async def delete_company(self, company_id: uuid.UUID) -> None:
        await self._delete_company_members(company_id)
        await self.delete_one(model_id=company_id)

    async def _delete_company_members(self, company_id: uuid.UUID) -> None:
        query = delete(CompanyMember).where(CompanyMember.company_id == company_id)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_company_member(self, company_id: uuid.UUID, user_id) -> None:
        query = delete(CompanyMember).where(
            CompanyMember.company_id == company_id, CompanyMember.user_id == user_id
        )
        await self.session.execute(query)
        await self.session.commit()
