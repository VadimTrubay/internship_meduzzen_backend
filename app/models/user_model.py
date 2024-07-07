import enum

from sqlalchemy import Column, String, Boolean, Enum

from app.models.base_model import BaseModel


class Role(enum.Enum):
    admin: str = "admin"
    user: str = "user"


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    roles = Column("roles", Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
