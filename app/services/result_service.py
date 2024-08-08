import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exept.custom_exceptions import NotFound, NotPermission
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.result_repository import ResultRepository
from app.repository.user_repository import UserRepository
from app.schemas.actions import CompanyMemberSchema
from app.schemas.results import ResultSchema, QuizRequest


class ResultService:
    def __init__(
        self,
        session: AsyncSession,
        quiz_repository: QuizRepository,
        company_repository: CompanyRepository,
        user_repository: UserRepository,
        result_repository: ResultRepository,
    ):
        self.session = session
        self.quiz_repository = quiz_repository
        self.company_repository = company_repository
        self.user_repository = user_repository
        self.result_repository = result_repository

    async def _validate_is_company_member(
        self, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> CompanyMemberSchema:
        member = await self.company_repository.get_company_member(user_id, company_id)
        if not member:
            raise NotPermission()
        return member

    async def create_result(
        self, quiz_id: uuid.UUID, current_user_id: uuid.UUID, quiz_request: QuizRequest
    ) -> ResultSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company_id = quiz.company_id
        if quiz is None:
            raise NotFound()
        member = await self._validate_is_company_member(current_user_id, company_id)
        questions = await self.quiz_repository.get_questions_by_quiz_id(quiz_id)
        total_questions = 0
        correct_answers = 0
        for question in questions:
            total_questions += 1
            answer = quiz_request.answers.get(question.id)
            is_correct = set(answer) == set(question.correct_answer)
            if is_correct:
                correct_answers += 1
        score = correct_answers / total_questions
        rounded_score = round(score, 2)
        result_data = {
            "company_member_id": member.id,
            "quiz_id": quiz_id,
            "score": rounded_score,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
        }
        await self.result_repository.create_one(result_data)
        return ResultSchema(**result_data)

    async def get_company_rating(
        self, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> float:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise NotFound()
        member = await self._validate_is_company_member(current_user_id, company.id)
        results = await self.result_repository.get_many(company_member_id=member.id)
        if not results:
            raise NotFound()

        total_score = sum(result.score for result in results)
        average_score = total_score / len(results) if len(results) > 0 else 0.0

        return average_score

    async def get_global_rating(self, current_user_id: uuid.UUID) -> float:
        members = await self.user_repository.get_company_members_by_user_id(
            current_user_id
        )
        if not members:
            raise NotFound()
        total_average_score = 0
        total_count = 0
        for member in members:
            results = await self.result_repository.get_many(company_member_id=member.id)
            if results:
                total_score = sum(result.score for result in results)
                average_score = total_score / len(results)
                total_average_score += average_score
                total_count += 1
        if total_count == 0:
            raise NotFound()
        global_average_score = total_average_score / total_count
        return global_average_score
