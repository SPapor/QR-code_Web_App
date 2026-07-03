from __future__ import annotations

import os
from dataclasses import dataclass

import aiosqlite


@dataclass
class Session:
    access_token: str
    refresh_token: str


class SessionStore:
    def __init__(self, db_path: str):
        self._db_path = db_path

    async def init(self) -> None:
        directory = os.path.dirname(self._db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    telegram_id   INTEGER PRIMARY KEY,
                    access_token  TEXT NOT NULL,
                    refresh_token TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def get(self, telegram_id: int) -> Session | None:
        async with aiosqlite.connect(self._db_path) as db:
            cur = await db.execute(
                "SELECT access_token, refresh_token FROM sessions WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = await cur.fetchone()
            await cur.close()
        if row is None:
            return None
        return Session(access_token=row[0], refresh_token=row[1])

    async def save(self, telegram_id: int, session: Session) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO sessions (telegram_id, access_token, refresh_token)
                VALUES (?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token
                """,
                (telegram_id, session.access_token, session.refresh_token),
            )
            await db.commit()

    async def delete(self, telegram_id: int) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("DELETE FROM sessions WHERE telegram_id = ?", (telegram_id,))
            await db.commit()
