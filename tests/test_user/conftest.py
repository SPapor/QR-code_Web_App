import pytest
import pytest_asyncio

from user.dao import UserCrud


@pytest_asyncio.fixture
async def user_crud(request_container) -> UserCrud:
    return await request_container.get(UserCrud)


@pytest.fixture
def users_payload(users_number):
    return [{"username": f"test_user_{i}"} for i in range(users_number)]


@pytest.fixture
def user_payload(users_payload):
    return users_payload[0]


@pytest.fixture
def users_number():
    return 1


@pytest_asyncio.fixture
async def user_in_db(user_crud, user_payload):
    assert len(user_payload) == 1
    return await user_crud.create_and_get(user_payload)


@pytest_asyncio.fixture
async def users_in_db(user_crud, users_payload):
    return await user_crud.create_and_get_many(users_payload)
