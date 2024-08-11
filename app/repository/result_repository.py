import uuid
from typing import Optional, List

from sqlalchemy import select, func, desc, and_

from app.models.company_member import CompanyMember
from app.models.result_model import Result
from app.models.user_model import User
from app.repository.base_repository import BaseRepository


class ResultRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Result)

    async def calculate_rating(self, company_member_id: uuid.UUID) -> float:
        total_score_query = select(func.sum(self.model.score)).filter(
            self.model.company_member_id == company_member_id
        )

        total_results_query = select(func.count(self.model.id)).filter(
            self.model.company_member_id == company_member_id
        )
        total_score = await self.session.execute(total_score_query)
        total_results = await self.session.execute(total_results_query)

        total_score_value = total_score.scalars().first() or 0.0
        total_results_value = total_results.scalars().first() or 0

        average_score = (
            total_score_value / total_results_value if total_results_value > 0 else 0.0
        )
        return average_score

    async def get_last_result_for_user(
        self, company_member_id: uuid.UUID
    ) -> Optional[Result]:
        query = (
            select(Result)
            .join(CompanyMember)
            .filter(CompanyMember.user_id == company_member_id)
            .order_by(desc(Result.created_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_results_for_company_member(
        self, user_id: uuid.UUID
    ) -> List[Result]:
        subquery = (
            select(Result.quiz_id, func.max(Result.created_at).label("max_created_at"))
            .join(CompanyMember)
            .join(User)
            .filter(User.id == user_id)
            .group_by(Result.quiz_id)
            .subquery()
        )
        query = select(Result).join(
            subquery,
            and_(
                Result.quiz_id == subquery.c.quiz_id,
                Result.created_at == subquery.c.created_at,
            ),
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_results_for_company(
        self, company_id: uuid.UUID
    ) -> List[Result]:
        subquery = (
            select(
                CompanyMember.id.label("company_member_id"),
                Result.quiz_id,
                func.max(Result.created_at).label("max_created_at"),
            )
            .join(Result, Result.company_member_id == CompanyMember.id)
            .join(User, CompanyMember.user_id == User.id)
            .filter(CompanyMember.company_id == company_id)
            .group_by(CompanyMember.id, Result.quiz_id)
            .subquery()
        )
        query = select(Result).join(
            subquery,
            and_(
                Result.company_member_id == subquery.c.company_member_id,
                Result.quiz_id == subquery.c.quiz_id,
                Result.created_at == subquery.c.created_at,
            ),
        )

        result = await self.session.execute(query)
        return result.scalars().all()
