import uuid

from sqlalchemy import select, and_

from app.models.company_member import CompanyMember
from app.models.company_model import Company
from app.models.user_model import User
from app.models.action_model import CompanyAction
from app.conf.invite import InvitationStatus
from app.repository.base_repository import BaseRepository


class ActionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=CompanyAction)

    @staticmethod
    async def get_relatives_query(
        id_: uuid.UUID, status: InvitationStatus, is_company: bool
    ):
        id_column = CompanyAction.company_id if is_company else CompanyAction.user_id
        if is_company:
            query = (
                select(CompanyAction, User, Company, CompanyMember)
                .distinct()
                .join(User, CompanyAction.user_id == User.id)
                .join(Company, CompanyAction.company_id == Company.id)
                .join(
                    CompanyMember,
                    and_(
                        CompanyAction.company_id == CompanyMember.company_id,
                        CompanyAction.user_id == CompanyMember.user_id,
                    ),
                )
                .filter(id_column == id_, CompanyAction.status == status)
            )
        if not is_company:
            query = (
                select(CompanyAction, User, Company, CompanyMember)
                .distinct()
                .join(User, CompanyAction.user_id == User.id)
                .join(Company, CompanyAction.company_id == Company.id)
                .join(
                    CompanyMember, CompanyAction.company_id == CompanyMember.company_id
                )
                .filter(id_column == id_, CompanyAction.status == status)
            )
        return query

