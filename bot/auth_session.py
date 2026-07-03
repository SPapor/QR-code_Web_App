from __future__ import annotations

from typing import Awaitable, Callable, TypeVar

from api_client import AuthExpiredError, BackendClient, TokenPair
from session_store import Session, SessionStore

T = TypeVar("T")


class NotLoggedInError(Exception):
    pass


class AuthSession:
    """Per-update wrapper that handles token refresh and persistence."""

    def __init__(self, telegram_id: int, store: SessionStore, client: BackendClient):
        self._telegram_id = telegram_id
        self._store = store
        self._client = client
        self._session: Session | None = None
        self._loaded = False

    async def _load(self) -> Session | None:
        if not self._loaded:
            self._session = await self._store.get(self._telegram_id)
            self._loaded = True
        return self._session

    async def is_logged_in(self) -> bool:
        return (await self._load()) is not None

    async def store_tokens(self, pair: TokenPair) -> None:
        new = Session(access_token=pair.access_token, refresh_token=pair.refresh_token)
        await self._store.save(self._telegram_id, new)
        self._session = new
        self._loaded = True

    async def clear(self) -> None:
        await self._store.delete(self._telegram_id)
        self._session = None
        self._loaded = True

    async def call(self, fn: Callable[[str], Awaitable[T]]) -> T:
        session = await self._load()
        if session is None:
            raise NotLoggedInError()
        try:
            return await fn(session.access_token)
        except AuthExpiredError:
            pass

        try:
            pair = await self._client.refresh(session.refresh_token)
        except AuthExpiredError as exc:
            await self.clear()
            raise NotLoggedInError() from exc

        await self.store_tokens(pair)
        return await fn(pair.access_token)
