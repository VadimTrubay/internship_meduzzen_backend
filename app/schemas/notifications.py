import uuid

from pydantic import BaseModel


class NotificationSchema(BaseModel):
    id: uuid.UUID
    text: str
    is_read: bool
    user_id: uuid.UUID
