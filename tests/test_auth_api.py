import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.exept.custom_exceptions import (
    UserWithEmailNotFound,
    EmailAlreadyExists,
    UnAuthorized,
)


class TestAuthService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock()
        self.repository = AsyncMock()
        self.auth_service = AuthService(
            session=self.session, repository=self.repository
        )

    @patch("app.utils.jwt_utils.encode_jwt", return_value="test_token")
    @patch("app.utils.password_utils.validate_password", return_value=True)
    async def test_login_success(self, mock_validate_password, mock_encode_jwt):
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        db_user = UserSchema(
            id=uuid4(),
            email="testuser@example.com",
            username="testuser",
            password="hashedpassword",
        )
        self.repository.get_one.return_value = db_user

        token = await self.auth_service.validate_auth_user(login_data)
        self.assertEqual(token.access_token, "test_token")
        self.assertEqual(token.token_type, "Bearer")

    async def test_login_user_not_found(self):
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword",
        }
        self.repository.get_one.return_value = None

        with self.assertRaises(UserWithEmailNotFound):
            await self.auth_service.validate_auth_user(login_data)

    @patch("app.utils.jwt_utils.encode_jwt", return_value="test_token")
    @patch("app.utils.password_utils.hash_password", return_value=b"hashedpassword")
    async def test_signup_success(self, mock_hash_password, mock_encode_jwt):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword",
        }
        self.repository.get_one.side_effect = [
            None,
            None,
        ]

        token = await self.auth_service.create_user(user_data)
        self.assertEqual(token.access_token, "test_token")
        self.assertEqual(token.token_type, "Bearer")

    async def test_signup_email_exists(self):
        user_data = {
            "email": "existinguser@example.com",
            "username": "newuser",
            "password": "newpassword",
        }
        existing_user = UserSchema(
            id=uuid4(),
            email="existinguser@example.com",
            username="existinguser",
            password="hashedpassword",
        )
        self.repository.get_one.return_value = existing_user

        with self.assertRaises(EmailAlreadyExists):
            await self.auth_service.create_user(user_data)

    @patch(
        "app.utils.jwt_utils.decode_jwt",
        return_value={
            "email": "testuser@example.com",
            "exp": (datetime.utcnow() - timedelta(minutes=5)).timestamp(),
        },
    )
    async def test_get_current_user_token_expired(self, mock_decode_jwt):
        token = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="expired_token"
        )

        with self.assertRaises(UnAuthorized):
            await self.auth_service.get_current_user(token=token, session=self.session)
