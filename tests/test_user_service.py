import unittest
from unittest.mock import patch, AsyncMock
import uuid
from app.services.user_service import UserService
from app.schemas.users import SignUpRequest, UserUpdateRequest
from app.models.user_model import User as UserModel


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.session = AsyncMock()
        self.user_service = UserService(session=self.session)

    @patch("app.services.user_service.pwd_context.hash", return_value="hashedpassword")
    async def test_create_user(self, mock_hash):
        user_data = SignUpRequest(
            username="testuser",
            email="testuser@example.com",
            hashed_password="testpassword",
        )
        mock_user = UserModel(
            id=uuid.uuid4(),
            username="testuser",
            email="testuser@example.com",
            hashed_password="hashedpassword",
        )
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        self.session.get.return_value = mock_user

        user = await self.user_service.create_user(user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")

    async def test_get_all_users(self):
        mock_user_list = [
            UserModel(
                id=uuid.uuid4(),
                username="testuser",
                email="testuser@example.com",
                hashed_password="hashedpassword",
            )
        ]
        self.session.execute.return_value.fetchall.return_value = mock_user_list

        users = await self.user_service.get_all_users(skip=0, limit=10)
        self.assertEqual(len(users["users"]), 1)

    async def test_get_user_by_id(self):
        user_id = uuid.uuid4()
        mock_user = UserModel(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            hashed_password="hashedpassword",
        )
        self.session.get.return_value = mock_user

        user = await self.user_service.get_user_by_id(user_id)
        self.assertEqual(user.id, user_id)
        self.assertEqual(user.username, "testuser")

    async def test_update_user(self):
        user_id = uuid.uuid4()
        mock_user = UserModel(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            hashed_password="hashedpassword",
        )
        self.session.get.return_value = mock_user
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        update_data = UserUpdateRequest(username="updateduser")
        user = await self.user_service.update_user(user_id, update_data)
        self.assertEqual(user.username, "updateduser")

    async def test_delete_by_id(self):
        user_id = uuid.uuid4()
        mock_user = UserModel(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            hashed_password="hashedpassword",
        )
        self.session.get.return_value = mock_user
        self.session.delete.return_value = None
        self.session.commit.return_value = None

        user = await self.user_service.delete_by_id(user_id)
        self.assertEqual(user.id, user_id)
