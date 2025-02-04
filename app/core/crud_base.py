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
