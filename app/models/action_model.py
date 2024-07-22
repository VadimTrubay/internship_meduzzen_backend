from sqlalchemy import Column, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.conf.invite import InvitationStatus, InvitationType
from app.models.base_model import BaseModel


class CompanyAction(BaseModel):
    __tablename__ = "actions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    status = Column(Enum(InvitationStatus), nullable=False)
    type = Column(Enum(InvitationType), nullable=False)
