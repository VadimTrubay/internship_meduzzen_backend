import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.user_repository import UserRepository
from app.schemas.actions import (
    ActionSchema,
    InviteCreateSchema,
    RequestCreateSchema,
    GetActionsResponseSchema,
)
from app.schemas.users import UserSchema
from app.services.action_service import ActionService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/actions", tags=["actions"])


async def get_action_service(
    session: AsyncSession = Depends(get_session),
) -> ActionService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)
    return ActionService(
        session=session,
        action_repository=action_repository,
        company_repository=company_repository,
        user_repository=user_repository,
    )


@router.post("/invite", response_model=ActionSchema)
async def create_invite(
    action_data: InviteCreateSchema,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.create_invite(
        action_data=action_data, current_user_id=current_user_id
    )


@router.delete("/invite", response_model=ActionSchema)
async def delete_invite(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.cancel_invite(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/invite/accept", response_model=ActionSchema)
async def accept_invite(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.accept_invite(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/invite/decline", response_model=ActionSchema)
async def decline_invite(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.decline_invite(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/request", response_model=ActionSchema)
async def create_request(
    action_data: RequestCreateSchema,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.create_request(
        action_data=action_data, current_user_id=current_user_id
    )


@router.delete("/request", response_model=ActionSchema)
async def delete_request(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.cancel_request(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/request/accept", response_model=ActionSchema)
async def accept_request(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.accept_request(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/request/decline", response_model=ActionSchema)
async def decline_request(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.decline_request(
        action_id=action_id, current_user_id=current_user_id
    )


@router.delete("/leave", response_model=ActionSchema)
async def leave_from_company(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.leave_from_company(
        action_id=action_id, current_user_id=current_user_id
    )


@router.delete("/kick", response_model=ActionSchema)
async def kick_from_company(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.kick_from_company(
        action_id=action_id, current_user_id=current_user_id
    )


@router.get("/company/invites", response_model=List[GetActionsResponseSchema])
async def get_company_invites(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    company_id: Optional[uuid.UUID] = Query(None),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_company_invites(current_user_id, company_id)


@router.get("/company/requests", response_model=List[GetActionsResponseSchema])
async def get_company_requests(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    company_id: Optional[uuid.UUID] = Query(None),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_company_requests(current_user_id, company_id)


@router.get("/my/requests", response_model=List[GetActionsResponseSchema])
async def get_my_requests(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    requests_response = await action_service.get_my_requests(current_user_id)
    return requests_response


@router.get("/my/invites", response_model=List[GetActionsResponseSchema])
async def get_my_invites(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_my_invites(current_user_id)


@router.get("/company/members", response_model=List[GetActionsResponseSchema])
async def get_company_members(
    current_user: UserSchema = Depends(AuthService.get_current_user),
    company_id: Optional[uuid.UUID] = Query(None),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_company_members(current_user_id, company_id)