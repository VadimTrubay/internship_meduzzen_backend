import uuid
from typing import List, Optional

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

    # CHECK USER PERMISSION
    @staticmethod
    async def check_user_permission(user_id: uuid.UUID, current_user: UserSchema):
        if user_id != current_user.id:
            logger.info(Messages.NOT_PERMISSION)
            raise NotPermission()

    # GET TOTAL COUNT
    async def get_total_count(self):
        count = await self.repository.get_count()
        logger.info(Messages.SUCCESS_GET_TOTAL_COUNT)
        return count

    # GET USER BY OR RAISE
    async def _get_user_or_raise(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.repository.get_one(id=user_id)
        if not user:
            logger.info(Messages.NOT_FOUND)
            raise UserNotFound()
        logger.info(Messages.SUCCESS_GET_USER)

        return UserSchema.model_validate(user)

    # GET USERS
    async def get_users(self, skip, limit) -> List[UserSchema]:
        users = await self.repository.get_many(skip=skip, limit=limit)
        if not users:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()

        logger.info(Messages.SUCCESS_GET_USERS)

        return [UserSchema.model_validate(user) for user in users]

    # GET USER BY ID
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        return await self._get_user_or_raise(user_id)

    # UPDATE USER
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
                logger.info(Messages.INCORRECT_PASSWORD)
                raise IncorrectPassword()

            hashed_password = password_utils.hash_password(update_data.new_password)
            update_dict["password"] = hashed_password.decode("utf-8")

        if not update_dict:
            logger.info(Messages.NOT_FOUND)
            raise NotFound()

        updated_user = await self.repository.update_one(user_id, update_dict)
        logger.info(Messages.SUCCESS_UPDATE_USER)
        return UserSchema.model_validate(updated_user)

    # DELETE USER
    async def delete_user(
        self, user_id: uuid.UUID, current_user: UserSchema
    ) -> BaseUserSchema:
        await self.check_user_permission(user_id, current_user)
        await self._get_user_or_raise(user_id)
        logger.info(Messages.SUCCESS_DELETE_USER)
        return await self.repository.delete_one(user_id)
