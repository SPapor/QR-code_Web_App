from uuid import UUID

from sqlalchemy import delete, select

from auth.models import Auth, RefreshSession
from auth.tables import auth_table, refresh_session_table
from core.crud_base import CrudBase
from core.repo_base import RepoBase
from core.serializer import Serializer
from core.types import DTO


class AuthCrud(CrudBase[UUID, DTO]):
    table = auth_table

    async def get_by_username(self, username: str) -> DTO:
        res = await self.session.execute(select(self.table).where(self.table.c.username == username))
        return res.mappings().one()

    async def get_by_user_id(self, user_id: UUID) -> DTO:
        res = await self.session.execute(select(self.table).where(self.table.c.user_id == user_id))
        return res.mappings().one()


class AuthRepo(RepoBase[UUID, Auth]):
    crud: AuthCrud

    def __init__(self, crud: AuthCrud, serializer: Serializer[Auth, DTO]):
        super().__init__(crud, serializer, Auth)

    async def get_by_username(self, username: str) -> Auth:
        dto = await self.crud.get_by_username(username)
        return self.serializer.deserialize(dto)

    async def get_by_user_id(self, user_id: UUID) -> Auth:
        dto = await self.crud.get_by_user_id(user_id)
        return self.serializer.deserialize(dto)


class RefreshSessionCrud(CrudBase[UUID, DTO]):
    table = refresh_session_table

    async def delete_expired(self, now: int) -> None:
        await self.session.execute(delete(self.table).where(self.table.c.expires_at < now))

    async def delete_by_auth_id(self, auth_id: UUID) -> None:
        await self.session.execute(delete(self.table).where(self.table.c.auth_id == auth_id))


class RefreshSessionRepo(RepoBase[UUID, RefreshSession]):
    crud: RefreshSessionCrud

    def __init__(self, crud: RefreshSessionCrud, serializer: Serializer[RefreshSession, DTO]):
        super().__init__(crud, serializer, RefreshSession)

    async def delete_expired(self, now: int) -> None:
        await self.crud.delete_expired(now)

    async def delete_by_auth_id(self, auth_id: UUID) -> None:
        await self.crud.delete_by_auth_id(auth_id)
