import json
import uuid
from datetime import timedelta
from typing import List, Optional, Dict

import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.file_format import FileFormat
from app.exept.custom_exceptions import (
    NotFound,
    NotPermission,
    BadRequest,
    UserNotFound,
    CompanyNotFound,
)
from app.models.result_model import Result
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.result_repository import ResultRepository
from app.repository.user_repository import UserRepository
from app.schemas.actions import CompanyMemberSchema
from app.schemas.companies import CompanySchema
from app.schemas.results import ResultSchema, QuizRequest, ExportedFile
from app.services.redis_service import redis_service
from app.utils.export_data import export_redis_data


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

    async def _get_company_or_raise(self, company_id: uuid.UUID) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise CompanyNotFound()
        return company

    async def create_result(
        self, quiz_id: uuid.UUID, current_user_id: uuid.UUID, quiz_request: QuizRequest
    ) -> ResultSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company_id = quiz.company_id
        if quiz is None:
            raise NotFound()

        member = await self._validate_is_company_member(current_user_id, company_id)
        questions = await self.quiz_repository.get_questions_by_quiz_id(quiz_id)

        redis_result = {
            "user_id": str(current_user_id),
            "company_id": str(company_id),
            "quiz_id": str(quiz_id),
            "questions": [],
        }

        total_questions = 0
        correct_answers = 0

        for question in questions:
            total_questions += 1
            answer = quiz_request.answers.get(question.id)

            question_data = {
                "question": question.question_text,
                "user_answer": answer,
                "is_correct": answer == question.correct_answer,
            }
            redis_result["questions"].append(question_data)

            is_correct = set(answer) == set(question.correct_answer)
            if is_correct:
                correct_answers += 1

        score = correct_answers / total_questions
        rounded_score = round(score, 2)

        result = Result(
            company_member_id=member.id,
            quiz_id=quiz_id,
            correct_answers=correct_answers,
            total_questions=total_questions,
            score=rounded_score,
        )
        result_schema = ResultSchema.from_orm(result)

        result = await self.result_repository.create_one(result_schema.dict())
        result_id = str(result.id)

        key = f"quiz_result:{current_user_id}:{company_id}:{quiz_id}:{result_id}"
        serialized_result = json.dumps(redis_result)
        expiration_time_seconds = int(timedelta(hours=48).total_seconds())
        await redis_service.redis_set(key, serialized_result, expiration_time_seconds)

        return ResultSchema.from_orm(result)

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

    async def _validate_export(
        self, company_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not await self.company_repository.is_user_company_owner(
            current_user_id, company.id
        ):
            raise NotPermission()
        if not company:
            raise NotFound()
        return company

    @staticmethod
    async def _check_export_format(file_format: FileFormat) -> None:
        if file_format not in [FileFormat.JSON, FileFormat.CSV]:
            raise BadRequest()

    async def company_answers_list(
        self, company_id: uuid.UUID, file_format: FileFormat, current_user_id: uuid.UUID
    ) -> ExportedFile:
        await self._validate_export(company_id, current_user_id)
        query = f"quiz_result:*:{company_id}:*"
        return await export_redis_data(query=query, file_format=file_format)

    async def user_answers_list(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        file_format: FileFormat,
        current_user_id: uuid.UUID,
    ) -> ExportedFile:
        await self._validate_export(company_id, current_user_id)
        user = await self.user_repository.get_one(id=user_id)
        if not user:
            raise UserNotFound()
        query = f"quiz_result:{user_id}:{company_id}:*"
        return await export_redis_data(query=query, file_format=file_format)

    async def my_answers_list(self, current_user_id, file_format) -> ExportedFile:
        await self._check_export_format(file_format)
        await self.user_repository.get_one(id=current_user_id)
        query = f"quiz_result:{current_user_id}:*:*"
        return await export_redis_data(query=query, file_format=file_format)

    @staticmethod
    async def _make_chart_data(results: List) -> Dict:
        chart_data = {}
        current_total_questions = 0
        current_correct_answers = 0
        for result in results:
            current_total_questions += result.total_questions
            current_correct_answers += result.correct_answers
            chart_data[result.created_at] = (
                round((current_correct_answers / current_total_questions), 2)
            )

        return chart_data

    async def my_quiz_results(self, current_user_id, quiz_id: uuid.UUID) -> Dict:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company_id = quiz.company_id
        if not quiz:
            raise NotFound()
        member = await self._validate_is_company_member(current_user_id, company_id)
        results = await self.result_repository.get_many(
            company_member_id=member.id, quiz_id=quiz_id
        )
        chart_data = await self._make_chart_data(results)
        return chart_data

    async def my_quizzes_latest_results(self, current_user_id: uuid.UUID) -> Dict:
        results = await self.result_repository.get_latest_results_for_company_member(
            current_user_id
        )
        latest_results = {}
        for result in results:
            latest_results[result.quiz_id] = result.created_at.isoformat()
        return latest_results

    async def _validate_company_owner_analytics(
        self, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> None:
        owner = await self.company_repository.is_user_company_owner(
            current_user_id, company_id
        )
        if not owner:
            raise NotPermission()

    async def _validate_company_owner_or_admin_analytics(
        self, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> None:
        owner = await self.company_repository.is_user_company_owner(
            current_user_id, company_id
        )
        admin = await self.company_repository.is_user_company_admin(
            current_user_id, company_id
        )
        if not (owner or admin):
            raise NotPermission()

    async def company_members_results(
        self, current_user_id: uuid.UUID, company_id: uuid.UUID
    ) -> Dict:
        await self._get_company_or_raise(company_id)
        await self._validate_company_owner_or_admin_analytics(current_user_id, company_id)
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise CompanyNotFound()

        results = await self.company_repository.get_company_members_result_data(
            company_id
        )

        member_results = {}
        for result, username in results:
            if username not in member_results:
                member_results[username] = []
            member_results[username].append(result)

        chart_data = {}
        for username, member_result in member_results.items():
            chart_data[username] = await self._make_chart_data(member_result)

        return chart_data

    async def company_member_results(
        self, company_id: uuid.UUID, company_member_id, current_user_id: uuid.UUID
    ) -> Dict:
        await self._get_company_or_raise(company_id)
        await self._validate_company_owner_analytics(current_user_id, company_id)
        member = await self.company_repository.get_company_member(
            company_member_id, company_id
        )
        if not member:
            raise NotFound
        results = await self.result_repository.get_many(company_member_id=member.id)
        chart_data = await self._make_chart_data(results)
        return chart_data

    async def company_members_result_last(
        self, company_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> Dict:
        await self._get_company_or_raise(company_id)
        await self._validate_company_owner_analytics(current_user_id, company_id)

        latest_results = await self.result_repository.get_latest_results_for_company(
            company_id
        )
        results_dict = {}

        for result in latest_results:
            user_id = result.company_member_id
            if user_id not in results_dict:
                results_dict[user_id] = {}
            results_dict[user_id][result.quiz_id] = result.created_at

        return results_dict
