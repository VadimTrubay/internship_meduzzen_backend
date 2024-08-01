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
    CompanyMemberSchema,
    GetAdminsResponseSchema,
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


@router.post("/company/{company_id}/invite/user/{user_id}", response_model=ActionSchema)
async def create_invite(
    company_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    action_data = InviteCreateSchema(
        company_id=company_id,
        user_id=user_id,
    )
    return await action_service.create_invite(
        action_data=action_data, current_user_id=current_user_id
    )


@router.delete("/{action_id}/invite", response_model=ActionSchema)
async def delete_invite(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.cancel_invite(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/{action_id}/invite/accept", response_model=ActionSchema)
async def accept_invite(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.accept_invite(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/{action_id}/invite/decline", response_model=ActionSchema)
async def decline_invite(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.decline_invite(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post(
    "/company/{company_id}/request/user/{user_id}", response_model=ActionSchema
)
async def create_request(
    company_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    action_data = RequestCreateSchema(
        company_id=company_id,
        user_id=user_id,
    )
    return await action_service.create_request(
        action_data=action_data, current_user_id=current_user_id
    )


@router.delete("/{action_id}/request", response_model=ActionSchema)
async def delete_request(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.cancel_request(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/{action_id}/request/accept", response_model=ActionSchema)
async def accept_request(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.accept_request(
        action_id=action_id, current_user_id=current_user_id
    )


@router.post("/{action_id}/request/decline", response_model=ActionSchema)
async def decline_request(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.decline_request(
        action_id=action_id, current_user_id=current_user_id
    )


@router.delete("/{action_id}/leave", response_model=ActionSchema)
async def leave_from_company(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.leave_from_company(
        action_id=action_id, current_user_id=current_user_id
    )


@router.delete("/{action_id}/kick", response_model=ActionSchema)
async def kick_from_company(
    action_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> ActionSchema:
    current_user_id = current_user.id
    return await action_service.kick_from_company(
        action_id=action_id, current_user_id=current_user_id
    )


@router.get(
    "/company/{company_id}/invites", response_model=List[GetActionsResponseSchema]
)
async def get_company_invites(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_company_invites(current_user_id, company_id)


@router.get(
    "/company/{company_id}/requests", response_model=List[GetActionsResponseSchema]
)
async def get_company_requests(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
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


@router.get(
    "/company/{company_id}/members", response_model=List[GetActionsResponseSchema]
)
async def get_company_members(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetActionsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_company_members(current_user_id, company_id)


@router.patch(
    "/company/{company_id}/add/admin/user/{user_id}", response_model=CompanyMemberSchema
)
async def add_admin(
    company_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> CompanyMemberSchema:
    current_user_id = current_user.id
    return await action_service.add_admin(current_user_id, company_id, user_id)


@router.patch(
    "/company/{company_id}/remove/admin/user/{user_id}",
    response_model=CompanyMemberSchema,
)
async def remove_admin(
    company_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> CompanyMemberSchema:
    current_user_id = current_user.id
    return await action_service.remove_admin(current_user_id, company_id, user_id)


@router.get(
    "/company/{company_id}/admins", response_model=List[GetAdminsResponseSchema]
)
async def get_admins(
    company_id: uuid.UUID,
    current_user: UserSchema = Depends(AuthService.get_current_user),
    action_service: ActionService = Depends(get_action_service),
) -> List[GetAdminsResponseSchema]:
    current_user_id = current_user.id
    return await action_service.get_admins(current_user_id, company_id)
