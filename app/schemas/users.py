import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class BaseUserSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseUserSchema):
    is_admin: bool


class UserResponse(BaseUserSchema):
    password: str
    is_admin: bool


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
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]


class UserDetailResponse(BaseUserSchema):
    is_admin: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "user1",
                "email": "user1@example.com",
                "is_admin": True,
            }
        },
    )


class UsersListResponse(BaseModel):
    users: List[BaseUserSchema]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
        },
        strict=True,
    )
