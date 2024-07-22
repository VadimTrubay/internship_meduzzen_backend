from app.conf.detail import Messages


class BaseCustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExists(BaseCustomError):
    def __init__(self, message=Messages.USER_ALREADY_EXISTS):
        super().__init__(message)


class EmailAlreadyExists(BaseCustomError):
    def __init__(self, message=Messages.EMAIL_AlREADY_EXISTS):
        super().__init__(message)


class UserNotFound(BaseCustomError):
    def __init__(self, message=Messages.USER_NOT_FOUND):
        super().__init__(message)


class CompanyNotFound(BaseCustomError):
    def __init__(self, message=Messages.COMPANY_NOT_FOUND):
        super().__init__(message)


class NotFound(BaseCustomError):
    def __init__(self, message=Messages.NOT_FOUND):
        super().__init__(message)


class UserWithEmailNotFound(BaseCustomError):
    def __init__(self, message=Messages.USER_WITH_EMAIL_NOT_FOUND):
        super().__init__(message)


class IncorrectPassword(BaseCustomError):
    def __init__(self, message=Messages.INCORRECT_PASSWORD):
        super().__init__(message)


class UnAuthorized(BaseCustomError):
    def __init__(self, message=Messages.UNAUTHORIZED):
        super().__init__(message)


class NotPermission(BaseCustomError):
    def __init__(self, message=Messages.NOT_PERMISSION):
        super().__init__(message)
