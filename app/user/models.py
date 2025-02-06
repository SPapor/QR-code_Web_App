from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    username: str
    id: UUID = None
