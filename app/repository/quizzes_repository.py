import uuid
from typing import List

from sqlalchemy import delete, select, func
from sqlalchemy.orm import joinedload

from app.repository.base_repository import BaseRepository
from app.models.quiz_model import Quiz, Question
from app.schemas.quizzes import QuizSchema


class QuizRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Quiz)

    async def get_count_quizzes(self, company_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Quiz).where(Quiz.company_id == company_id)
        result = await self.session.execute(query)
        quiz_count = result.scalar()
        return quiz_count

    async def create_quiz(
        self, quiz_data: QuizSchema, company_id: uuid.UUID
    ) -> QuizSchema:
        quiz_dict = quiz_data.dict(exclude={"questions"})
        quiz = await self.create_one(dict(**quiz_dict, company_id=company_id))

        questions = [
            Question(
                quiz_id=quiz.id,
                question_text=question_data.question_text,
                correct_answer=question_data.correct_answer,
                answer_options=question_data.answer_options,
            )
            for question_data in quiz_data.questions
        ]

        self.session.add_all(questions)
        await self.session.commit()
        return quiz

    async def delete_quiz(self, quiz_id: uuid.UUID) -> None:
        query = delete(Question).where(Question.quiz_id == quiz_id)
        await self.session.execute(query)
        await self.session.commit()
        await self.delete_one(quiz_id)

    async def quiz_by_id(self, quiz_id: uuid.UUID):
        query = (
            select(Quiz).options(joinedload(Quiz.questions)).filter(Quiz.id == quiz_id)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().one_or_none()

    async def get_questions_by_quiz_id(self, quiz_id: uuid.UUID) -> List[Question]:
        query = select(Question).filter(Question.quiz_id == quiz_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def toggle_quiz_active_status(
        self, quiz_id: uuid.UUID, new_status: bool
    ) -> None:
        quiz = await self.get_one(id=quiz_id)
        quiz.is_active = new_status
        await self.session.commit()
