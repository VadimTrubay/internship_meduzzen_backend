from enum import Enum


class Messages(Enum):
    NOT_FOUND = "Not found"
    UNAUTHORIZED = "Unauthorized"
    NOT_PERMISSION = "Permission denied"
    SUCCESS_GET_USER = "Success get user"
    SUCCESS_GET_USERS = "Success get users"
    SUCCESS_CREATE_USER = "Success create user"
    SUCCESS_UPDATE_USER = "User updated"
    SUCCESS_DELETE_USER = "User deleted"
    SUCCESS_GET_COMPANIES = "Success get companies"
    SUCCESS_GET_COMPANY = "Success get company"
    SUCCESS_CREATE_COMPANY = "Success create company"
    SUCCESS_UPDATE_COMPANY = "Company updated"
    SUCCESS_DELETE_COMPANY = "Company deleted"
    SUCCESS_GET_TOTAL_COUNT = "Success get total count"
    USER_ALREADY_EXISTS = "User already exists"
    EMAIL_AlREADY_EXISTS = "Email already exists"
    USER_NOT_FOUND = "User is not found"
    COMPANY_NOT_FOUND = "Company not found"
    ACTION_NOT_FOUND = "Action not found"
    USER_WITH_EMAIL_NOT_FOUND = "User with email not found"
    INCORRECT_PASSWORD = "Incorrect password"
    ALREADY_IN_COMPANY = "User is already in company"
    NOT_OWNER_COMPANY = "You are not the owner of this company"
    USER_NOT_REQUESTED = "User is not requested"
    USER_NOT_INVITED = "User is not invited"
    USER_NOT_INTERACT_WITH_ACTIONS = "You can't interact with this action"
    USER_ALREADY_INVITED = "User is already invited"
    ACTION_ALREADY_AVAILABLE = "Action is already available"
    SUCCESS_GET_CURRENT_USER = "Success get current user"

    def __str__(self):
        return self.value
