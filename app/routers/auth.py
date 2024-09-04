from fastapi import APIRouter, Depends

from app.schemas.auth import TokenModel
from app.services.auth_service import AuthService
from app.schemas.users import (
    SignInRequest,
    SignUpRequest,
    UserSchema, BaseUserSchema,
)
from app.utils.call_services import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenModel)
async def login_jwt(
    login_data: SignInRequest, auth_service: AuthService = Depends(get_auth_service)
) -> TokenModel:

    return await auth_service.validate_auth_user(login_data.model_dump())


@router.post("/signup", response_model=TokenModel)
async def create_user(
    user_create: SignUpRequest, user_service: AuthService = Depends(get_auth_service)
) -> TokenModel:

    return await user_service.create_user(user_create.model_dump())


@router.get("/me", response_model=BaseUserSchema)
async def get_current_user_route(
    current_user: BaseUserSchema = Depends(AuthService.get_current_user),
) -> BaseUserSchema:

    return current_user
