import unittest
from unittest.mock import AsyncMock, MagicMock
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
    NotOwner,
    UserNotInvited,
    ActionNotFound,
)


class TestActionService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock()
        self.action_repository = AsyncMock()
        self.company_repository = AsyncMock()
        self.user_repository = AsyncMock()
        self.notification_repository = AsyncMock()
        self.action_service = ActionService(
            session=self.session,
            action_repository=self.action_repository,
            company_repository=self.company_repository,
            user_repository=self.user_repository,
            notification_repository=self.notification_repository,
        )

    async def test_create_invite_success(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = uuid4()
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.user_repository.get_one.return_value = UserSchema(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password="hashedpassword",
        )
        self.company_repository.is_user_company_owner.return_value = True
        self.action_repository.get_one.return_value = None
        self.action_repository.create_one.return_value = ActionSchema(
            id=uuid4(),
            company_id=company_id,
            user_id=user_id,
            status=InvitationStatus.INVITED,
            type=InvitationType.INVITE,
        )

        result = await self.action_service.create_invite(action_data, current_user_id)

        self.action_repository.create_one.assert_called_once()
        self.notification_repository.create_notification_for_user.assert_called_once()
        self.assertEqual(result.status, InvitationStatus.INVITED)

    async def test_create_invite_user_not_found(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = uuid4()
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.user_repository.get_one.return_value = None

        with self.assertRaises(UserNotFound):
            await self.action_service.create_invite(action_data, current_user_id)

    async def test_create_invite_company_not_found(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = uuid4()
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.user_repository.get_one.return_value = UserSchema(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password="hashedpassword",
        )
        self.company_repository.get_one.return_value = None

        with self.assertRaises(CompanyNotFound):
            await self.action_service.create_invite(action_data, current_user_id)

    async def test_create_invite_self_invitation(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = user_id
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.user_repository.get_one.return_value = UserSchema(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password="hashedpassword",
        )
        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.company_repository.is_user_company_owner.return_value = True

        with self.assertRaises(YouCanNotInviteYourSelf):
            await self.action_service.create_invite(action_data, current_user_id)

    async def test_create_invite_user_already_invited(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = uuid4()
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.user_repository.get_one.return_value = UserSchema(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password="hashedpassword",
        )
        self.action_repository.get_one.return_value = ActionSchema(
            id=uuid4(),
            company_id=company_id,
            user_id=user_id,
            status=InvitationStatus.INVITED,
            type=InvitationType.INVITE,
        )

        with self.assertRaises(UserAlreadyInvited):
            await self.action_service.create_invite(action_data, current_user_id)

    async def test_create_invite_user_already_in_company(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = uuid4()
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.user_repository.get_one.return_value = UserSchema(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password="hashedpassword",
        )
        self.action_repository.get_one.return_value = ActionSchema(
            id=uuid4(),
            company_id=company_id,
            user_id=user_id,
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        with self.assertRaises(AlreadyInCompany):
            await self.action_service.create_invite(action_data, current_user_id)

    async def test_create_invite_action_already_available(self):
        company_id = uuid4()
        user_id = uuid4()
        current_user_id = uuid4()
        action_data = InviteCreateSchema(company_id=company_id, user_id=user_id)

        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.user_repository.get_one.return_value = UserSchema(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password="hashedpassword",
        )
        self.action_repository.get_one.return_value = ActionSchema(
            id=uuid4(),
            company_id=company_id,
            user_id=user_id,
            status=InvitationStatus.REQUESTED,
            type=InvitationType.INVITE,
        )

        with self.assertRaises(ActionAlreadyAvailable):
            await self.action_service.create_invite(action_data, current_user_id)

    async def test_cancel_invite_success(self):
        action_id = uuid4()
        current_user_id = uuid4()
        company_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=company_id,
            user_id=uuid4(),
            status=InvitationStatus.INVITED,
            type=InvitationType.INVITE,
        )
        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.company_repository.is_user_company_owner.return_value = True

        result = await self.action_service.cancel_invite(action_id, current_user_id)

        self.action_repository.delete_one.assert_called_once_with(action_id)
        self.assertEqual(result.id, action_id)

    async def test_accept_invite_success(self):
        action_id = uuid4()
        current_user_id = uuid4()
        company_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=company_id,
            user_id=current_user_id,
            status=InvitationStatus.INVITED,
            type=InvitationType.INVITE,
        )
        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            description="Test Description",
            visible=True,
        )

        result = await self.action_service.accept_invite(action_id, current_user_id)

        self.action_repository.update_one.assert_called_once()
        self.company_repository.create_company_member.assert_called_once()
        self.assertEqual(result.id, action_id)

    async def test_accept_invite_invalid_status(self):
        action_id = uuid4()
        current_user_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=uuid4(),
            user_id=current_user_id,
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        with self.assertRaises(UserNotInvited):
            await self.action_service.accept_invite(action_id, current_user_id)

    async def test_decline_invite_success(self):
        action_id = uuid4()
        current_user_id = uuid4()
        company_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=company_id,
            user_id=current_user_id,
            status=InvitationStatus.INVITED,
            type=InvitationType.INVITE,
        )

        result = await self.action_service.decline_invite(action_id, current_user_id)

        self.action_repository.update_one.assert_called_once_with(
            action_id, {"status": InvitationStatus.DECLINED_BY_USER}
        )
        self.assertEqual(result.id, action_id)

    async def test_decline_invite_invalid_status(self):
        action_id = uuid4()
        current_user_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=uuid4(),
            user_id=current_user_id,
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        with self.assertRaises(UserNotInvited):
            await self.action_service.decline_invite(action_id, current_user_id)

    async def test_create_request_already_in_company(self):
        company_id = uuid4()
        current_user_id = uuid4()

        self.company_repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="Test Company",
            owner_id=current_user_id,
            description="Test Description",
            visible=True,
        )
        self.company_repository.is_user_company_owner.return_value = True

        action_data = RequestCreateSchema(
            company_id=company_id, user_id=current_user_id
        )

        with self.assertRaises(AlreadyInCompany):
            await self.action_service.create_request(action_data, current_user_id)

    async def test_leave_from_company_success(self):
        action_id = uuid4()
        current_user_id = uuid4()
        company_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=company_id,
            user_id=current_user_id,
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        self.action_repository.delete_one.return_value = ActionSchema(
            id=action_id,
            user_id=current_user_id,
            company_id=company_id,
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        result = await self.action_service.leave_from_company(
            action_id, current_user_id
        )

        self.company_repository.delete_company_member.assert_called_once_with(
            company_id, current_user_id
        )
        self.action_repository.delete_one.assert_called_once_with(action_id)
        self.assertEqual(result.id, action_id)

    async def test_leave_from_company_not_allowed(self):
        action_id = uuid4()
        current_user_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=uuid4(),
            user_id=uuid4(),  # different user_id
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        with self.assertRaises(ActionAlreadyAvailable):
            await self.action_service.leave_from_company(action_id, current_user_id)

    async def test_kick_from_company_success(self):
        action_id = uuid4()
        current_user_id = uuid4()
        company_id = uuid4()

        self.action_repository.get_one.return_value = ActionSchema(
            id=action_id,
            company_id=company_id,
            user_id=uuid4(),
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        self.action_repository.delete_one.return_value = ActionSchema(
            id=action_id,
            company_id=company_id,
            user_id=uuid4(),
            status=InvitationStatus.ACCEPTED,
            type=InvitationType.INVITE,
        )

        result = await self.action_service.kick_from_company(action_id, current_user_id)

        self.company_repository.delete_company_member.assert_called_once_with(
            company_id, self.action_repository.get_one.return_value.user_id
        )
        self.action_repository.delete_one.assert_called_once_with(action_id)
        self.assertEqual(result.id, action_id)

    async def test_kick_from_company_action_not_found(self):
        action_id = uuid4()
        current_user_id = uuid4()

        self.action_repository.get_one.return_value = None

        with self.assertRaises(ActionNotFound):
            await self.action_service.kick_from_company(action_id, current_user_id)
