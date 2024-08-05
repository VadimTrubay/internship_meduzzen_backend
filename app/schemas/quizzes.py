from typing import List

from pydantic import BaseModel, ConfigDict


class QuestionSchema(BaseModel):
    question_text: str
    correct_answer: List[str]
    options: List[str]


class QuizSchema(BaseModel):
    name: str
    description: str
    frequency_days: int
    questions: List[QuestionSchema]


class QuizUpdateSchema(BaseModel):
    name: str
    description: str
    frequency_days: int


class QuizResponseSchema(BaseModel):
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
