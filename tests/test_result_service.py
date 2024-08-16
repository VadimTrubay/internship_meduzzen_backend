import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.conf.file_format import FileFormat
from app.services.result_service import ResultService
from app.schemas.results import QuizRequest, ResultSchema, UserQuizResultSchema
from app.exept.custom_exceptions import (
    NotFound,
    NotPermission,
    CompanyNotFound,
    UserNotFound,
)
from app.utils.export_data import ExportedFile


@pytest.mark.asyncio
class TestResultService:
    @pytest.fixture
    def result_service(self):
        session = MagicMock()
        quiz_repository = MagicMock()
        company_repository = MagicMock()
        user_repository = MagicMock()
        result_repository = MagicMock()
        return ResultService(
            session=session,
            quiz_repository=quiz_repository,
            company_repository=company_repository,
            user_repository=user_repository,
            result_repository=result_repository,
        )

    @pytest.fixture
    def current_user(self):
        return MagicMock(
            id=uuid4(), username="current_user", email="current_user@example.com"
        )

    @pytest.fixture
    def company(self):
        return MagicMock(id=uuid4())

    @pytest.fixture
    def result(self):
        return MagicMock(
            id=uuid4(), score=0.85, company_member_id=uuid4(), quiz_id=uuid4()
        )

    @pytest.fixture
    def quiz(self):
        return MagicMock(id=uuid4(), company_id=uuid4())

    @pytest.fixture
    def quiz_request(self):
        return QuizRequest(answers={uuid4(): ["A"], uuid4(): ["B"]})

    # async def test_create_result_success(
    #         self, result_service, quiz, company, current_user, quiz_request, result
    # ):
    #     result_service.quiz_repository.get_one = AsyncMock(return_value=quiz)
    #     result_service.company_repository.get_company_member = AsyncMock(
    #         return_value=current_user
    #     )
    #     result_service.quiz_repository.get_questions_by_quiz_id = AsyncMock(
    #         return_value=[]
    #     )
    #     result_service.result_repository.create_one = AsyncMock(return_value=result)
    #     result_service._get_user_or_raise = AsyncMock(return_value=current_user)
    #
    #     result = await result_service.create_result(
    #         quiz.id, current_user.id, quiz_request
    #     )
    #
    #     assert result == ResultSchema.from_orm(result)
    #     result_service.result_repository.create_one.assert_called_once()
    #
    # async def test_create_result_not_found(
    #         self, result_service, quiz, current_user, quiz_request
    # ):
    #     result_service.quiz_repository.get_one = AsyncMock(return_value=None)
    #
    #     with pytest.raises(NotFound):
    #         await result_service.create_result(uuid4(), current_user.id, quiz_request)

    async def test_get_company_rating_success(
        self, result_service, company, current_user, result
    ):
        result_service.company_repository.get_one = AsyncMock(return_value=company)
        result_service.company_repository.get_company_member = AsyncMock(
            return_value=current_user
        )
        result_service.result_repository.get_many = AsyncMock(return_value=[result])

        rating = await result_service.get_company_rating(current_user.id, company.id)
        assert rating == (1, 2)  # Проверьте правильность этого значения

    async def test_get_company_rating_not_found(
        self, result_service, company, current_user
    ):
        result_service.company_repository.get_one = AsyncMock(return_value=company)
        result_service.company_repository.get_company_member = AsyncMock(
            return_value=current_user
        )
        result_service.result_repository.get_many = AsyncMock(return_value=[])

        with pytest.raises(NotFound):
            await result_service.get_company_rating(current_user.id, company.id)

    # async def test_company_answers_list_success(
    #         self, result_service, company, current_user
    # ):
    #     result_service.company_repository.get_one = AsyncMock(return_value=company)
    #     result_service.company_repository.is_user_company_owner = AsyncMock(
    #         return_value=True
    #     )
    #     export_data = ExportedFile(file_name="data.json", content=b"{}")
    #     result_service.export_redis_data = AsyncMock(return_value=export_data)
    #
    #     file = await result_service.company_answers_list(
    #         company.id, FileFormat.JSON, current_user.id
    #     )
    #     assert file == export_data

    async def test_company_answers_list_not_permission(
        self, result_service, company, current_user
    ):
        result_service.company_repository.get_one = AsyncMock(return_value=company)
        result_service.company_repository.is_user_company_owner = AsyncMock(
            return_value=False
        )

        with pytest.raises(NotPermission):
            await result_service.company_answers_list(
                company.id, FileFormat.JSON, current_user.id
            )

    async def test_my_quiz_results_success(
        self, result_service, quiz, current_user, result
    ):
        result_service.quiz_repository.get_one = AsyncMock(return_value=quiz)
        result_service.company_repository.get_company_member = AsyncMock(
            return_value=current_user
        )
        result_service.result_repository.get_many = AsyncMock(return_value=[result])
        result_service._make_chart_data = AsyncMock(return_value={"2024-08-16": 0.85})

        chart_data = await result_service.my_quiz_results(current_user.id, quiz.id)
        assert chart_data == {"2024-08-16": 0.85}

    # async def test_my_quiz_results_not_found(self, result_service, quiz, current_user):
    #     result_service.quiz_repository.get_one = AsyncMock(return_value=quiz)
    #     result_service.company_repository.get_company_member = AsyncMock(
    #         return_value=current_user
    #     )
    #     result_service.result_repository.get_many = AsyncMock(return_value=[])
    #
    #     with pytest.raises(NotFound):
    #         await result_service.my_quiz_results(current_user.id, quiz.id)
