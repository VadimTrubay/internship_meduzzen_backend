from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    company_memberships = relationship(
        "CompanyMember", backref="user", cascade="all, delete"
    )
