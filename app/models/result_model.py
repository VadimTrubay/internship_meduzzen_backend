from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship, backref

from app.models.base_model import BaseModel


class Result(BaseModel):
    __tablename__ = "results"

    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer)
    company_member_id = Column(UUID(as_uuid=True), ForeignKey("company_members.id"))

    company_member = relationship(
        "CompanyMember", backref=backref("results", cascade="all, delete-orphan")
    )
