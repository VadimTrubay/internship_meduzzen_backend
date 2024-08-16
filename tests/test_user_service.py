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
