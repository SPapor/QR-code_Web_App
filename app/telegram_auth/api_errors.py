from fastapi import FastAPI
from starlette import status

from core.api_errors import ApiError, static_exception_handler
from telegram_auth.errors import (
    BotIntegrationDisabledError,
    InvalidBotSecretError,
    TargetAccountAlreadyLinkedError,
)


class ApiErrors:
    INVALID_BOT_SECRET = ApiError(status.HTTP_401_UNAUTHORIZED, "Invalid bot secret", "telegram_auth.0001")
    BOT_INTEGRATION_DISABLED = ApiError(status.HTTP_404_NOT_FOUND, "Bot integration disabled", "telegram_auth.0002")
    TARGET_ACCOUNT_ALREADY_LINKED = ApiError(
        status.HTTP_409_CONFLICT,
        "Target account is already linked to another Telegram user",
        "telegram_auth.0003",
    )


def register_exception_handlers(app: FastAPI):
    static_exception_handler(app, InvalidBotSecretError, ApiErrors.INVALID_BOT_SECRET)
    static_exception_handler(app, BotIntegrationDisabledError, ApiErrors.BOT_INTEGRATION_DISABLED)
    static_exception_handler(app, TargetAccountAlreadyLinkedError, ApiErrors.TARGET_ACCOUNT_ALREADY_LINKED)
