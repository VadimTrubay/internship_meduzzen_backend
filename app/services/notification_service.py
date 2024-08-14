import uuid
from typing import List

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.detail import Messages
from app.exept.custom_exceptions import NotFound, NotPermission
from app.repository.company_repository import CompanyRepository
from app.repository.notification_repository import NotificationRepository
from app.schemas.notifications import NotificationSchema


class NotificationService:
    def __init__(
        self,
        session: AsyncSession,
        notification_repository: NotificationRepository,
        company_repository: CompanyRepository,
    ):
        self.session = session
        self.notification_repository = notification_repository
        self.company_repository = company_repository

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
                company_member_id=field.company_member_id,
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

        member_id = notification.company_member_id
        member = await self.company_repository.get_company_member_by_id(member_id)

        if member.user_id != current_user_id:
            logger.info(Messages.NOT_PERMISSION)
            raise NotPermission()

        notification.is_read = True
        await self.notification_repository.update_one(
            notification.id, {"is_read": True}
        )
        return notification
