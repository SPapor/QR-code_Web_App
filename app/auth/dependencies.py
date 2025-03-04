from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import DecodeError
from starlette.requests import Request

from core.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def access_token_payload(request: Request, token: str = Depends(oauth2_scheme)):
    print(request.headers)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except DecodeError:
        raise ValueError("Access token is not valid")

    user_id = payload.get("user_id")
    if user_id is None:
        raise ValueError("Access token is not valid")
    return payload


def logged_in_user_id(payload: dict = Depends(access_token_payload)) -> UUID:
    return UUID(payload["user_id"])
