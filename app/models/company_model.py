from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"

    name = Column(String(50), nullable=False)
    description = Column(String(1500), nullable=False)
    visible = Column(Boolean, default=True)

    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User", back_populates="companies_owned")
