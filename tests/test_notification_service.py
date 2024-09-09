import uuid
import pytest
from unittest.mock import AsyncMock

from app.services.notification_service import NotificationService
from app.exept.custom_exceptions import NotFound, NotPermission
from app.schemas.notifications import NotificationSchema


@pytest.mark.asyncio
async def test_get_my_notifications_success():
    mock_session = AsyncMock()
    mock_notification_repo = AsyncMock()
    mock_company_repo = AsyncMock()
    mock_user_repo = AsyncMock()

    service = NotificationService(
        session=mock_session,
        notification_repository=mock_notification_repo,
        company_repository=mock_company_repo,
        user_repository=mock_user_repo,
    )

    user_id = uuid.uuid4()
    notifications = [
        NotificationSchema(
            id=uuid.uuid4(),
            text="You have a new message",
            is_read=False,
            user_id=user_id,
        ),
        NotificationSchema(
            id=uuid.uuid4(),
            text="Your profile was viewed",
            is_read=False,
            user_id=user_id,
        ),
    ]

    mock_notification_repo.get_unread_notifications_for_user.return_value = (
        notifications
    )

    result = await service.get_my_notifications(user_id)

    assert len(result) == 2
    for notification in result:
        assert not notification.is_read
        assert notification.user_id == user_id


@pytest.mark.asyncio
async def test_mark_as_read_success():
    mock_session = AsyncMock()
    mock_notification_repo = AsyncMock()
    mock_company_repo = AsyncMock()
    mock_user_repo = AsyncMock()

    service = NotificationService(
        session=mock_session,
        notification_repository=mock_notification_repo,
        company_repository=mock_company_repo,
        user_repository=mock_user_repo,
    )

    user_id = uuid.uuid4()
    notification_id = uuid.uuid4()

    notification = NotificationSchema(
        id=notification_id,
        text="You have a new message",
        is_read=False,
        user_id=user_id,
    )

    mock_notification_repo.get_one.return_value = notification

    mock_user = AsyncMock()
    mock_user.id = user_id
    mock_user_repo.get_one.return_value = mock_user

    result = await service.mark_as_read(
        current_user_id=user_id, notification_id=notification_id
    )

    assert result.is_read
    assert result.id == notification_id
    mock_notification_repo.update_one.assert_called_once_with(
        notification_id, {"is_read": True}
    )


@pytest.mark.asyncio
async def test_mark_as_read_not_found():
    # Arrange
    mock_session = AsyncMock()
    mock_notification_repo = AsyncMock()
    mock_company_repo = AsyncMock()
    mock_user_repo = AsyncMock()

    service = NotificationService(
        session=mock_session,
        notification_repository=mock_notification_repo,
        company_repository=mock_company_repo,
        user_repository=mock_user_repo,
    )

    notification_id = uuid.uuid4()
    current_user_id = uuid.uuid4()

    mock_notification_repo.get_one.return_value = None

    with pytest.raises(NotFound):
        await service.mark_as_read(
            current_user_id=current_user_id, notification_id=notification_id
        )
