from dataclasses import dataclass
from uuid import UUID

from core.models import Model


@dataclass(kw_only=True)
class GoogleLink(Model):
    google_sub: str
    user_id: UUID
    email: str
