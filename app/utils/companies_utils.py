import uuid

from fastapi import HTTPException
from starlette import status

from app.conf.invite import InvitationStatus


async def check_company_owner(user_id: uuid.UUID, company_owner_id) -> None:
    if user_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to interact with this company",
        )
    return


async def check_correct_user(user_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot interact with this action",
        )


def check_invited(action_status: InvitationStatus) -> None:
    if action_status != InvitationStatus.INVITED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is not invited",
        )


def check_requested(action_status: InvitationStatus) -> None:
    if action_status != InvitationStatus.REQUESTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is not requested",
        )
