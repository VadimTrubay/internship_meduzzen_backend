import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
from app.services.user_service import UserService
from app.exept.custom_exceptions import UserNotFound, UserAlreadyExists, NotPermission


@pytest.fixture
def user_service():
    session = AsyncMock()
    repository = AsyncMock()
    return UserService(session=session, repository=repository)


@pytest.mark.asyncio
async def test_get_users_success(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    user_service.repository.get_many.return_value = [
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
    users = await user_service.get_users(skip=0, limit=10, current_user=current_user)
    assert len(users) == 2


@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    user_service.repository.get_one.return_value = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    user = await user_service.get_user_by_id(user_id, current_user)
    assert user.id == user_id


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    user_service.repository.get_one.return_value = None
    with pytest.raises(UserNotFound):
        await user_service.get_user_by_id(user_id, current_user)


@pytest.mark.asyncio
async def test_update_user_success(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    update_data = UserUpdateRequest(username="updateduser", password="updatedpassword")

    user_service.repository.get_one.side_effect = [current_user, None]
    user_service.repository.update_one.return_value = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="updateduser",
        password="updatedpassword",
    )

    updated_user = await user_service.update_user(user_id, update_data, current_user)
    assert updated_user.username == "updateduser"


@pytest.mark.asyncio
async def test_update_user_permission_denied(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=uuid4(),
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    update_data = UserUpdateRequest(username="updateduser", password="updatedpassword")

    with pytest.raises(NotPermission):
        await user_service.update_user(user_id, update_data, current_user)


@pytest.mark.asyncio
async def test_update_user_user_not_found(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    update_data = UserUpdateRequest(username="updateduser", password="updatedpassword")

    user_service.repository.get_one.return_value = None
    with pytest.raises(UserNotFound):
        await user_service.update_user(user_id, update_data, current_user)


@pytest.mark.asyncio
async def test_update_user_username_already_exists(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    update_data = UserUpdateRequest(username="updateduser", password="updatedpassword")

    user_service.repository.get_one.side_effect = [
        current_user,
        UserSchema(
            id=uuid4(),
            email="anotheruser@example.com",
            username="updateduser",
            password="testpassword",
        ),
    ]
    with pytest.raises(UserAlreadyExists):
        await user_service.update_user(user_id, update_data, current_user)


@pytest.mark.asyncio
async def test_delete_user_success(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )

    user_service.repository.get_one.return_value = current_user
    user_service.repository.delete_one.return_value = BaseUserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
    )

    deleted_user = await user_service.delete_user(user_id, current_user)
    assert deleted_user.id == user_id


@pytest.mark.asyncio
async def test_delete_user_permission_denied(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=uuid4(),
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )

    with pytest.raises(NotPermission):
        await user_service.delete_user(user_id, current_user)


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )

    user_service.repository.get_one.return_value = None
    with pytest.raises(UserNotFound):
        await user_service.delete_user(user_id, current_user)
