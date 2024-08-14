import uuid

from app.conf.invite import InvitationStatus
from app.exept.custom_exceptions import (
    UserNotRequested,
    UserNotInvited,
    UserNotInteractWithActions,
    UnAuthorized,
)


async def check_company_owner(user_id: uuid.UUID, company_owner_id) -> None:
    if user_id != company_owner_id:
        raise UnAuthorized()

    return


async def check_correct_user(user_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
    if user_id != current_user_id:
        raise UserNotInteractWithActions()


def check_invited(action_status: InvitationStatus) -> None:
    if action_status != InvitationStatus.INVITED:
        raise UserNotInvited()


def check_requested(action_status: InvitationStatus) -> None:
    if action_status != InvitationStatus.REQUESTED:
        raise UserNotRequested()
