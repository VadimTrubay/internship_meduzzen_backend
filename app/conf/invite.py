from enum import Enum


class InvitationStatus(Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    REQUESTED = "requested"
    DECLINED_BY_USER = "declined_by_user"
    DECLINED_BY_COMPANY = "declined_by_company"


class InvitationType(str, Enum):
    INVITE = "invite"
    REQUEST = "request"


class MemberStatus(str, Enum):
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"
