import functools
from types import MappingProxyType

from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse


class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found")


class AlreadyExistError(ApplicationError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} already exists")


def static_exception_handler(
    app: FastAPI,
    exc: type[ApplicationError],
    status_code: int,
    error_message: str,
    error_code: str,
    kwargs=MappingProxyType({}),
):
    @app.exception_handler(exc)
    async def handle_error(request, e):
        return JSONResponse(
            status_code=status_code, content={"error_message": error_message, "error_code": error_code, **kwargs}
        )

    return handle_error


def register_exception_handlers(app: FastAPI):
    seh = functools.partial(static_exception_handler, app)

    seh(NotFoundError, status.HTTP_404_NOT_FOUND, "Resource not found", "core.0001")
    seh(AlreadyExistError, status.HTTP_409_CONFLICT, "Resource already exists", "core.0002")
    seh(ApplicationError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error", "core.0003")
