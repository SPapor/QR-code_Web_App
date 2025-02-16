import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(kw_only=True)
class QrCode:
    id: UUID = field(default_factory=uuid.uuid4)
    user_id: UUID
    name: str
    link: str
