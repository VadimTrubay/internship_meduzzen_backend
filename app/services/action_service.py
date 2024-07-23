import uuid
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exept.custom_exceptions import (
    AlreadyInCompany,
    NotOwner,
    CompanyNotFound,
    UserNotFound,
    ActionNotFound,
)
from app.conf.invite import InvitationStatus, InvitationType, MemberStatus
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.user_repository import UserRepository
from app.schemas.actions import (
    ActionSchema,
    InviteCreateSchema,
    RequestCreateSchema,
    GetActionsResponseSchema,
    CompanyMemberSchema,
)
from app.schemas.companies import CompanySchema
from app.schemas.users import UserSchema
from app.utils import companies_utils


class ActionService:
    def __init__(
        self,
        session: AsyncSession,
        action_repository: ActionRepository,
        company_repository: CompanyRepository,
        user_repository: UserRepository,
    ):
        self.session = session
        self.action_repository = action_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    async def _get_company_or_raise(self, company_id: uuid.UUID) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise CompanyNotFound()
        return company

    async def _get_user_or_raise(self, user_id: uuid.UUID) -> UserSchema:
        user = await self.user_repository.get_one(id=user_id)
        if not user:
            raise UserNotFound()
        return user

    async def _get_action_or_raise(self, action_id: uuid.UUID) -> ActionSchema:
        action = await self.action_repository.get_one(id=action_id)
        if not action:
            raise ActionNotFound()
        return action

    async def _add_user_to_company(
        self, action_id: uuid.UUID, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> CompanyMemberSchema:
        company_member_data = {
            "user_id": user_id,
            "company_id": company_id,
            "role": MemberStatus.USER,
        }
        company_member = await self.company_repository.create_company_member(
            company_member_data
        )
        update_data = {"status": InvitationStatus.ACCEPTED.value}
        await self.action_repository.update_one(action_id, update_data)
        return company_member

    async def create_invite(
        self, action_data: InviteCreateSchema, current_user_id: uuid.UUID
    ) -> ActionSchema:
        await self._get_user_or_raise(action_data.user_id)
        company = await self._get_company_or_raise(action_data.company_id)
        await self.company_repository.is_user_company_owner(current_user_id, company.id)

        if action_data.user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You can't invite yourself",
            )
        invite = await self.action_repository.get_one(
            company_id=company.id,
            user_id=action_data.user_id,
        )
        if invite:
            match invite.status:
                case InvitationStatus.ACCEPTED:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User is already invited",
                    )
                case InvitationStatus.ACCEPTED:
                    raise AlreadyInCompany()
                case InvitationStatus.REQUESTED:
                    await self._add_user_to_company(
                        invite.id, current_user_id, company.id
                    )
                    return invite
                case InvitationStatus.DECLINED_BY_USER:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can't invite this user",
                    )
                case InvitationStatus.DECLINED_BY_COMPANY:
                    invite.status = InvitationStatus.REQUESTED
                    return invite
        else:
            data = action_data.dict()
            data["status"] = InvitationStatus.INVITED.value
            data["type"] = InvitationType.INVITE.value
            return await self.action_repository.create_one(data=data)

    async def cancel_invite(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        company = await self._get_company_or_raise(action.company_id)
        if not self.company_repository.is_user_company_owner(
            current_user_id, company.id
        ):
            raise NotOwner()
        await self.action_repository.delete_one(action_id)
        return action

    async def _get_invite(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        await companies_utils.check_correct_user(action.user_id, current_user_id)
        companies_utils.check_invited(action.status)
        return action

    async def accept_invite(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_invite(action_id, current_user_id)
        company_id = action.company_id
        await companies_utils.check_correct_user(action.user_id, current_user_id)
        await self._add_user_to_company(action_id, current_user_id, company_id)
        return action

    async def decline_invite(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_invite(action_id, current_user_id)
        update_data = {"status": InvitationStatus.DECLINED_BY_USER}
        await self.action_repository.update_one(action_id, update_data)
        return action

    async def create_request(
        self, action_data: RequestCreateSchema, current_user_id: id
    ) -> ActionSchema:
        company = await self._get_company_or_raise(action_data.company_id)
        request = await self.action_repository.get_one(
            company_id=company.id, user_id=current_user_id
        )
        if await self.company_repository.is_user_company_owner(
            current_user_id, company.id
        ):
            raise AlreadyInCompany()
        if request:
            match request.status:
                case InvitationStatus.REQUESTED:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="You have already sent a request to this company",
                    )
                case InvitationStatus.ACCEPTED:
                    raise AlreadyInCompany()
                case InvitationStatus.INVITED:
                    await self._add_user_to_company(
                        request.id, current_user_id, company.id
                    )
                    request.status = InvitationStatus.ACCEPTED
                    return request
                case InvitationStatus.DECLINED_BY_COMPANY:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="You have already declined this company",
                    )
                case InvitationStatus.DECLINED_BY_USER:
                    request.status = InvitationStatus.REQUESTED
                    return request
        else:
            data = action_data.dict()
            data["status"] = InvitationStatus.REQUESTED.value
            data["user_id"] = current_user_id
            data["type"] = InvitationType.REQUEST.value
            return await self.action_repository.create_one(data=data)

    async def cancel_request(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        companies_utils.check_requested(action.status)
        await companies_utils.check_correct_user(action.user_id, current_user_id)
        await self.action_repository.delete_one(action.id)
        return action

    async def _validate_request(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        company = await self._get_company_or_raise(action.company_id)
        if not await self.company_repository.is_user_company_owner(
            current_user_id, company.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return action

    async def accept_request(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._validate_request(action_id, current_user_id)
        companies_utils.check_requested(action.status)
        company = await self._get_company_or_raise(action.company_id)
        await self._add_user_to_company(action_id, current_user_id, company.id)
        return action

    async def decline_request(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._validate_request(action_id, current_user_id)
        companies_utils.check_requested(action.status)
        update_data = {"status": InvitationStatus.DECLINED_BY_COMPANY}
        await self.action_repository.update_one(action_id, update_data)
        return action

    async def leave_from_company(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        company_id = action.company_id
        if current_user_id != action.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to leave this company",
            )
        await self.company_repository.delete_company_member(company_id, current_user_id)
        return await self.action_repository.delete_one(action.id)

    async def kick_from_company(
        self, action_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActionSchema:
        action = await self._validate_request(action_id, current_user_id)
        company_id = action.company_id
        await self.company_repository.delete_company_member(company_id, action.user_id)
        return await self.action_repository.delete_one(action.id)

    async def _validate_company_get(
        self, current_user_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        await self.company_repository.is_user_company_owner(current_user_id, company.id)
        return company

    async def _process_query_results(self, results):
        actions = []
        for action, user in results.fetchall():
            action_dto = GetActionsResponseSchema(
                id=action.id, user_id=user.id, user_username=user.username
            )
            actions.append(action_dto)
        return actions

    async def get_company_invites(
        self, current_user_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        query = await self.action_repository.get_relatives_query(
            company_id, InvitationStatus.INVITED, True
        )
        result = await self.session.execute(query)
        invites = await self._process_query_results(result)
        return invites

    async def get_company_requests(
        self, current_user_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        query = await self.action_repository.get_relatives_query(
            company_id, InvitationStatus.REQUESTED, True
        )
        result = await self.session.execute(query)
        requests = await self._process_query_results(result)
        return requests

    async def get_company_members(
        self, current_user_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        query = await self.action_repository.get_relatives_query(
            company_id, InvitationStatus.ACCEPTED, True
        )
        result = await self.session.execute(query)
        members = await self._process_query_results(result)
        return members

    async def get_my_requests(
        self, current_user_id: uuid.UUID
    ) -> List[GetActionsResponseSchema]:
        query = await self.action_repository.get_relatives_query(
            current_user_id, InvitationStatus.REQUESTED, False
        )
        result = await self.session.execute(query)
        requests = await self._process_query_results(result)
        return requests

    async def get_my_invites(
        self, current_user_id: uuid.UUID
    ) -> List[GetActionsResponseSchema]:
        query = await self.action_repository.get_relatives_query(
            current_user_id, InvitationStatus.INVITED, False
        )
        result = await self.session.execute(query)
        invites = await self._process_query_results(result)
        return invites
