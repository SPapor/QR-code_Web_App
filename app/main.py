import asyncio

from core.database import ConnectionProvider, DatabaseUrl, create_tables
from core.settings import settings
from dishka import make_async_container


def get_container():
    return make_async_container(ConnectionProvider(f"sqlite:///./{settings.db_name}"))


async def main():
    container = get_container()
    create_tables(db_url=await container.get(DatabaseUrl))


if __name__ == '__main__':
    asyncio.run(main())
