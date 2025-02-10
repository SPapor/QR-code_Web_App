import asyncio

from dishka import make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine

from core.database import ConnectionProvider, create_tables
from core.settings import settings
from user.providers import UserProvider


def get_container():
    return make_async_container(ConnectionProvider(f"sqlite+aiosqlite:///./{settings.db_name}"), UserProvider())


async def main():
    container = get_container()
    await create_tables(await container.get(AsyncEngine))


if __name__ == '__main__':
    asyncio.run(main())
