<<<<<<< Updated upstream
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.user_service import UserService
from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
from app.exept.custom_exceptions import (
    UserNotFound,
    NotPermission,
    UserAlreadyExists,
    IncorrectPassword,
)
from app.utils import password_utils


@pytest.mark.asyncio
class TestUserService:
    @pytest.fixture
    def user_service(self):
        session = MagicMock()
        repository = MagicMock()
        return UserService(session, repository)

    @pytest.fixture
    def current_user(self):
        return UserSchema(
            id=uuid4(),
            username="current_user",
            email="current_user@example.com",
            password="hashed_password",
        )

    @pytest.fixture
    def user(self):
        return UserSchema(
            id=uuid4(),
            username="test_user",
            email="current_user@example.com",
            password="hashed_password",
        )

    async def test_get_user_by_id_success(self, user_service, user):
        user_service.repository.get_one = AsyncMock(return_value=user)
        result = await user_service.get_user_by_id(user.id)
        assert result == user

    async def test_get_user_by_id_not_found(self, user_service):
        user_service.repository.get_one = AsyncMock(return_value=None)
        with pytest.raises(UserNotFound):
            await user_service.get_user_by_id(uuid4())

    async def test_update_user_success(self, user_service, current_user):
        update_data = UserUpdateRequest(username="new_username")
        user_service._get_user_or_raise = AsyncMock(return_value=current_user)
        user_service.repository.get_one = AsyncMock(return_value=None)
        user_service.repository.update_one = AsyncMock(return_value=current_user)

        result = await user_service.update_user(
            current_user.id, update_data, current_user
        )
        assert result == current_user

    async def test_update_user_user_already_exists(self, user_service, current_user):
        update_data = UserUpdateRequest(username="existing_user")
        user_service._get_user_or_raise = AsyncMock(return_value=current_user)
        user_service.repository.get_one = AsyncMock(
            return_value=UserSchema(
                id=uuid4(),
                username="existing_user",
                email="existing_user@example.com",
                password="hashed_password",
            )
        )

        with pytest.raises(UserAlreadyExists):
            await user_service.update_user(current_user.id, update_data, current_user)

    async def test_update_user_incorrect_password(self, user_service, current_user):
        update_data = UserUpdateRequest(
            password="wrong_password", new_password="new_password"
        )
        user_service._get_user_or_raise = AsyncMock(return_value=current_user)
        password_utils.validate_password = MagicMock(return_value=False)

        with pytest.raises(IncorrectPassword):
            await user_service.update_user(current_user.id, update_data, current_user)

    async def test_delete_user_success(self, user_service, current_user):
        user_service._get_user_or_raise = AsyncMock(return_value=current_user)
        user_service.repository.delete_one = AsyncMock(return_value=current_user)

        result = await user_service.delete_user(current_user.id, current_user)
        assert result == current_user
=======
import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
from app.services.user_service import UserService
from app.exept.custom_exceptions import (
    UserNotFound,
    UserAlreadyExists,
    NotFound,
    NotPermission,
)


class TestUserService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock()
        self.repository = AsyncMock()
        self.user_service = UserService(
            session=self.session, repository=self.repository
        )

    async def test_get_users_success(self):
        self.repository.get_many.return_value = [
            UserSchema(
                id=uuid4(),
                email="testuser1@example.com",
                username="testuser1",
                password="testpassword1",
            ),
            UserSchema(
                id=uuid4(),
                email="testuser2@example.com",
                username="testuser2",
                password="testpassword2",
            ),
        ]
        users = await self.user_service.get_users(skip=0, limit=10)
        self.assertEqual(len(users), 2)

    async def test_get_user_by_id_success(self):
        user_id = uuid4()
        self.repository.get_one.return_value = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )
        user = await self.user_service.get_user_by_id(user_id)
        self.assertEqual(user.id, user_id)

    async def test_get_user_by_id_not_found(self):
        user_id = uuid4()
        self.repository.get_one.return_value = None
        with self.assertRaises(UserNotFound):
            await self.user_service.get_user_by_id(user_id)

    async def test_update_user_success(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )
        update_data = UserUpdateRequest(
            username="updateduser", password="updatedpassword"
        )

        self.repository.get_one.side_effect = [current_user, None]
        self.repository.update_one.return_value = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="updateduser",
            password="updatedpassword",
        )

        updated_user = await self.user_service.update_user(
            user_id, update_data, current_user
        )
        self.assertEqual(updated_user.username, "updateduser")

    async def test_update_user_permission_denied(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=uuid4(),
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )
        update_data = UserUpdateRequest(
            username="updateduser", password="updatedpassword"
        )

        with self.assertRaises(NotPermission):
            await self.user_service.update_user(user_id, update_data, current_user)

    async def test_update_user_user_not_found(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )
        update_data = UserUpdateRequest(
            username="updateduser", password="updatedpassword"
        )

        self.repository.get_one.side_effect = [None]
        with self.assertRaises(UserNotFound):
            await self.user_service.update_user(user_id, update_data, current_user)

    async def test_update_user_username_already_exists(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )
        update_data = UserUpdateRequest(
            username="updateduser", password="updatedpassword"
        )

        self.repository.get_one.side_effect = [
            current_user,
            UserSchema(
                id=uuid4(),
                email="anotheruser@example.com",
                username="updateduser",
                password="testpassword",
            ),
        ]
        with self.assertRaises(UserAlreadyExists):
            await self.user_service.update_user(user_id, update_data, current_user)

    async def test_delete_user_success(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )

        self.repository.get_one.return_value = current_user
        self.repository.delete_one.return_value = BaseUserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
        )

        deleted_user = await self.user_service.delete_user(user_id, current_user)
        self.assertEqual(deleted_user.id, user_id)

    async def test_delete_user_permission_denied(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=uuid4(),
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )

        with self.assertRaises(NotPermission):
            await self.user_service.delete_user(user_id, current_user)

    async def test_delete_user_not_found(self):
        user_id = uuid4()
        current_user = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
        )

        self.repository.get_one.return_value = None
        with self.assertRaises(UserNotFound):
            await self.user_service.delete_user(user_id, current_user)
>>>>>>> Stashed changes
