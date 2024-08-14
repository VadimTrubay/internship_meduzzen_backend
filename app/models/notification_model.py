from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class CompanyMemberNotification(BaseModel):
    __tablename__ = "user_notifications"

    text = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    company_member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("company_members.id", ondelete="CASCADE"),
        nullable=False,
    )

    company_member = relationship(
        "CompanyMember",
        back_populates="notifications",
    )
