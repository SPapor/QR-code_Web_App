from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from core.settings import settings
from user.models import User

db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def register(username: str, password: str):
    password_hash = get_password_hash(password)
    user = User(username=username, password_hash=password_hash)
    db[str(user.id)] = user

    access_token = create_jwt_token({"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(
        {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return access_token, refresh_token


def login(username: str, password: str):
    for user in db.values():
        if user.username == username:
            break
    else:
        raise ValueError("User not found")
    is_authorized = verify_password(password, user.password_hash)
    if not is_authorized:
        raise ValueError("Not authorized")

    access_token = create_jwt_token({"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(
        {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return access_token, refresh_token


def refresh(refresh_token: str):
    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_id = payload.get("user_id")
    if user_id is None:
        raise ValueError("Refresh token is not valid")
    user = db[user_id]
    access_token = create_jwt_token({"user_id": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(
        {"user_id": str(user.id)}, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return access_token, refresh_token


def decode_access_token(access_token: str):
    payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_id = payload.get("user_id")
    if user_id is None:
        raise ValueError("Access token is not authenticated")
    return payload


def create_jwt_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


#
# register("asdasda","owei234")
# access_token,refresh_token = login("asdasda","owei234")
# print(decode_access_token(access_token))
# time.sleep(61)
# print(decode_access_token(access_token))
# access_token,refresh_token = refresh(refresh_token)
