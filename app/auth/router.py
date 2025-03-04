from datetime import timedelta

from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from core.settings import settings
from user.services import UserService

router = APIRouter(route_class=DishkaRoute)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


@router.post("/register")
async def register(
    username: str, password: str, session: FromDishka[AsyncSession], user_service: FromDishka[UserService]
):
    user, token_pair = await user_service.register(username, password)
    await session.commit()
    return token_pair


@router.post("/login")
async def login(user_service: FromDishka[UserService], form_data: OAuth2PasswordRequestForm = Depends()):
    access_token, refresh_token = await user_service.login(form_data.username, form_data.password)
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    set_refresh_token_cookie(response, refresh_token)
    return response


@router.post("/refresh")
async def refresh(request: Request, user_service: FromDishka[UserService]):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    refresh_token, access_token = await user_service.refresh(refresh_token)
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    set_refresh_token_cookie(response, refresh_token)
    return refresh_token, access_token


def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="auth/refresh",
        max_age=int(timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES).total_seconds()),
    )
    return response
