from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from passlib.context import CryptContext

from core.settings import settings
from user.dal import UserRepo
from user.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register(self, username: str, password: str) -> tuple[User, tuple[str, str]]:
        password_hash = get_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        user = await self.user_repo.create_and_get(user)
        access_token = self.create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = self.create_jwt_token(
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

        access_token = self.create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = self.create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return access_token, refresh_token

    async def refresh(self, refresh_token: str):
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("Refresh token is not valid")
        user = await self.user_repo.get_by_id(UUID(user_id))
        access_token = self.create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = self.create_jwt_token(
            {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return access_token, refresh_token

    @staticmethod
    def create_jwt_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
