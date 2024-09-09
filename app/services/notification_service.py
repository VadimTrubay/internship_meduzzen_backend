import uuid
from typing import List

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.detail import Messages
from app.exept.custom_exceptions import NotFound, NotPermission
from app.repository.company_repository import CompanyRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.user_repository import UserRepository
from app.schemas.notifications import NotificationSchema


class NotificationService:
    def __init__(
        self,
        session: AsyncSession,
        notification_repository: NotificationRepository,
        company_repository: CompanyRepository,
        user_repository: UserRepository,
    ):
        self.session = session
        self.notification_repository = notification_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    async def get_my_notifications(
        self, current_user_id: uuid.UUID
    ) -> List[NotificationSchema]:
        unread_notifications = (
            await self.notification_repository.get_unread_notifications_for_user(
                current_user_id
            )
        )

        notification_schemas = [
            NotificationSchema(
                id=field.id,
                text=field.text,
                is_read=field.is_read,
                user_id=field.user_id,
            )
            for field in unread_notifications
        ]

        return notification_schemas

    async def mark_as_read(
        self, current_user_id: uuid.UUID, notification_id: uuid.UUID
    ) -> NotificationSchema:
        notification = await self.notification_repository.get_one(id=notification_id)

        if not notification:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()

        user_id = notification.user_id
        user = await self.user_repository.get_one(id=user_id)
        if user.id != current_user_id:
            logger.info(Messages.NOT_PERMISSION)
            raise NotPermission()

        notification.is_read = True
        await self.notification_repository.update_one(
            notification.id, {"is_read": True}
        )
        return notification
