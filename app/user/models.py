import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(kw_only=True)
class User:
    username: str
    id: UUID = field(default_factory=uuid.uuid4)
