import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class QuestionSchema(BaseModel):
    question_text: str
    correct_answer: List[str]
    answer_options: List[str]

    model_config = ConfigDict(from_attributes=True)


class QuizSchema(BaseModel):
    name: str
    description: str
    frequency_days: int
    questions: List[QuestionSchema]

    model_config = ConfigDict(from_attributes=True)


class QuestionByIdSchema(BaseModel):
    id: uuid.UUID
    question_text: str
    correct_answer: List[str]
    answer_options: List[str]

    model_config = ConfigDict(from_attributes=True)


class QuizByIdSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    frequency_days: int
    questions: List[QuestionByIdSchema]

    model_config = ConfigDict(from_attributes=True)


class QuizUpdateSchema(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    description: Optional[str] = None
    frequency_days: Optional[int] = None
    questions: Optional[List[QuestionSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class QuizResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    frequency_days: int


class QuizzesListResponse(BaseModel):
    quizzes: List[QuizResponseSchema]
    total_count: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "quizzes": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174003",
                        "name": "Quizz name",
                        "description": "Description quiz",
                        "frequency_days": 5,
                    },
                    {
                        "id": "223e4567-e89b-12d3-a456-426614174031",
                        "name": "Quizz name",
                        "description": "Description quiz",
                        "frequency_days": 3,
                    },
                ],
                "total_count": 0,
            }
        },
        strict=True,
    )
