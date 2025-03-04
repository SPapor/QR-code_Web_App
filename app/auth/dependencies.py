from uuid import UUID

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from jwt.exceptions import DecodeError
from core.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def access_token_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except DecodeError:
            raise ValueError("Refresh token is not valid")

    user_id = payload.get("user_id")
    if user_id is None:
        raise ValueError("Refresh token is not valid")
    return payload

def logged_in_user_id(payload:dict = Depends(access_token_payload))->UUID:
    return UUID(payload["user_id"])