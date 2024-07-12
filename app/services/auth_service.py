# app/services/auth_service.py

from datetime import datetime
from typing import Dict, Any

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from app.db.connection import get_session
from app.models.user_model import User as UserModel
from app.conf import detail
from app.repository.user_repository import UserRepository
from app.schemas.auth import TokenModel
from app.utils import jwt_utils
from app.utils import password_utils
from app.exept.custom_exceptions import (
    UserWithEmailNotFound,
    IncorrectPassword,
    EmailAlreadyExists,
    UserAlreadyExists,
)

security = HTTPBearer()


class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def validate_auth_user(self, data: dict) -> dict[str, TokenModel | Any]:
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
        # data = {
        #     "username": db_user.username,
        #     "email": db_user.email,
        #     "access_token": token_info,
        # }
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
            "email": email,
            "username": username,
            "password": hashed_password.decode("utf-8"),
            "is_admin": data.get("is_admin", False),
        }

        new_user = await self.repository.create_one(user_data)

        token = await jwt_utils.encode_jwt(payload={"email": email})
        token_info = TokenModel(access_token=token, token_type="Bearer")

        return token_info

    async def create_user_from_auth0(self, token: str) -> TokenModel:
        # Decode the Auth0 token
        decoded_token = jwt_utils.decode_jwt(token)

        # Extract user information from the token
        email = decoded_token.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in token",
            )

        # Check if the user already exists
        existing_user = await self.repository.get_one(email=email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

        # Create the new user
        user_data = {
            "email": email,
            "username": email.split("@")[0],  # Use part of the email as username
            "password": password_utils.hash_password(password="defaultpassword").decode(
                "utf-8"
            ),
            "is_admin": False,
        }
        new_user = await self.repository.create_one(user_data)

        # Generate a new token for the user
        token = await jwt_utils.encode_jwt(payload={"email": email})
        token_info = TokenModel(access_token=token, token_type="Bearer")

        return token_info

    @staticmethod
    async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_session),
    ) -> UserModel:
        decoded_token = jwt_utils.decode_jwt(token.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=detail.INVALID_TOKEN
            )

        current_time = datetime.utcnow()
        expiration_time = datetime.utcfromtimestamp(decoded_token["exp"])
        if current_time >= expiration_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail.TOKEN_HAS_EXPIRED,
            )

        user_email = decoded_token.get("email")
        user_repository = UserRepository(session=session)
        current_user = await user_repository.get_one(email=user_email)

        if not current_user:
            # Decode Auth0 token again to get email and create new user
            new_user_data = {
                "email": user_email,
                "username": user_email.split("@")[
                    0
                ],  # Use part of the email as username
                "password": password_utils.hash_password(
                    password="defaultpassword"
                ).decode("utf-8"),
                "is_admin": False,
            }
            await user_repository.create_one(new_user_data)
            current_user = await user_repository.get_one(email=user_email)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user from Auth0 token",
            )

        return UserModel(
            id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            is_admin=current_user.is_admin,
        )
