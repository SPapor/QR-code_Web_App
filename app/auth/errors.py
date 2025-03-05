from core.errors import ApplicationError


class AuthError(ApplicationError):
    pass


class NotAuthorizedError(AuthError):
    pass
