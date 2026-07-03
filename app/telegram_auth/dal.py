from uuid import UUID

from sqlalchemy import delete, select, update

from core.crud_base import CrudBase
from core.repo_base import RepoBase
from core.serializer import Serializer
from core.types import DTO
from telegram_auth.models import TelegramLink
from telegram_auth.tables import telegram_link_table


class TelegramLinkCrud(CrudBase[int, DTO]):
    table = telegram_link_table

    async def get_by_telegram_id(self, telegram_id: int) -> DTO | None:
        res = await self.session.execute(select(self.table).where(self.table.c.telegram_id == telegram_id))
        return res.mappings().one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> DTO | None:
        res = await self.session.execute(select(self.table).where(self.table.c.user_id == user_id))
        return res.mappings().one_or_none()

    async def update_user_id(self, telegram_id: int, user_id: UUID) -> None:
        await self.session.execute(
            update(self.table).where(self.table.c.telegram_id == telegram_id).values(user_id=user_id)
        )

    async def delete_by_telegram_id(self, telegram_id: int) -> None:
        await self.session.execute(delete(self.table).where(self.table.c.telegram_id == telegram_id))


class TelegramLinkRepo(RepoBase[int, TelegramLink]):
    crud: TelegramLinkCrud

    def __init__(self, crud: TelegramLinkCrud, serializer: Serializer[TelegramLink, DTO]):
        super().__init__(crud, serializer, TelegramLink)

    async def get_by_telegram_id(self, telegram_id: int) -> TelegramLink | None:
        dto = await self.crud.get_by_telegram_id(telegram_id)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def get_by_user_id(self, user_id: UUID) -> TelegramLink | None:
        dto = await self.crud.get_by_user_id(user_id)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def update_user_id(self, telegram_id: int, user_id: UUID) -> None:
        await self.crud.update_user_id(telegram_id, user_id)

    async def delete_by_telegram_id(self, telegram_id: int) -> None:
        await self.crud.delete_by_telegram_id(telegram_id)
