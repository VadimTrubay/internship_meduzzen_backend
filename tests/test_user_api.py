import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
from app.services.user_service import UserService
from app.exept.custom_exceptions import (
    UserNotFound,
    EmailAlreadyExists,
    UserAlreadyExists,
    NotFound,
    NotPermission,
)
from app.conf.detail import Messages


class TestUserService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock()
        self.repository = AsyncMock()
        self.user_service = UserService(
            session=self.session, repository=self.repository
        )

    async def test_create_user_success(self):
        user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword",
        }
        self.repository.get_one.side_effect = [None, None]
        self.repository.create_one.return_value = UserSchema(
            id=uuid4(),
            email="testuser@example.com",
            username="testuser",
            password="hashedpassword",
            is_admin=False,
        )

        user = await self.user_service.create_user(user_data)
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.username, user_data["username"])

    async def test_get_users_success(self):
        self.repository.get_many.return_value = [
            UserSchema(
                id=uuid4(),
                email="testuser1@example.com",
                username="testuser1",
                password="testpassword1",
                is_admin=False,
            ),
            UserSchema(
                id=uuid4(),
                email="testuser2@example.com",
                username="testuser2",
                password="testpassword2",
                is_admin=False,
            ),
        ]
        users = await self.user_service.get_users(skip=0, limit=10)
        self.assertEqual(len(users), 2)

    async def test_get_users_not_found(self):
        self.repository.get_many.return_value = []
        with self.assertRaises(NotFound):
            await self.user_service.get_users(skip=0, limit=10)

    async def test_get_user_by_id_success(self):
        user_id = uuid4()
        self.repository.get_one.return_value = UserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
            is_admin=False,
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
            is_admin=False,
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
            is_admin=False,
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
            is_admin=False,
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
            is_admin=False,
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
            is_admin=False,
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
                is_admin=False,
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
            is_admin=False,
        )

        self.repository.get_one.return_value = current_user
        self.repository.delete_one.return_value = BaseUserSchema(
            id=user_id,
            email="testuser@example.com",
            username="testuser",
            is_admin=False,
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
            is_admin=False,
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
            is_admin=False,
        )

        self.repository.get_one.return_value = None
        with self.assertRaises(UserNotFound):
            await self.user_service.delete_user(user_id, current_user)
