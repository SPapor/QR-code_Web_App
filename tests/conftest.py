import pytest
import pytest_asyncio
from core.database import ConnectionProvider
from databases import Database
from dishka import make_async_container


@pytest.fixture
def container():
    return make_async_container(ConnectionProvider("sqlite:///:memory:"))


@pytest_asyncio.fixture
async def database(container) -> Database:
    database = await container.get(Database)
    return database
