from loguru import logger
import uuid
from typing import List, Optional

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from app.repository.user_repository import UserRepository
from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema

from app.conf import detail


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def _get_user_or_raise(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.repository.get_one(id=user_id)
        if not user:
            logger.info(detail.NOT_FOUND)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail.NOT_FOUND,
            )
        logger.info(detail.SUCCESS_GET_USER)
        return UserSchema.from_orm(user)

    async def create_user(self, data: dict) -> UserSchema:
        email = data.get("email")
        existing_user_email = await self.repository.get_one(email=email)
        if existing_user_email:
            logger.info(detail.EMAIL_AlREADY_EXISTS)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail.EMAIL_AlREADY_EXISTS,
            )

        username = data.get("username")
        existing_user_username = await self.repository.get_one(username=username)
        if existing_user_username:
            logger.info(detail.USER_ALREADY_EXISTS)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail.USER_ALREADY_EXISTS,
            )

        hashed_password = data.get("hashed_password")
        hashed_password = bcrypt.hashpw(
            hashed_password.encode("utf-8"), bcrypt.gensalt()
        )

        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hashed_password.decode("utf-8"),
            "is_admin": data.get("is_admin", False),
        }

        user = await self.repository.create_one(user_data)
        logger.info(detail.EMAIL_AlREADY_EXISTS)
        return UserSchema.from_orm(user)

    async def get_users(self, skip: int = 1, limit: int = 10) -> List[UserSchema]:
        users = await self.repository.get_many(skip=skip, limit=limit)
        return users

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        return await self._get_user_or_raise(user_id)

    async def update_user(
        self, user_id: uuid.UUID, update_data: UserUpdateRequest
    ) -> UserSchema:
        await self._get_user_or_raise(user_id)
        update_dict = update_data.dict(exclude_unset=True)
        updated_user = await self.repository.update_one(user_id, update_dict)
        logger.info(detail.SUCCESS_UPDATE_USER)
        return UserSchema.from_orm(updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> BaseUserSchema:
        await self._get_user_or_raise(user_id)
        logger.info(detail.SUCCESS_DELETE_USER)
        return await self.repository.delete_one(user_id)
