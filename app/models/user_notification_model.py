from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class UserNotification(BaseModel):
    __tablename__ = "user_notifications"

    text = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="notifications")
