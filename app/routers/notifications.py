import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.schemas.notifications import NotificationSchema
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.notification_service import NotificationService
from app.utils.call_services import get_notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=List[NotificationSchema])
async def get_my_notifications(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> List[NotificationSchema]:
    current_user_id = current_user.id

    return await notification_service.get_my_notifications(current_user_id)


@router.patch("/{notification_id}/mark_as_read", response_model=NotificationSchema)
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationSchema:
    current_user_id = current_user.id

    return await notification_service.mark_as_read(current_user_id, notification_id)
