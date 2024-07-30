import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class BaseUserSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseUserSchema):
    password: str


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    username: str
    email: EmailStr
    access_token: str
    token_type: str


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    new_password: Optional[str] = None


class UserDetailResponse(BaseUserSchema):

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "user1",
                "email": "user1@example.com",
            }
        },
    )


class UsersListResponse(BaseModel):
    users: List[BaseUserSchema]
    total_count: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "user1",
                        "email": "user1@example.com",
                    },
                    {
                        "id": "223e4567-e89b-12d3-a456-426614174001",
                        "username": "user2",
                        "email": "user2@example.com",
                    },
                ],
                "total_count": 0,
            }
        },
        strict=True,
    )
