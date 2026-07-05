import hmac

from fastapi import Header

from core.settings import settings
from telegram_auth.errors import BotIntegrationDisabledError, InvalidBotSecretError


def require_bot_secret(x_bot_secret: str | None = Header(default=None)) -> None:
    if not settings.BOT_SHARED_SECRET:
        raise BotIntegrationDisabledError
    if not x_bot_secret or not hmac.compare_digest(x_bot_secret, settings.BOT_SHARED_SECRET):
        raise InvalidBotSecretError
