import uuid
from typing import List, Dict

from pydantic import BaseModel


class ResultSchema(BaseModel):
    company_member_id: uuid.UUID
    quiz_id: uuid.UUID
    score: float
    total_questions: int
    correct_answers: int


class QuizRequest(BaseModel):
    answers: Dict[int, List[str]]
