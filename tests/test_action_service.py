import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.services.action_service import ActionService
from app.schemas.actions import InviteCreateSchema, ActionSchema, RequestCreateSchema
from app.schemas.companies import CompanySchema
from app.schemas.users import UserSchema
from app.conf.invite import InvitationStatus, InvitationType
from app.exept.custom_exceptions import (
    CompanyNotFound,
    UserNotFound,
    YouCanNotInviteYourSelf,
    AlreadyInCompany,
    UserAlreadyInvited,
    ActionAlreadyAvailable,
    UserNotInvited,
    ActionNotFound,
)


@pytest.fixture
def action_service():
    session = AsyncMock()
    action_repository = AsyncMock()
    company_repository = AsyncMock()
    user_repository = AsyncMock()
    notification_repository = AsyncMock()
    return ActionService(
        session=session,
        action_repository=action_repository,
        company_repository=company_repository,
        user_repository=user_repository,
        notification_repository=notification_repository,
    )


@pytest.mark.asyncio
async def test_create_invite_success(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = uuid4()
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=current_user_id,
        description="Test Description",
        visible=True,
    )
    action_service.user_repository.get_one.return_value = UserSchema(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword",
    )
    action_service.company_repository.is_user_company_owner.return_value = True
    action_service.action_repository.get_one.return_value = None
    action_service.action_repository.create_one.return_value = ActionSchema(
        id=uuid4(),
        company_id=company_id,
        user_id=user_id,
        status=InvitationStatus.INVITED,
        type=InvitationType.INVITE,
    )

    result = await action_service.create_invite(action_data, current_user_id)

    action_service.action_repository.create_one.assert_called_once()
    action_service.notification_repository.create_notification_for_user.assert_called_once()
    assert result.status == InvitationStatus.INVITED


@pytest.mark.asyncio
async def test_create_invite_user_not_found(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = uuid4()
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.user_repository.get_one.return_value = None

    with pytest.raises(UserNotFound):
        await action_service.create_invite(action_data, current_user_id)


@pytest.mark.asyncio
async def test_create_invite_company_not_found(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = uuid4()
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.user_repository.get_one.return_value = UserSchema(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword",
    )
    action_service.company_repository.get_one.return_value = None

    with pytest.raises(CompanyNotFound):
        await action_service.create_invite(action_data, current_user_id)


@pytest.mark.asyncio
async def test_create_invite_self_invitation(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = user_id
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.user_repository.get_one.return_value = UserSchema(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword",
    )
    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=current_user_id,
        description="Test Description",
        visible=True,
    )
    action_service.company_repository.is_user_company_owner.return_value = True

    with pytest.raises(YouCanNotInviteYourSelf):
        await action_service.create_invite(action_data, current_user_id)


@pytest.mark.asyncio
async def test_create_invite_user_already_invited(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = uuid4()
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=current_user_id,
        description="Test Description",
        visible=True,
    )
    action_service.user_repository.get_one.return_value = UserSchema(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword",
    )
    action_service.action_repository.get_one.return_value = ActionSchema(
        id=uuid4(),
        company_id=company_id,
        user_id=user_id,
        status=InvitationStatus.INVITED,
        type=InvitationType.INVITE,
    )

    with pytest.raises(UserAlreadyInvited):
        await action_service.create_invite(action_data, current_user_id)


@pytest.mark.asyncio
async def test_create_invite_user_already_in_company(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = uuid4()
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=current_user_id,
        description="Test Description",
        visible=True,
    )
    action_service.user_repository.get_one.return_value = UserSchema(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword",
    )
    action_service.action_repository.get_one.return_value = ActionSchema(
        id=uuid4(),
        company_id=company_id,
        user_id=user_id,
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    with pytest.raises(AlreadyInCompany):
        await action_service.create_invite(action_data, current_user_id)


@pytest.mark.asyncio
async def test_create_invite_action_already_available(action_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user_id = uuid4()
    action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=current_user_id,
        description="Test Description",
        visible=True,
    )
    action_service.user_repository.get_one.return_value = UserSchema(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword",
    )
    action_service.action_repository.get_one.return_value = ActionSchema(
        id=uuid4(),
        company_id=company_id,
        user_id=user_id,
        status=InvitationStatus.REQUESTED,
        type=InvitationType.INVITE,
    )

    with pytest.raises(ActionAlreadyAvailable):
        await action_service.create_invite(action_data, current_user_id)


@pytest.mark.asyncio
async def test_accept_invite_success(action_service):
    action_id = uuid4()
    current_user_id = uuid4()
    company_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=company_id,
        user_id=current_user_id,
        status=InvitationStatus.INVITED,
        type=InvitationType.INVITE,
    )
    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=uuid4(),
        description="Test Description",
        visible=True,
    )

    result = await action_service.accept_invite(action_id, current_user_id)

    action_service.action_repository.update_one.assert_called_once()
    action_service.company_repository.create_company_member.assert_called_once()
    assert result.id == action_id


@pytest.mark.asyncio
async def test_accept_invite_invalid_status(action_service):
    action_id = uuid4()
    current_user_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=uuid4(),
        user_id=current_user_id,
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    with pytest.raises(UserNotInvited):
        await action_service.accept_invite(action_id, current_user_id)


@pytest.mark.asyncio
async def test_decline_invite_success(action_service):
    action_id = uuid4()
    current_user_id = uuid4()
    company_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=company_id,
        user_id=current_user_id,
        status=InvitationStatus.INVITED,
        type=InvitationType.INVITE,
    )

    result = await action_service.decline_invite(action_id, current_user_id)

    action_service.action_repository.update_one.assert_called_once_with(
        action_id, {"status": InvitationStatus.DECLINED_BY_USER}
    )
    assert result.id == action_id


@pytest.mark.asyncio
async def test_decline_invite_invalid_status(action_service):
    action_id = uuid4()
    current_user_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=uuid4(),
        user_id=current_user_id,
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    with pytest.raises(UserNotInvited):
        await action_service.decline_invite(action_id, current_user_id)


@pytest.mark.asyncio
async def test_create_request_already_in_company(action_service):
    company_id = uuid4()
    current_user_id = uuid4()

    action_service.company_repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="Test Company",
        owner_id=current_user_id,
        description="Test Description",
        visible=True,
    )
    action_service.company_repository.is_user_company_owner.return_value = True

    action_data = RequestCreateSchema(company_id=company_id, user_id=current_user_id)

    with pytest.raises(AlreadyInCompany):
        await action_service.create_request(action_data, current_user_id)


@pytest.mark.asyncio
async def test_leave_from_company_success(action_service):
    action_id = uuid4()
    current_user_id = uuid4()
    company_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=company_id,
        user_id=current_user_id,
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    action_service.action_repository.delete_one.return_value = ActionSchema(
        id=action_id,
        user_id=current_user_id,
        company_id=company_id,
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    result = await action_service.leave_from_company(action_id, current_user_id)

    action_service.company_repository.delete_company_member.assert_called_once_with(
        company_id, current_user_id
    )
    action_service.action_repository.delete_one.assert_called_once_with(action_id)
    assert result.id == action_id


@pytest.mark.asyncio
async def test_leave_from_company_not_allowed(action_service):
    action_id = uuid4()
    current_user_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=uuid4(),
        user_id=uuid4(),
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    with pytest.raises(ActionAlreadyAvailable):
        await action_service.leave_from_company(action_id, current_user_id)


@pytest.mark.asyncio
async def test_kick_from_company_success(action_service):
    action_id = uuid4()
    current_user_id = uuid4()
    company_id = uuid4()

    action_service.action_repository.get_one.return_value = ActionSchema(
        id=action_id,
        company_id=company_id,
        user_id=uuid4(),
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    action_service.action_repository.delete_one.return_value = ActionSchema(
        id=action_id,
        company_id=company_id,
        user_id=uuid4(),
        status=InvitationStatus.ACCEPTED,
        type=InvitationType.INVITE,
    )

    result = await action_service.kick_from_company(action_id, current_user_id)

    action_service.company_repository.delete_company_member.assert_called_once_with(
        company_id, action_service.action_repository.get_one.return_value.user_id
    )
    action_service.action_repository.delete_one.assert_called_once_with(action_id)
    assert result.id == action_id


@pytest.mark.asyncio
async def test_kick_from_company_action_not_found(action_service):
    action_id = uuid4()
    current_user_id = uuid4()

    action_service.action_repository.get_one.return_value = None

    with pytest.raises(ActionNotFound):
        await action_service.kick_from_company(action_id, current_user_id)
