import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(kw_only=True)
class User:
    username: str
    password_hash: str
    id: UUID = field(default_factory=uuid.uuid4)
