import asyncio
import dataclasses
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt
from fastapi.encoders import jsonable_encoder

from auth.dal import AuthRepo, RefreshSessionRepo
from auth.errors import InvalidLoginOrPasswordError, NotAuthorizedError, RefreshTokenRequiredError
from auth.models import Auth, RefreshSession
from core.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AccessTokenPayload:
    user_id: UUID
    username: str
    is_admin: bool = False
    token_type: str = "access"


class AuthService:
    def __init__(self, auth_repo: AuthRepo, refresh_session_repo: RefreshSessionRepo):
        self.auth_repo = auth_repo
        self.refresh_session_repo = refresh_session_repo

    async def create_auth(self, user_id: UUID, username: str, password: str) -> Auth:
        # bcrypt takes ~100ms of pure CPU; keep it off the event loop
        password_hash = await asyncio.to_thread(self.get_password_hash, password)
        auth = Auth(user_id=user_id, username=username, password_hash=password_hash)
        auth = await self.auth_repo.create_and_get(auth)
        return auth

    async def login(self, username: str, password: str):
        try:
            user = await self.auth_repo.get_by_username(username)
        except Auth.NotFoundError:
            logger.info("login failed for username=%r: unknown username", username)
            raise InvalidLoginOrPasswordError

        if not await asyncio.to_thread(self.verify_password, password, user.password_hash):
            logger.info("login failed for username=%r: wrong password", username)
            raise InvalidLoginOrPasswordError

        logger.info("login ok for username=%r", username)
        token_pair = await self.issue_token_pair(user)
        return token_pair

    async def refresh(self, refresh_token: str | None):
        if not refresh_token:
            raise RefreshTokenRequiredError
        payload = self.decode_jwt_token(refresh_token)
        if payload.get("token_type") != "refresh":
            raise NotAuthorizedError
        jti = payload.get("jti")
        if jti is None:
            # pre-rotation token without a session id: force re-login
            raise NotAuthorizedError

        try:
            session = await self.refresh_session_repo.get_by_id(UUID(jti))
        except (ValueError, RefreshSession.NotFoundError):
            logger.info("refresh rejected: unknown session jti=%s", jti)
            raise NotAuthorizedError
        # rotation: each refresh token is single-use
        await self.refresh_session_repo.delete(session.id)
        now = int(time.time())
        if session.expires_at < now:
            raise NotAuthorizedError
        await self.refresh_session_repo.delete_expired(now)

        try:
            auth = await self.auth_repo.get_by_id(session.auth_id)
        except Auth.NotFoundError:
            raise NotAuthorizedError
        token_pair = await self.issue_token_pair(auth)
        return token_pair

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        try:
            payload = self.decode_jwt_token(refresh_token)
        except NotAuthorizedError:
            return
        jti = payload.get("jti")
        if payload.get("token_type") != "refresh" or jti is None:
            return
        try:
            await self.refresh_session_repo.delete(UUID(jti))
        except ValueError:
            return
        logger.info("logout: revoked session jti=%s", jti)

    async def issue_token_pair(self, auth: Auth) -> tuple[str, str]:
        access_token_exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = AccessTokenPayload(user_id=auth.user_id, username=auth.username, is_admin=auth.is_admin)
        at_payload = dataclasses.asdict(payload)  # noqa
        access_token = self.create_jwt_token(jsonable_encoder(at_payload), access_token_exp)

        refresh_token_exp = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        session = RefreshSession(auth_id=auth.id, expires_at=int(time.time() + refresh_token_exp.total_seconds()))
        await self.refresh_session_repo.create(session)
        refresh_token_payload = {"id": str(auth.id), "jti": str(session.id), 'token_type': 'refresh'}
        refresh_token = self.create_jwt_token(refresh_token_payload, refresh_token_exp)
        return access_token, refresh_token

    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
        except ValueError:
            return False

    @staticmethod
    def get_password_hash(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

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
        except jwt.PyJWTError:
            raise NotAuthorizedError
        return payload

    @staticmethod
    def decode_access_token(token: str) -> AccessTokenPayload:
        payload = AuthService.decode_jwt_token(token)
        if payload.get("token_type") != "access":
            raise NotAuthorizedError
        return AccessTokenPayload(
            user_id=UUID(payload["user_id"]),
            username=payload["username"],
            is_admin=payload.get("is_admin", False),
        )
