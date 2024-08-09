import uuid
from typing import Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.invite import MemberStatus
from app.exept.custom_exceptions import NotFound, NotPermission, BadRequest
from app.models.quiz_model import Question
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.schemas.companies import CompanySchema
from app.schemas.quizzes import (
    QuizSchema,
    QuizUpdateSchema,
    QuestionSchema,
    QuizResponseSchema,
    QuizzesListResponse,
    QuizByIdSchema, QuestionByIdSchema,
)


class QuizService:
    def __init__(
        self,
        session: AsyncSession,
        quiz_repository: QuizRepository,
        action_repository: ActionRepository,
        company_repository: CompanyRepository,
    ):
        self.session = session
        self.quiz_repository = quiz_repository
        self.action_repository = action_repository
        self.company_repository = company_repository

    # GET COMPANY OR RAISE
    async def _get_company_or_raise(self, company_id: uuid.UUID) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise NotFound()
        return company

    # GET TOTAL COUNT
    async def get_total_count(self):
        count = await self.quiz_repository.get_count()
        return count

    # GET QUIZZES
    async def get_quizzes(self, company_id: uuid.UUID) -> QuizzesListResponse:
        quizzes = await self.quiz_repository.get_many(company_id=company_id)
        quiz_responses = [
            QuizResponseSchema(
                id=quiz.id,
                name=quiz.name,
                description=quiz.description,
                frequency_days=quiz.frequency_days,
            )
            for quiz in quizzes
        ]
        return quiz_responses

    # GET VALIDATE QUIZ DATA
    @staticmethod
    async def _validate_quiz_data(quiz_data: QuizSchema) -> None:
        MIN_QUESTIONS = 2
        MIN_ANSWER_OPTIONS = 2
        if len(quiz_data.questions) < MIN_QUESTIONS or any(
            len(question.answer_options) < MIN_ANSWER_OPTIONS
            for question in quiz_data.questions
        ):
            raise BadRequest()

        for question in quiz_data.questions:
            if not question.correct_answer:
                raise BadRequest()

            for answer in question.correct_answer:
                if answer not in question.answer_options:
                    raise BadRequest()

    # CREATE QUIZ
    async def create_quiz(
        self, quiz_data: QuizSchema, company_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> QuizSchema:
        member = await self.company_repository.get_company_member(
            current_user_id, company_id
        )
        if not member:
            raise NotFound()
        if member.role not in [MemberStatus.OWNER, MemberStatus.ADMIN]:
            raise NotPermission()
        await self._validate_quiz_data(quiz_data)
        await self.quiz_repository.create_quiz(quiz_data, company_id=company_id)
        quiz_dict = quiz_data.dict(exclude={"questions"})
        question_dicts = [question.dict() for question in quiz_data.questions]
        created_quiz_schema = QuizSchema(
            **quiz_dict, questions=question_dicts, company_id=company_id
        )
        return created_quiz_schema

    # VALIDATE QUIZ
    async def _validate_quiz(
        self, quiz_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> QuizSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        if not quiz:
            raise NotFound()
        company_id = quiz.company_id
        await self._get_company_or_raise(company_id)
        await self.company_repository.is_user_company_owner(current_user_id, company_id)
        return quiz

    # UPDATE QUIZ
    async def update_quiz(
        self,
        quiz_id: uuid.UUID,
        quiz_data: QuizUpdateSchema,
        current_user_id: uuid.UUID,
    ) -> QuizByIdSchema:
        quiz = await self._validate_quiz(quiz_id, current_user_id)

        if quiz_data.name is not None:
            quiz.name = quiz_data.name
        if quiz_data.description is not None:
            quiz.description = quiz_data.description
        if quiz_data.frequency_days is not None:
            quiz.frequency_days = quiz_data.frequency_days

        if quiz_data.questions is not None:
            await self.session.execute(
                delete(Question).where(Question.quiz_id == quiz_id)
            )
            await self.session.commit()

            questions = [
                Question(
                    quiz_id=quiz_id,
                    question_text=q.question_text,
                    correct_answer=q.correct_answer,
                    answer_options=q.answer_options,
                )
                for q in quiz_data.questions
            ]
            self.session.add_all(questions)

        await self.session.commit()
        await self.session.refresh(quiz)

        updated_quiz = await self.quiz_repository.quiz_by_id(quiz_id)

        return QuizByIdSchema.from_orm(updated_quiz)

    # DELETE QUIZ
    async def delete_quiz(self, quiz_id: uuid.UUID, current_user_id: uuid.UUID) -> dict:
        await self._validate_quiz(quiz_id, current_user_id)
        await self.quiz_repository.delete_quiz(quiz_id)
        return {"message": "Quiz deleted", "id": quiz_id}

    # GET QUIZ BY ID
    async def get_quiz_by_id(self, quiz_id: uuid.UUID) -> Optional[QuizByIdSchema]:
        quiz = await self.quiz_repository.quiz_by_id(quiz_id)
        if not quiz:
            raise NotFound()

        quiz_schema = QuizByIdSchema(
            id=quiz.id,
            name=quiz.name,
            description=quiz.description,
            frequency_days=quiz.frequency_days,
            questions=[
                QuestionByIdSchema(
                    id=question.id,
                    question_text=question.question_text,
                    correct_answer=question.correct_answer,
                    answer_options=question.answer_options,
                )
                for question in quiz.questions
            ],
        )
        return quiz_schema

    # HANDLE IS ACTIVE
    async def _handle_is_active(self, quiz_id: uuid.UUID) -> None:
        questions = await self.quiz_repository.get_questions_by_quiz_id(quiz_id)
        if len(questions) < 2:
            await self.quiz_repository.toggle_quiz_active_status(quiz_id, False)
        else:
            await self.quiz_repository.toggle_quiz_active_status(quiz_id, True)
