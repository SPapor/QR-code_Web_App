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
