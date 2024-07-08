import uuid
from typing import List

from pydantic import BaseModel, EmailStr


class BaseUserSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserSchema(BaseUserSchema):
    hashed_password: str
    is_admin: bool


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str


class SignInRequest(BaseModel):
    email: EmailStr
    hashed_password: str


class UserUpdateRequest(BaseModel):
    username: str | None
    hashed_password: str | None
    email: str | None


class UserDetailResponse(BaseUserSchema):
    is_admin: bool

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "user1",
                "email": "user1@example.com",
                "is_admin": True,
            }
        }


class UsersListResponse(BaseModel):
    users: List[UserDetailResponse]

    class Config:
        schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "user1",
                        "email": "user1@example.com",
                        "is_admin": True,
                    },
                    {
                        "id": "223e4567-e89b-12d3-a456-426614174001",
                        "username": "user2",
                        "email": "user2@example.com",
                        "is_admin": False,
                    },
                ]
            }
        }
