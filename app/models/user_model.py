from sqlalchemy import Column, String, Boolean

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String)
    is_admin = Column(Boolean, nullable=False, default=False)
