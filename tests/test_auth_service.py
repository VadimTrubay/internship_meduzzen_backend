import pytest
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


@pytest.fixture
def auth_service():
    session = AsyncMock()
    repository = AsyncMock()
    return AuthService(session=session, repository=repository)


@pytest.mark.asyncio
@patch("app.utils.jwt_utils.encode_jwt", return_value="test_token")
@patch("app.utils.password_utils.validate_password", return_value=True)
async def test_login_success(mock_validate_password, mock_encode_jwt, auth_service):
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
    auth_service.repository.get_one.return_value = db_user

    token = await auth_service.validate_auth_user(login_data)
    assert token.access_token == "test_token"
    assert token.token_type == "Bearer"


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "testpassword",
    }
    auth_service.repository.get_one.return_value = None

    with pytest.raises(UserWithEmailNotFound):
        await auth_service.validate_auth_user(login_data)


@pytest.mark.asyncio
@patch("app.utils.jwt_utils.encode_jwt", return_value="test_token")
@patch("app.utils.password_utils.hash_password", return_value=b"hashedpassword")
async def test_signup_success(mock_hash_password, mock_encode_jwt, auth_service):
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword",
    }
    auth_service.repository.get_one.side_effect = [None, None]

    token = await auth_service.create_user(user_data)
    assert token.access_token == "test_token"
    assert token.token_type == "Bearer"


@pytest.mark.asyncio
async def test_signup_email_exists(auth_service):
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
    auth_service.repository.get_one.return_value = existing_user

    with pytest.raises(EmailAlreadyExists):
        await auth_service.create_user(user_data)


@pytest.mark.asyncio
@patch(
    "app.utils.jwt_utils.decode_jwt",
    return_value={
        "email": "testuser@example.com",
        "exp": (datetime.utcnow() - timedelta(minutes=5)).timestamp(),
    },
)
async def test_get_current_user_token_expired(mock_decode_jwt, auth_service):
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired_token")

    with pytest.raises(UnAuthorized):
        await auth_service.get_current_user(token=token, session=auth_service.session)
