import uuid
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator
from datetime import date

from app.models.user_model import Role


class BaseUserSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None
    created_at: date

    class Config:
        orm_mode = True


class UserSchema(BaseUserSchema):
    password: str
    roles: Role
    confirmed: bool
    is_active: bool


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[EmailStr]

    @classmethod
    @field_validator("email")
    def remove_empty_email(cls, v: EmailStr) -> EmailStr:
        return EmailStr() if v is not None and v != "" else None

    @classmethod
    @field_validator("username")
    def remove_empty_username(cls, v: str) -> str:
        return v if v is not None and v != "" else None


class UserDetailResponse(BaseUserSchema):
    roles: Role
    is_active: bool


class UsersListResponse(BaseModel):
    users: List[BaseUserSchema]
    total_count: int


class RequestEmail(BaseModel):
    email: EmailStr
