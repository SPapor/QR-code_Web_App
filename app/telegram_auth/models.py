from dataclasses import dataclass
from uuid import UUID

from core.models import Model


@dataclass(kw_only=True)
class TelegramLink(Model):
    telegram_id: int
    user_id: UUID


@dataclass(kw_only=True)
class TelegramLinkCode(Model):
    code: str
    user_id: UUID
    expires_at: int
