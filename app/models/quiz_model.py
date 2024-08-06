from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import BaseModel


class Quiz(BaseModel):
    __tablename__ = "quizzes"

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    frequency_days = Column(Integer, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(BaseModel):
    __tablename__ = "questions"

    question_text = Column(String(1000), nullable=False)
    correct_answer = Column(ARRAY(String(255)), nullable=False)
    answer_options = Column(ARRAY(String(255)), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    quiz = relationship("Quiz", back_populates="questions")
