import uuid
from dataclasses import dataclass, field
from uuid import UUID

from core.models import Model


@dataclass(kw_only=True)
class User(Model):
    username: str
    password_hash: str
    id: UUID = field(default_factory=uuid.uuid4)
