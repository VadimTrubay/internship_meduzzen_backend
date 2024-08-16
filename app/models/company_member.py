from sqlalchemy import Column, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.conf.invite import MemberStatus
from app.models.base_model import BaseModel


class CompanyMember(BaseModel):
    __tablename__ = "company_members"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(Enum(MemberStatus), nullable=False)
