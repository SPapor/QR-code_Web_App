import functools

from fastapi import FastAPI
from starlette import status

from core.errors import ApplicationError, static_exception_handler


class AuthError(ApplicationError):
    pass


class NotAuthorizedError(AuthError):
    pass


class InvalidLoginOrPasswordError(AuthError):
    pass


class RefreshTokenRequiredError(AuthError):
    pass


def register_exception_handlers(app: FastAPI):
    seh = functools.partial(static_exception_handler, app)

    seh(AuthError, status.HTTP_403_FORBIDDEN, "Auth error", "auth.0001")
    seh(NotAuthorizedError, status.HTTP_401_UNAUTHORIZED, "Not authorized", "auth.0002")
    seh(RefreshTokenRequiredError, status.HTTP_401_UNAUTHORIZED, "Refresh token required", "auth.0003")
    seh(InvalidLoginOrPasswordError, status.HTTP_401_UNAUTHORIZED, "Invalid login or password", "auth.0004")
