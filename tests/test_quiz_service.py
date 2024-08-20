import uuid
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.invite import MemberStatus
from app.services.quiz_service import QuizService
from app.repository.quizzes_repository import QuizRepository
from app.repository.company_repository import CompanyRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.user_repository import UserRepository
from app.repository.action_repository import ActionRepository
from app.schemas.quizzes import (
    QuizSchema,
    QuestionSchema,
)


@pytest.fixture
def setup_quiz_service():
    session = AsyncMock(spec=AsyncSession)
    quiz_repository = AsyncMock(spec=QuizRepository)
    action_repository = AsyncMock(spec=ActionRepository)
    company_repository = AsyncMock(spec=CompanyRepository)
    notification_repository = AsyncMock(spec=NotificationRepository)
    user_repository = AsyncMock(spec=UserRepository)

    return QuizService(
        session=session,
        quiz_repository=quiz_repository,
        action_repository=action_repository,
        company_repository=company_repository,
        notification_repository=notification_repository,
        user_repository=user_repository,
    )


@pytest.mark.asyncio
async def test_create_quiz_success(setup_quiz_service):
    service = setup_quiz_service
    company_id = uuid.uuid4()
    current_user_id = uuid.uuid4()

    quiz_data = QuizSchema(
        name="New Quiz",
        description="Quiz Description",
        frequency_days=7,
        questions=[
            QuestionSchema(
                question_text="What is 2+2?",
                correct_answer=["4"],
                answer_options=["3", "4", "5"],
            ),
            QuestionSchema(
                question_text="What is the capital of France?",
                correct_answer=["Paris"],
                answer_options=["Berlin", "Madrid", "Paris"],
            ),
        ],
    )

    company = AsyncMock(name="Company")
    company.name = "Company Name"
    service.company_repository.get_one.return_value = company

    member = AsyncMock()
    member.role = MemberStatus.OWNER
    service.company_repository.get_company_member.return_value = member

    service.quiz_repository.create_quiz.return_value = None
    service.notification_repository.create_notifications_for_users.return_value = None

    result = await service.create_quiz(quiz_data, company_id, current_user_id)

    assert result.name == "New Quiz"
    assert result.description == "Quiz Description"
    assert result.frequency_days == 7
    assert len(result.questions) == 2


@pytest.mark.asyncio
async def test_delete_quiz_success(setup_quiz_service):
    service = setup_quiz_service
    quiz_id = uuid.uuid4()
    current_user_id = uuid.uuid4()

    quiz = AsyncMock(name="Quiz")
    quiz.id = quiz_id
    quiz.name = "Quiz Name"
    quiz.description = "Quiz Description"
    quiz.frequency_days = 7
    service.quiz_repository.get_one.return_value = quiz
    service.company_repository.is_user_company_owner.return_value = True

    service.quiz_repository.delete_quiz.return_value = None

    result = await service.delete_quiz(quiz_id, current_user_id)

    assert result.id == quiz_id


@pytest.mark.asyncio
async def test_get_quiz_by_id_success(setup_quiz_service):
    service = setup_quiz_service
    quiz_id = uuid.uuid4()

    quiz = AsyncMock(name="Quiz")
    quiz.id = quiz_id
    quiz.name = "Quiz Name"
    quiz.description = "Quiz Description"
    quiz.frequency_days = 7
    quiz.questions = []
    service.quiz_repository.quiz_by_id.return_value = quiz

    result = await service.get_quiz_by_id(quiz_id)

    assert result.id == quiz_id


@pytest.mark.asyncio
async def test_validate_quiz_data_success(setup_quiz_service):
    service = setup_quiz_service
    quiz_data = QuizSchema(
        name="Sample Quiz",
        description="Description",
        frequency_days=5,
        questions=[
            QuestionSchema(
                question_text="What is 2+2?",
                correct_answer=["4"],
                answer_options=["3", "4", "5"],
            ),
            QuestionSchema(
                question_text="What is 3+3?",
                correct_answer=["6"],
                answer_options=["5", "6", "7"],
            ),
        ],
    )

    await service._validate_quiz_data(quiz_data)


@pytest.mark.asyncio
async def test_validate_quiz_success(setup_quiz_service):
    service = setup_quiz_service
    quiz_id = uuid.uuid4()
    current_user_id = uuid.uuid4()

    quiz = AsyncMock(name="Quiz")
    quiz.id = quiz_id
    quiz.name = "Quiz Name"
    quiz.description = "Quiz Description"
    quiz.frequency_days = 7
    service.quiz_repository.get_one.return_value = quiz
    service.company_repository.is_user_company_owner.return_value = True

    result = await service._validate_quiz(quiz_id, current_user_id)

    assert result.id == quiz_id
