from typing import ClassVar, Sequence, TypeVar, Mapping, Any

from sqlalchemy import Table, insert, literal, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

DTO = TypeVar("DTO", bound=Mapping[str, Any])


class CrudBase[ID, DTO]:
    table: ClassVar[Table]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_: ID) -> DTO | None:
        res = await self.session.execute(select(self.table).where(self.table.c.id == literal(id_)))
        return res.mappings().one_or_none()

    async def create(self, obj: DTO) -> ID:
        res = await self.session.execute(insert(self.table).values(**obj))
        pk = res.inserted_primary_key
        return pk[0] if len(pk) == 1 else pk

    async def create_and_get(self, obj: DTO) -> DTO:
        res = await self.session.execute(insert(self.table).values(**obj).returning(self.table))
        return res.mappings().one_or_none()

    async def create_many(self, objs: Sequence[DTO]) -> list[ID]:
        objs = list(objs)
        if len(objs) == 0:
            return []
        # TODO: res = self.session.execute(... .returning(self.table.c.id)))
        res = ...
        return [row[0] for row in res.all()]

    async def create_and_get_many(self, objs: Sequence[DTO]) -> Sequence[DTO]:
        objs = list(objs)
        ...  # TODO

    async def update(self, values: DTO) -> None:
        id_ = values.pop("id")
        if not values:
            return
        # TODO

    async def update_many(self, objs: Sequence[DTO]) -> None:
        for obj in objs:
            # TODO
            ...

    async def get_many_by_ids(self, ids: Sequence[ID]) -> Sequence[DTO]:
        # TODO
        ...

    async def delete(self, id_: ID) -> None:
        # TODO
        ...

    async def delete_many(self, ids: Sequence[ID]) -> None:
        # TODO
        ...

    async def count(self) -> int:
        # TODO
        res = ...
        return res.scalar()

    async def get_all(self) -> Sequence[DTO]:
        # TODO
        ...
