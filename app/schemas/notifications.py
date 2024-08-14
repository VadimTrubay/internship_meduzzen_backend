import uuid

from pydantic import BaseModel


class NotificationSchema(BaseModel):
    id: uuid.UUID
    text: str
    is_read: bool
    company_member_id: uuid.UUID
