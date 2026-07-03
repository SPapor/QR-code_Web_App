from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from api_client import BackendClient
from handlers import build_router
from middlewares.auth import AuthMiddleware
from session_store import SessionStore
from settings import settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    log = logging.getLogger("bot")

    store = SessionStore(settings.SESSION_DB_PATH)
    await store.init()

    client = BackendClient(settings.BACKEND_URL, settings.BOT_SHARED_SECRET)
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    auth_mw = AuthMiddleware(store, client)
    dp.message.middleware(auth_mw)
    dp.callback_query.middleware(auth_mw)

    dp.include_router(build_router())

    log.info("Bot started, backend=%s", settings.BACKEND_URL)
    try:
        await dp.start_polling(bot)
    finally:
        await client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
