from uuid import UUID

from sqlalchemy import select

from core.crud_base import CrudBase
from core.repo_base import RepoBase
from core.serializer import Serializer
from core.types import DTO
from google_auth.models import GoogleLink
from google_auth.tables import google_link_table


class GoogleLinkCrud(CrudBase[str]):
    table = google_link_table

    async def get_by_sub(self, google_sub: str) -> DTO | None:
        res = await self.session.execute(select(self.table).where(self.table.c.google_sub == google_sub))
        return res.mappings().one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> DTO | None:
        res = await self.session.execute(select(self.table).where(self.table.c.user_id == user_id))
        return res.mappings().one_or_none()


class GoogleLinkRepo(RepoBase[str, GoogleLink]):
    crud: GoogleLinkCrud

    def __init__(self, crud: GoogleLinkCrud, serializer: Serializer[GoogleLink, DTO]):
        super().__init__(crud, serializer, GoogleLink)

    async def get_by_sub(self, google_sub: str) -> GoogleLink | None:
        dto = await self.crud.get_by_sub(google_sub)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def get_by_user_id(self, user_id: UUID) -> GoogleLink | None:
        dto = await self.crud.get_by_user_id(user_id)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)
