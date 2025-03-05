import functools

from fastapi import FastAPI

from core.errors import static_exception_handler
from user.models import User


def register_exception_handlers(app: FastAPI):
    seh = functools.partial(static_exception_handler, app)

    seh(User.NotFoundError, 404, "User not found", "qr_code.0001")
    seh(User.AlreadyExistError, 409, "User already exists", "qr_code.0002")
