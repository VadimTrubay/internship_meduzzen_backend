import uuid

from pydantic import BaseModel, ConfigDict

from app.conf.invite import InvitationStatus, InvitationType, MemberStatus


class ActionBaseSchema(BaseModel):
    id: uuid.UUID


class ActionSchema(ActionBaseSchema):
    user_id: uuid.UUID
    company_id: uuid.UUID
    status: InvitationStatus
    type: InvitationType

    model_config = ConfigDict(from_attributes=True)


class InviteCreateSchema(BaseModel):
    user_id: uuid.UUID
    company_id: uuid.UUID


class RequestCreateSchema(BaseModel):
    user_id: uuid.UUID
    company_id: uuid.UUID


class GetActionsResponseSchema(ActionBaseSchema):
    user_id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
    user_username: str


class MembersResponseSchema(ActionBaseSchema):
    user_id: uuid.UUID
    user_username: str
    company_id: uuid.UUID
    action_id: uuid.UUID
    company_name: str
    role: MemberStatus

    model_config = ConfigDict(from_attributes=True)


class GetAdminsResponseSchema(ActionBaseSchema):
    user_id: uuid.UUID
    user_username: str


class GetActionsAdminResponseSchema(ActionBaseSchema):
    user_id: uuid.UUID
    user_username: str


class CompanyMemberSchema(ActionBaseSchema):
    user_id: uuid.UUID
    company_id: uuid.UUID
    role: MemberStatus

    model_config = ConfigDict(from_attributes=True)
