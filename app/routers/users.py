import uuid

from fastapi import APIRouter, Depends
from app.db.connection import get_session

from app.schemas.users import (
    UserSchema,
    SignUpRequest,
    UserUpdateRequest,
    UsersListResponse,
    UserUpdateRequest,
)

from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UsersListResponse)
async def get_users(
    skip: int = 0, limit: int = 10, session=Depends(get_session)
) -> UsersListResponse:
    user_service = UserService(session=session)
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: uuid.UUID, session=Depends(get_session)) -> UserSchema:
    user_service = UserService(session=session)
    user = await user_service.get_user_by_id(user_id)
    return user


@router.post("/", response_model=UserSchema)
async def create_user(
    user_data: SignUpRequest, session=Depends(get_session)
) -> UserSchema:
    user_service = UserService(session=session)
    user = await user_service.create_user(user_data)
    return user


@router.put("/{user_id}", response_model=UserUpdateRequest)
async def update_user(
    user_id: uuid.UUID, user_data: UserUpdateRequest, session=Depends(get_session)
) -> UserUpdateRequest:
    user_service = UserService(session=session)
    user = await user_service.update_user(user_id, user_data)
    return user


@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(user_id: uuid.UUID, session=Depends(get_session)) -> UserSchema:
    user_service = UserService(session=session)
    user = await user_service.delete_by_id(user_id)
    return user
