import pytest
import pytest_asyncio
from dishka import Provider, decorate, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine

from core.database import ConnectionProvider, create_tables
from user.providers import UserProvider


class DatabaseWithTablesProvider(Provider):
    @decorate
    async def create_tables_on_connection(self, engine: AsyncEngine) -> AsyncEngine:
        await create_tables(engine)
        return engine


@pytest.fixture
async def container():
    container = make_async_container(
        ConnectionProvider("sqlite+aiosqlite:///:memory:"),
        DatabaseWithTablesProvider(),
        UserProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def request_container(container):
    async with container() as request_container:
        yield request_container
