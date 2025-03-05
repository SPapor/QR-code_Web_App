from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt import DecodeError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel

from auth.errors import NotAuthorizedError
from core.settings import settings
from user.dal import UserRepo
from user.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccessTokenPayload(BaseModel):
    user_id: UUID


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo
        self.access_token_exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_exp = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    async def register(self, username: str, password: str) -> tuple[User, tuple[str, str]]:
        password_hash = self.get_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        user = await self.user_repo.create_and_get(user)
        token_pair = self.create_access_refresh_token_pait(user)
        return user, token_pair

    async def login(self, username: str, password: str):
        user = await self.user_repo.get_by_username(username)
        is_authorized = self.verify_password(password, user.password_hash)
        if not is_authorized:
            raise NotAuthorizedError

        token_pair = self.create_access_refresh_token_pait(user)
        return token_pair

    async def refresh(self, refresh_token: str):
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise NotAuthorizedError
        user = await self.user_repo.get_by_id(UUID(user_id))
        token_pair = self.create_access_refresh_token_pait(user)
        return token_pair

    def create_access_refresh_token_pait(self, user: User):
        access_token = self.create_jwt_token({"user_id": str(user.id)}, self.access_token_exp)
        refresh_token = self.create_jwt_token({"user_id": str(user.id)}, self.refresh_token_exp)
        return access_token, refresh_token

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

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

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except DecodeError:
            raise NotAuthorizedError
        except ExpiredSignatureError:
            raise NotAuthorizedError
        return payload

    @staticmethod
    def decode_access_token(token: str) -> AccessTokenPayload:
        payload = AuthService.decode_jwt_token(token)
        return AccessTokenPayload(user_id=UUID(payload["user_id"]))
