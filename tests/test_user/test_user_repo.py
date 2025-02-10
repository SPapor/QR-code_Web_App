from user.models import User


async def test_user_repo_get_by_id(user_repo, user_dto_in_db):
    u = await user_repo.get_by_id(user_dto_in_db["id"])
    assert isinstance(u, User)
    assert u.id == user_dto_in_db["id"]
    assert u.username == user_dto_in_db["username"]
