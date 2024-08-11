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


class QuizRequest(BaseModel):
    answers: Dict[uuid.UUID, List[str]]
