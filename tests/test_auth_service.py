import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.repository.user_repository import UserRepository
from app.schemas.auth import TokenModel
from app.exept.custom_exceptions import (
    UserWithEmailNotFound,
    IncorrectPassword,
    EmailAlreadyExists,
    UserAlreadyExists,
    NotFound,
    UnAuthorized,
)


class TestAuthService:
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        self.session_mock = AsyncMock()
        self.user_repository_mock = AsyncMock(
            spec=UserRepository, session=self.session_mock
        )
        self.auth_service = AuthService(
            session=self.session_mock, repository=self.user_repository_mock
        )

        self.valid_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }

        self.valid_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "password": "hashedpassword123",
        }

    @pytest.mark.asyncio
    # async def test_validate_auth_user_success(self, monkeypatch):
    #     self.user_repository_mock.get_one = AsyncMock(return_value=self.valid_user)
    #     monkeypatch.setattr(
    #         "app.utils.password_utils.validate_password",
    #         lambda password, hashed_password: True,
    #     )
    #     monkeypatch.setattr("app.utils.jwt_utils.encode_jwt", lambda payload: "token")
    #
    #     token_info = await self.auth_service.validate_auth_user(self.valid_user_data)
    #     assert isinstance(token_info, TokenModel)
    #     assert token_info.access_token == "token"
    #     assert token_info.token_type == "Bearer"

    @pytest.mark.asyncio
    async def test_validate_auth_user_user_not_found(self):
        self.user_repository_mock.get_one = AsyncMock(return_value=None)
        with pytest.raises(UserWithEmailNotFound):
            await self.auth_service.validate_auth_user(self.valid_user_data)

    # @pytest.mark.asyncio
    # async def test_validate_auth_user_incorrect_password(self):
    #     self.user_repository_mock.get_one = AsyncMock(return_value=self.valid_user)
    #     with patch("app.utils.password_utils.validate_password", return_value=False):
    #         with pytest.raises(IncorrectPassword):
    #             await self.auth_service.validate_auth_user(self.valid_user_data)

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        self.user_repository_mock.get_one = AsyncMock(return_value=None)
        self.user_repository_mock.create_one = AsyncMock()
        with patch(
            "app.utils.password_utils.hash_password", return_value=b"hashedpassword123"
        ):
            with patch("app.utils.jwt_utils.encode_jwt", return_value="token"):
                token_info = await self.auth_service.create_user(self.valid_user_data)
                assert isinstance(token_info, TokenModel)
                assert token_info.access_token == "token"
                assert token_info.token_type == "Bearer"

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        self.user_repository_mock.get_one = AsyncMock(
            side_effect=[self.valid_user, None]
        )
        with pytest.raises(EmailAlreadyExists):
            await self.auth_service.create_user(self.valid_user_data)

    @pytest.mark.asyncio
    async def test_create_user_username_exists(self):
        self.user_repository_mock.get_one = AsyncMock(
            side_effect=[None, self.valid_user]
        )
        with pytest.raises(UserAlreadyExists):
            await self.auth_service.create_user(self.valid_user_data)

    # @pytest.mark.asyncio
    # async def test_get_current_user_success(self):
    #     token = "valid_token"
    #     decoded_token = {
    #         "email": self.valid_user["email"],
    #         "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
    #     }
    #     with patch("app.utils.jwt_utils.decode_jwt", return_value=decoded_token):
    #         self.user_repository_mock.get_one = AsyncMock(return_value=self.valid_user)
    #         current_user = await self.auth_service.get_current_user(
    #             token=MagicMock(credentials=token)
    #         )
    #         assert current_user == self.valid_user

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self):
        token = "expired_token"
        decoded_token = {
            "email": "test@example.com",
            "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
        }
        with patch("app.utils.jwt_utils.decode_jwt", return_value=decoded_token):
            with pytest.raises(UnAuthorized):
                await self.auth_service.get_current_user(
                    token=MagicMock(credentials=token)
                )

    # @pytest.mark.asyncio
    # async def test_get_current_user_not_found(self):
    #     token = "valid_token"
    #     decoded_token = {
    #         "email": "test@example.com",
    #         "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
    #     }
    #     with patch("app.utils.jwt_utils.decode_jwt", return_value=decoded_token):
    #         self.user_repository_mock.get_one = AsyncMock(return_value=None)
    #         with pytest.raises(NotFound):
    #             await self.auth_service.get_current_user(
    #                 token=MagicMock(credentials=token)
    #             )
