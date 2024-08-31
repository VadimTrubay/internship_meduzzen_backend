import uuid

from fastapi import APIRouter, Depends
from loguru import logger

from app.conf.detail import Messages
from app.exept.custom_exceptions import NotPermission
from app.schemas.users import (
    UserSchema,
    UsersListResponse,
    UserUpdateRequest,
    BaseUserSchema,
)
from app.services.auth_service import AuthService
from app.utils.call_services import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


async def verify_user_permission(
    user_id: uuid.UUID, current_user: UserSchema = Depends(AuthService.get_current_user)
):
    if user_id != current_user.id:
        logger.info(Messages.NOT_PERMISSION)
        raise NotPermission()


@router.get("/", response_model=UsersListResponse)
async def get_all_users(
    skip: int = 1,
    limit: int = 10,
    user_service=Depends(get_user_service),
    current_user: UserSchema = Depends(AuthService.get_current_user),
):
    current_user_id = current_user.id
    users = await user_service.get_users(skip, limit)
    total_count = await user_service.get_total_count()
    result = [UserSchema.from_orm(user) for user in users]

    return UsersListResponse(users=result, total_count=total_count)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: uuid.UUID,
    user_service=Depends(get_user_service),
    current_user: UserSchema = Depends(AuthService.get_current_user),
):
    current_user_id = current_user.id
    user = await user_service.get_user_by_id(user_id)

    return user


@router.patch(
    "/{user_id}",
    response_model=UserSchema,
    dependencies=[Depends(verify_user_permission)],
)
async def update_user(
    user_id: uuid.UUID,
    update_data: UserUpdateRequest,
    user_service=Depends(get_user_service),
    current_user: UserSchema = Depends(AuthService.get_current_user),
):
    updated_user = await user_service.update_user(user_id, update_data, current_user)

    return updated_user


@router.delete(
    "/{user_id}",
    response_model=BaseUserSchema,
    dependencies=[Depends(verify_user_permission)],
)
async def delete_user(
    user_id: uuid.UUID,
    user_service=Depends(get_user_service),
    current_user: UserSchema = Depends(AuthService.get_current_user),
):
    deleted_user = await user_service.delete_user(user_id, current_user)

    return deleted_user
