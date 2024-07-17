import uuid
from typing import List, Optional, Tuple

import bcrypt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
from app.conf.detail import Messages
from app.exept.custom_exceptions import (
    UserNotFound,
    EmailAlreadyExists,
    UserAlreadyExists,
    NotFound,
    NotPermission,
    IncorrectPassword,
)
from app.utils import password_utils


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    @staticmethod
    async def check_user_permission(user_id: uuid.UUID, current_user: UserSchema):
        if user_id != current_user.id:
            logger.info(Messages.NOT_PERMISSION)
            raise NotPermission()

    async def get_total_count(self):
        count = await self.repository.get_count()
        logger.info(Messages.SUCCESS_GET_TOTAL_COUNT)
        return count

    async def _get_user_or_raise(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.repository.get_one(id=user_id)
        if not user:
            logger.info(Messages.NOT_FOUND)
            raise UserNotFound()
        logger.info(Messages.SUCCESS_GET_USER)

        return UserSchema.model_validate(user)

    async def create_user(self, data: dict) -> UserSchema:
        email = data.get("email")
        existing_user_email = await self.repository.get_one(email=email)
        if existing_user_email:
            logger.info(Messages.EMAIL_AlREADY_EXISTS)
            raise EmailAlreadyExists()

        username = data.get("username")
        existing_user_username = await self.repository.get_one(username=username)
        if existing_user_username:
            logger.info(Messages.USER_ALREADY_EXISTS)
            raise UserAlreadyExists()

        hashed_password = data.get("password")
        hashed_password = bcrypt.hashpw(
            hashed_password.encode("utf-8"), bcrypt.gensalt()
        )

        user_data = {
            "email": email,
            "username": username,
            "password": hashed_password.decode("utf-8"),
            "is_admin": data.get("is_admin", False),
        }

        user = await self.repository.create_one(user_data)
        logger.info(Messages.SUCCESS_CREATE_USER)

        return UserSchema.model_validate(user)

    async def get_users(self, skip, limit) -> List[UserSchema]:
        users = await self.repository.get_many(skip=skip, limit=limit)
        if not users:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()

        logger.info(Messages.SUCCESS_GET_USERS)

        return [UserSchema.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        return await self._get_user_or_raise(user_id)

    async def update_user(
        self,
        user_id: uuid.UUID,
        update_data: UserUpdateRequest,
        current_user: UserSchema,
    ) -> UserSchema:
        await self.check_user_permission(user_id, current_user)
        user = await self._get_user_or_raise(user_id)

        if not user:
            logger.info(Messages.NOT_FOUND)
            raise UserNotFound()

        update_dict = {}

        if update_data.username:
            existing_user = await self.repository.get_one(username=update_data.username)
            if existing_user and existing_user.id != user_id:
                logger.info(Messages.USER_ALREADY_EXISTS)
                raise UserAlreadyExists()
            update_dict["username"] = update_data.username

        if update_data.password and update_data.new_password:
            if not password_utils.validate_password(
                update_data.password, user.password
            ):
                logger.info(Messages.INVALID_PASSWORD)
                raise IncorrectPassword()

            hashed_password = password_utils.hash_password(update_data.new_password)
            update_dict["password"] = hashed_password.decode("utf-8")

        if not update_dict:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()

        updated_user = await self.repository.update_one(user_id, update_dict)
        logger.info(Messages.SUCCESS_UPDATE_USER)
        return UserSchema.model_validate(updated_user)

    async def delete_user(
        self, user_id: uuid.UUID, current_user: UserSchema
    ) -> BaseUserSchema:
        await self.check_user_permission(user_id, current_user)
        await self._get_user_or_raise(user_id)
        logger.info(Messages.SUCCESS_DELETE_USER)
        return await self.repository.delete_one(user_id)
