from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"

    name = Column(String(50), nullable=False)
    description = Column(String(1500), nullable=False)
    visible = Column(Boolean, default=True)

    actions = relationship("CompanyAction", backref="company", cascade="all, delete")
