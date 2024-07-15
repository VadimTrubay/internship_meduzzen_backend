from datetime import datetime

from faker import Faker
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.connection import get_session
from app.repository.user_repository import UserRepository
from app.schemas.auth import TokenModel
from app.utils import jwt_utils
from app.utils import password_utils
from app.exept.custom_exceptions import (
    UserWithEmailNotFound,
    IncorrectPassword,
    EmailAlreadyExists,
    UserAlreadyExists,
    NotFound,
    UnAuthorized,
)

security = HTTPBearer()


class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def validate_auth_user(self, data: dict) -> TokenModel:
        email = data.get("email")
        password = data.get("password")
        db_user = await self.repository.get_one(email=email)

        if not db_user:
            raise UserWithEmailNotFound()

        if not password_utils.validate_password(
            password=password,
            hashed_password=db_user.password,
        ):
            raise IncorrectPassword()

        token = await jwt_utils.encode_jwt(payload={"email": email, "from": "noauth0"})
        token_info = TokenModel(access_token=token, token_type="Bearer")
        return token_info

    async def create_user(self, data: dict) -> TokenModel:
        email = data.get("email")
        existing_user_email = await self.repository.get_one(email=email)
        if existing_user_email:
            raise EmailAlreadyExists()

        username = data.get("username")
        existing_user_username = await self.repository.get_one(username=username)
        if existing_user_username:
            raise UserAlreadyExists()

        password = data.get("password")
        hashed_password = password_utils.hash_password(password=password)

        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password.decode("utf-8"),
            "is_admin": data.get("is_admin", False),
        }

        await self.repository.create_one(user_data)
        token = await jwt_utils.encode_jwt(payload={"email": email})
        token_info = TokenModel(access_token=token, token_type="Bearer")
        return token_info

    @staticmethod
    async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_session),
    ) -> str:
        decoded_token = jwt_utils.decode_jwt(token.credentials)
        if not decoded_token:
            raise NotFound()

        current_time = datetime.utcnow()
        expiration_time = datetime.utcfromtimestamp(decoded_token["exp"])
        if current_time >= expiration_time:
            raise UnAuthorized()

        user_email = decoded_token.get("email")
        user_repository = UserRepository(session=session)
        current_user = await user_repository.get_one(email=user_email)

        if not current_user:
            fake = Faker()
            username = fake.user_name()
            password = str(datetime.now())
            hashed_password = password_utils.hash_password(password)

            user_data = {
                "username": username,
                "email": user_email,
                "password": hashed_password.decode("utf-8"),
                "is_admin": decoded_token.get("is_admin", False),
            }

            await user_repository.create_one(user_data)
            current_user = await user_repository.get_one(email=user_email)

        return current_user
