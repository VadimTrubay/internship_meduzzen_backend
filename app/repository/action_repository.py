import uuid
from typing import List

from sqlalchemy import select, and_

from app.models.company_member import CompanyMember
from app.models.company_model import Company
from app.models.user_model import User
from app.models.action_model import CompanyAction
from app.conf.invite import InvitationStatus
from app.repository.base_repository import BaseRepository
from app.schemas.actions import CompanyMemberSchema


class ActionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=CompanyAction)

    async def get_members(self, company_id: uuid.UUID) -> List[CompanyMemberSchema]:
        query = (
            select(CompanyMember, CompanyAction)
            .join(CompanyAction, CompanyAction.user_id == CompanyMember.user_id)
            .join(User, User.id == CompanyAction.user_id)
            .join(Company, Company.id == CompanyAction.company_id)
            .filter(CompanyMember.company_id == company_id)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_member_role(self, user_id: uuid.UUID, company_id: uuid.UUID) -> str:
        query = select(CompanyMember).where(
            CompanyMember.user_id == user_id, CompanyMember.company_id == company_id
        )
        member_role = await self.session.execute(query)
        role = member_role.scalar_one()
        return role.role

    @staticmethod
    async def get_relatives_query(
            id_: uuid.UUID, status: InvitationStatus, is_company: bool
    ):
        id_column = CompanyAction.company_id if is_company else CompanyAction.user_id

        query = (
            select(CompanyAction, User, Company)
            .join(User, CompanyAction.user_id == User.id)
            .join(Company, CompanyAction.company_id == Company.id)
            .filter(id_column == id_, CompanyAction.status == status)
        )
        return query
