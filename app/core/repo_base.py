from typing import TypeVar

from core.crud_base import CrudBase
from core.serializer import Serializer

T = TypeVar("T")


class RepoBase[ID, Model]:
    def __init__(self, crud: CrudBase[ID, T], serializer: Serializer[Model, T]):
        self.crud = crud
        self.serializer = serializer

    async def get_by_id(self, id_: ID) -> Model:
        dto = await self.crud.get_by_id(id_)
        return self.serializer.deserialize(dto)
