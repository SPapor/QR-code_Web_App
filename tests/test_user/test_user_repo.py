from user.models import User
from uuid import UUID

from test_user.conftest import user

async def test_user_repo_get_by_id(user_repo, user_dto_in_db):
    u = await user_repo.get_by_id(user_dto_in_db["id"])
    assert isinstance(u, User)
    assert u.id == user_dto_in_db["id"]
    assert u.username == user_dto_in_db["username"]

async def test_user_crud_create(user_crud, user_dto):
    id_ = await user_crud.create(user_dto)
    assert isinstance(id_, UUID)
