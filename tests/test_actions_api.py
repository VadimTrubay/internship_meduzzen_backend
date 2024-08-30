import unittest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.action_service import ActionService
from app.schemas.actions import InviteCreateSchema, ActionSchema
from app.schemas.companies import CompanySchema
from app.schemas.users import UserSchema
from app.conf.invite import InvitationStatus, InvitationType
from app.exept.custom_exceptions import (
    CompanyNotFound,
    UserNotFound,
    YouCanNotInviteYourSelf,
)


class TestActionService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock()
        self.action_repository = AsyncMock()
        self.company_repository = AsyncMock()
        self.user_repository = AsyncMock()
        self.action_service = ActionService(
            session=self.session,
            action_repository=self.action_repository,
            company_repository=self.company_repository,
            user_repository=self.user_repository,
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
