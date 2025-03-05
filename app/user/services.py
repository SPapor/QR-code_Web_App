from auth.services import AuthService
from user.dal import UserRepo
from user.models import User


class UserService:
    def __init__(self, user_repo: UserRepo, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def register(self, username: str, password_hash: str) -> User:
        user = User(username=username, password_hash=password_hash)
        user = await self.user_repo.create_and_get(user)
        return user
