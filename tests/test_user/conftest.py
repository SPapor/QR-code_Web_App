from uuid import uuid4

import pytest
import pytest_asyncio

from user.dao import UserCrud, UserRepo, UserSerializer
from user.models import User


@pytest_asyncio.fixture
async def user_crud(request_container) -> UserCrud:
    return await request_container.get(UserCrud)


@pytest_asyncio.fixture
async def user_serializer(request_container) -> UserSerializer:
    return await request_container.get(UserSerializer)


@pytest_asyncio.fixture
async def user_repo(request_container) -> UserRepo:
    return await request_container.get(UserRepo)


@pytest.fixture
def users_dto(users_number):
    return [{"id": uuid4(), "username": f"test_user_{i}"} for i in range(users_number)]


@pytest.fixture
def user_dto(users_dto):
    assert len(users_dto) == 1
    return users_dto[0]


@pytest.fixture
def users_number():
    return 1


@pytest_asyncio.fixture
async def user_dto_in_db(user_crud, user_dto):
    return await user_crud.create_and_get(user_dto)


@pytest_asyncio.fixture
async def users_dto_in_db(user_crud, users_dto):
    return await user_crud.create_and_get_many(users_dto)


@pytest.fixture
def user():
    return User(id=uuid4(), username="test_user")
