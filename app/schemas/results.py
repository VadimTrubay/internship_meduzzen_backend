import uuid
from typing import List, Dict

from pydantic import BaseModel, ConfigDict


class ResultSchema(BaseModel):
    company_member_id: uuid.UUID
    quiz_id: uuid.UUID
    score: float
    total_questions: int
    correct_answers: int

    model_config = ConfigDict(from_attributes=True)


class UserQuizResultSchema(BaseModel):
    quiz_id: uuid.UUID
    quiz_name: str
    company_id: uuid.UUID
    company_name: str
    last_attempt: str
    average_score: float


class QuizRequest(BaseModel):
    answers: Dict[uuid.UUID, List[str]]


class CompanyRating(BaseModel):
    company_member_id: uuid.UUID
    company_id: uuid.UUID
    rating: int


class ExportedFile(BaseModel):
    file: bytes
    filename: str
