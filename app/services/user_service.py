import uuid

from loguru import logger

from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.user_model import User as UserModel
from app.schemas.users import (
    SignUpRequest,
    UsersListResponse,
    UserSchema,
    UserUpdateRequest,
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session):
        self.session = session

    async def get_all_users(self, skip: int, limit: int) -> UsersListResponse:
        logger.info("Get all users.")
        users = await self.session.execute(
            UserModel.__table__.select().offset(skip).limit(limit)
        )
        all_users = users.fetchall()

        users_list = []

        for user in all_users:
            users_list.append(
                UserSchema(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    is_admin=user.age,
                )
            )

        return UsersListResponse(users=users_list)

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.session.get(UserModel, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Get user by id ID: {user_id}.")

        return user

    async def create_user(self, user_data: SignUpRequest) -> UserSchema:
        password_hash = pwd_context.hash(user_data.hashed_password)
        user_data.hashed_password = password_hash
        user = UserModel(**user_data.model_dump())
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )
        logger.info("Creating a new user...")
        return user

    async def update_user(self, user_id: uuid.UUID, user_data) -> UserUpdateRequest:
        user = await self.session.get(UserModel, user_id)
        try:
            if user is None:
                logger.error(f"Error updating user: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Updating user with ID: {user_id}.")
            return user

        except IntegrityError as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

    async def delete_by_id(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.session.get(UserModel, user_id)
        if user is None:
            logger.error(f"Error deleting user: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        await self.session.delete(user)
        await self.session.commit()
        logger.info(f"Deleting user with ID: {user_id}.")
        return user
