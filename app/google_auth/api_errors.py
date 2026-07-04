from fastapi import FastAPI
from starlette import status

from core.api_errors import ApiError, static_exception_handler
from google_auth.errors import GoogleExchangeFailedError, GoogleIntegrationDisabledError, InvalidGoogleStateError


class ApiErrors:
    GOOGLE_INTEGRATION_DISABLED = ApiError(status.HTTP_404_NOT_FOUND, "Google integration disabled", "google_auth.0001")
    INVALID_GOOGLE_STATE = ApiError(status.HTTP_401_UNAUTHORIZED, "Invalid Google OAuth state", "google_auth.0002")
    GOOGLE_EXCHANGE_FAILED = ApiError(status.HTTP_502_BAD_GATEWAY, "Google code exchange failed", "google_auth.0003")


def register_exception_handlers(app: FastAPI):
    static_exception_handler(app, GoogleIntegrationDisabledError, ApiErrors.GOOGLE_INTEGRATION_DISABLED)
    static_exception_handler(app, InvalidGoogleStateError, ApiErrors.INVALID_GOOGLE_STATE)
    static_exception_handler(app, GoogleExchangeFailedError, ApiErrors.GOOGLE_EXCHANGE_FAILED)
