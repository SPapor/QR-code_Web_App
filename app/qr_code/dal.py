from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update

from core.crud_base import CrudBase
from core.repo_base import RepoBase
from core.serializer import Serializer
from core.types import DTO
from qr_code.models import QrCode
from qr_code.tables import qr_code_table


class QrCodeCrud(CrudBase[UUID, DTO]):
    table = qr_code_table

    async def get_all_user_qr_codes(self, user_id: UUID) -> Sequence[DTO]:
        res = await self.session.execute(select(self.table).where(self.table.c.user_id == user_id))
        return res.mappings().all()

    async def transfer_owner(self, from_user_id: UUID, to_user_id: UUID) -> None:
        await self.session.execute(
            update(self.table).where(self.table.c.user_id == from_user_id).values(user_id=to_user_id)
        )

    async def increment_scan_count(self, id_: UUID, now: int) -> None:
        await self.session.execute(
            update(self.table)
            .where(self.table.c.id == id_)
            .values(scan_count=self.table.c.scan_count + 1, last_scan_at=now)
        )


class QrCodeRepo(RepoBase[UUID, QrCode]):
    crud: QrCodeCrud

    def __init__(self, crud: QrCodeCrud, serializer: Serializer[QrCode, DTO]):
        super().__init__(crud, serializer, QrCode)

    async def get_all_user_qr_codes(self, user_id: UUID) -> Sequence[QrCode]:
        qr_code = await self.crud.get_all_user_qr_codes(user_id)
        return self.serializer.flat.deserialize(qr_code)

    async def transfer_owner(self, from_user_id: UUID, to_user_id: UUID) -> None:
        await self.crud.transfer_owner(from_user_id, to_user_id)

    async def increment_scan_count(self, id_: UUID, now: int) -> None:
        await self.crud.increment_scan_count(id_, now)
