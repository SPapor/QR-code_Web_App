from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from api_client import BackendClient
from auth_session import AuthSession
from session_store import SessionStore


class AuthMiddleware(BaseMiddleware):
    def __init__(self, store: SessionStore, client: BackendClient):
        self._store = store
        self._client = client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is not None:
            data["auth"] = AuthSession(user.id, self._store, self._client)
        data["client"] = self._client
        return await handler(event, data)
