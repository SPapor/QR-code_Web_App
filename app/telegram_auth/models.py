from dataclasses import dataclass
from uuid import UUID

from core.models import Model


@dataclass(kw_only=True)
class TelegramLink(Model):
    telegram_id: int
    user_id: UUID
