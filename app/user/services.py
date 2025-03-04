from datetime import timedelta
from uuid import UUID

import jwt

from auth.regist import create_jwt_token, get_password_hash, verify_password
from core.settings import settings
from user.dal import UserRepo
from user.models import User


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register(self, username: str, password: str) -> tuple[User, tuple[str, str]]:
        password_hash = get_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        user = await self.user_repo.create_and_get(user)
        access_token = create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return user, (access_token, refresh_token)

    async def login(self, username: str, password: str):

        user = await self.user_repo.get_by_username(username)
        if user is None:
            raise ValueError("User not found")
        is_authorized = verify_password(password, user.password_hash)
        if not is_authorized:
            raise ValueError("Not authorized")

        access_token = create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return access_token, refresh_token

    async def refresh(self, refresh_token: str):
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("Refresh token is not valid")
        user = await self.user_repo.get_by_id(UUID(user_id))
        access_token = create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return access_token, refresh_token
