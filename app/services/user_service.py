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

        if "password" in update_dict:
            update_dict["password"] = bcrypt.hashpw(
                update_dict["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

        updated_user = await self.repository.update_one(user_id, update_dict)
        logger.info(detail.SUCCESS_UPDATE_USER)
        return UserSchema.from_orm(updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> BaseUserSchema:
        await self._get_user_or_raise(user_id)
        logger.info(detail.SUCCESS_DELETE_USER)
        return await self.repository.delete_one(user_id)
