import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.conf.file_format import FileFormat
from app.schemas.results import (
    ResultSchema,
    QuizRequest,
)
from app.services.result_service import ResultService
from app.exept.custom_exceptions import (
    NotFound,
    NotPermission,
    UserNotFound,
)


@pytest.fixture
def setup_result_service():
    session = AsyncMock()
    quiz_repository = AsyncMock()
    company_repository = AsyncMock()
    user_repository = AsyncMock()
    result_repository = AsyncMock()
    return ResultService(
        session=session,
        quiz_repository=quiz_repository,
        company_repository=company_repository,
        user_repository=user_repository,
        result_repository=result_repository,
    )


@pytest.mark.asyncio
async def test_get_global_rating_success(setup_result_service):
    service = setup_result_service
    current_user_id = uuid4()

    members = [AsyncMock(id=uuid4()), AsyncMock(id=uuid4())]
    service.user_repository.get_company_members_by_user_id.return_value = members

    results = [
        ResultSchema(
            company_member_id=members[0].id,
            quiz_id=uuid4(),
            score=0.75,
            total_questions=10,
            correct_answers=7,
        ),
        ResultSchema(
            company_member_id=members[1].id,
            quiz_id=uuid4(),
            score=0.85,
            total_questions=10,
            correct_answers=8,
        ),
    ]
    service.result_repository.get_many.side_effect = [results, results]

    global_rating = await service.get_global_rating(current_user_id)
    assert global_rating == 0.80


@pytest.mark.asyncio
async def test_user_answers_list_user_not_found(setup_result_service):
    service = setup_result_service
    company_id = uuid4()
    user_id = uuid4()
    file_format = FileFormat.JSON
    current_user_id = uuid4()

    service.company_repository.get_one.return_value = AsyncMock()
    service.company_repository.is_user_company_owner.return_value = True
    service.user_repository.get_one.return_value = None

    with pytest.raises(UserNotFound):
        await service.user_answers_list(
            company_id, user_id, file_format, current_user_id
        )


@pytest.mark.asyncio
async def test_create_result_permission_denied(setup_result_service):
    service = setup_result_service
    quiz_id = uuid4()
    current_user_id = uuid4()
    quiz_request = QuizRequest(answers={uuid4(): ["answer"]})

    quiz = AsyncMock()
    quiz.company_id = uuid4()
    questions = [
        AsyncMock(id=uuid4(), question_text="What?", correct_answer=["answer"])
    ]

    service.quiz_repository.get_one.return_value = quiz
    service.quiz_repository.get_questions_by_quiz_id.return_value = questions
    service.company_repository.get_company_member.return_value = None

    with pytest.raises(NotPermission):
        await service.create_result(quiz_id, current_user_id, quiz_request)


@pytest.mark.asyncio
async def test_get_company_rating_no_results(setup_result_service):
    service = setup_result_service
    company_id = uuid4()
    current_user_id = uuid4()

    company = AsyncMock()
    service.company_repository.get_one.return_value = company

    member = AsyncMock(id=uuid4())
    service.company_repository.get_company_member.return_value = member

    service.result_repository.get_many.return_value = []

    with pytest.raises(NotFound):
        await service.get_company_rating(current_user_id, company_id)


@pytest.mark.asyncio
async def test_get_global_rating_no_results(setup_result_service):
    service = setup_result_service
    current_user_id = uuid4()

    members = [AsyncMock(id=uuid4()), AsyncMock(id=uuid4())]
    service.user_repository.get_company_members_by_user_id.return_value = members

    service.result_repository.get_many.side_effect = [[], []]

    with pytest.raises(NotFound):
        await service.get_global_rating(current_user_id)


@pytest.mark.asyncio
async def test_company_answers_list_permission_denied(setup_result_service):
    service = setup_result_service
    company_id = uuid4()
    file_format = FileFormat.JSON
    current_user_id = uuid4()

    company = AsyncMock()
    service.company_repository.get_one.return_value = company
    service.company_repository.is_user_company_owner.return_value = False

    with pytest.raises(NotPermission):
        await service.company_answers_list(company_id, file_format, current_user_id)


@pytest.mark.asyncio
async def test_my_quizzes_latest_results_empty(setup_result_service):
    service = setup_result_service
    current_user_id = uuid4()

    service.result_repository.get_latest_results_for_company_member.return_value = []

    latest_results = await service.my_quizzes_latest_results(current_user_id)
    assert latest_results == {}


@pytest.mark.asyncio
async def test_my_quiz_results_empty(setup_result_service):
    service = setup_result_service
    current_user_id = uuid4()
    quiz_id = uuid4()

    quiz = AsyncMock()
    quiz.company_id = uuid4()
    service.quiz_repository.get_one.return_value = quiz

    member = AsyncMock(id=uuid4())
    service.company_repository.get_company_member.return_value = member

    service.result_repository.get_many.return_value = []

    result_data = await service.my_quiz_results(current_user_id, quiz_id)
    assert result_data.data == {}
