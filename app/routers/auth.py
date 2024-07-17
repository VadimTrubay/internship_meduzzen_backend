from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.repository.user_repository import UserRepository
from app.schemas.auth import TokenModel
from app.services.auth_service import AuthService
from app.schemas.users import (
    SignInRequest,
    SignUpRequest,
    UserSchema,
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    user_repository = UserRepository(session)
    return AuthService(session=session, repository=user_repository)


@router.post("/login", response_model=TokenModel)
async def login_jwt(
    login_data: SignInRequest, auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.validate_auth_user(login_data.model_dump())


@router.post("/signup", response_model=TokenModel)
async def create_user(
    user_create: SignUpRequest, user_service: AuthService = Depends(get_auth_service)
):
    return await user_service.create_user(user_create.model_dump())


@router.get("/me", response_model=UserSchema)
async def get_current_user_route(
    current_user: UserSchema = Depends(AuthService.get_current_user),
):
    return current_user