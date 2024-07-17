from enum import Enum


class Messages(Enum):
    NOT_FOUND = "Not found"
    UNAUTHORIZED = "Unauthorized"
    SUCCESS_GET_USER = "Success get user"
    SUCCESS_GET_USERS = "Success get users"
    SUCCESS_CREATE_USER = "Success create user"
    SUCCESS_UPDATE_USER = "User updated"
    SUCCESS_DELETE_USER = "User deleted"
    USER_ALREADY_EXISTS = "User already exists"
    EMAIL_AlREADY_EXISTS = "Email already exists"
    USER_NOT_FOUND = "User is not found"
    USER_WITH_EMAIL_NOT_FOUND = "User with email not found"
    INVALID_EMAIL = "Invalid email"
    INCORRECT_PASSWORD = "Incorrect password"
    EMAIL_NOT_CONFIRMED = "Email not confirmed"
    INVALID_PASSWORD = "Invalid password"
    INVALID_REFRESH_TOKEN = "Invalid refresh token"
    VERIFICATION_ERROR = "Verification error"
    ALREADY_CONFIRMED = "Your email is already confirmed"
    EMAIL_CONFIRMED = "Email confirmed"
    CHECK_CONFIRMATION = "Check your email for confirmation."
    INVALID_TOKEN = "Invalid scope for token"
    NOT_VALIDATE = "Could not validate credentials"
    INVALID_TOKEN_EMAIL = "Invalid token for email verification"
    PRIVILEGES_DENIED = "You don't have this privileges"
    USER_ROLE_EXISTS = "User role exists"
    USER_CHANGE_ROLE_TO = "User change role"
    OPERATION_FORBIDDEN = "Operation forbidden"
    USER_IS_LOGOUT = "User is logout"

    def __str__(self):
        return self.value
