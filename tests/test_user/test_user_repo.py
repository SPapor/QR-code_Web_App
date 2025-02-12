from uuid import UUID

import pytest

from app.user.models import User


async def test_user_repo_get_by_id(user_repo, user_dto_in_db):
    u = await user_repo.get_by_id(user_dto_in_db["id"])
    assert isinstance(u, User)
    assert u.id == user_dto_in_db["id"]
    assert u.username == user_dto_in_db["username"]


async def test_user_repo_create(user_repo, user):
    id_ = await user_repo.create(user)
    assert isinstance(id_, UUID)


@pytest.mark.parametrize("users_number", [2])
async def test_user_repo_create_many(user_repo, users, users_number):
    ids = await user_repo.create_many(users)
    assert len(ids) == len(users)


async def test_user_crud_create_and_get(user_repo,user):
    dto = await user_repo.create_and_get(user)
    assert dto.id == user.id
    assert dto.username == user.username


@pytest.mark.parametrize('users_number', [2])
async def test_user_crud_create_and_get_many(user_repo, users, users_number):
    ids = await user_repo.create_and_get_many(users)
    assert len(ids) == len(users)
    for dto ,payload in zip(ids,users):
        assert dto.username == payload.username

# async def test_user_crud_update(user_repo, user):
#     await user_repo.update(user)
#     user_get = await user_repo.get_by_id(user.id)
#     assert user_get.username == user.username