from typing import Sequence, TypeVar

from core.crud_base import CrudBase
from core.serializer import Serializer

T = TypeVar("T")


class RepoBase[ID, Model]:
    def __init__(self, crud: CrudBase[ID, T], serializer: Serializer[Model, T]):
        self.crud = crud
        self.serializer = serializer

    async def get_by_id(self, id_: ID) -> Model:
        dto = self.crud.get_by_id(id_)
        return await self.serializer.deserialize(dto)

    async def create(self, model: Model) -> ID:
        dto = self.serializer.serialize(model)
        return await self.crud.create(dto)

    async def create_and_get(self, model: Model) -> Model:
        dto = self.serializer.serialize(model)
        return await self.crud.create_and_get(dto)

    async def create_many(self, models: Sequence[Model]) -> list[ID]:
        dtos = self.serializer.flat.serialize(models)
        return await self.crud.create_many(dtos)

    async def create_and_get_many(self, models: Sequence[Model]) -> Sequence[Model]:
        dtos = self.serializer.flat.serialize(models)
        return await self.crud.create_and_get_many(dtos)

    async def update(self, values: Model) -> None:
        dto = self.serializer.serialize(values)
        await self.crud.update(dto)

    # async def update_many(self, objs: Sequence[DTO]) -> None:
    #     pass
    # async def get_many_by_ids(self, ids: Sequence[ID]) -> Sequence[DTO]:
    #     pass
    # async def delete(self, id_: ID) -> None:
    #     pass
    #
    # async def delete_many(self, ids: Sequence[ID]) -> None:
    #     pass
    #
    # async def count(self) -> int:
    #     pass
    #
    # async def get_all(self) -> Sequence[DTO]:
    #     pass
