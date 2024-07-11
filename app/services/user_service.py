from loguru import logger
import uuid
from typing import List, Optional

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
from app.conf.detail import Messages
from app.exept.custom_exceptions import UserNotFound, NotFound


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def _get_user_or_raise(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.repository.get_one(id=user_id)
        if not user:
            logger.info(Messages.NOT_FOUND)
            raise UserNotFound()
        logger.info(Messages.SUCCESS_GET_USER)
        return UserSchema.from_orm(user)

    async def get_users(self, skip: int = 1, limit: int = 10) -> List[UserSchema]:
        users = await self.repository.get_many(skip=skip, limit=limit)
        if not users:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()
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
        logger.info(Messages.SUCCESS_UPDATE_USER)
        return UserSchema.from_orm(updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> BaseUserSchema:
        await self._get_user_or_raise(user_id)
        logger.info(Messages.SUCCESS_DELETE_USER)
        return await self.repository.delete_one(user_id)