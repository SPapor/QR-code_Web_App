import functools

from fastapi import FastAPI

from core.errors import static_exception_handler
from qr_code.models import QrCode


def register_exception_handlers(app: FastAPI):
    seh = functools.partial(static_exception_handler, app)

    seh(QrCode.NotFoundError, 404, "QrCode not found", "qr_code.0001")
    seh(QrCode.AlreadyExistError, 409, "QrCode already exists", "qr_code.0002")
