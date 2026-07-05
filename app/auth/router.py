from datetime import timedelta
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from auth.dependencies import access_token_payload
from auth.errors import InvalidCurrentPasswordError, InvalidLoginOrPasswordError
from auth.rate_limit import LoginRateLimiter
from auth.services import AccessTokenPayload, AuthService
from core.dependencies import auto_commit
from core.settings import settings

router = APIRouter(route_class=DishkaRoute)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/login")
async def login(
    request: Request,
    auth_service: FromDishka[AuthService],
    rate_limiter: FromDishka[LoginRateLimiter],
    session: FromDishka[AsyncSession],
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    rate_limit_key = f"{client_ip(request)}:{form_data.username}"
    rate_limiter.check(rate_limit_key)
    try:
        access_token, refresh_token = await auth_service.login(form_data.username, form_data.password)
    except InvalidLoginOrPasswordError:
        rate_limiter.record(rate_limit_key)
        raise
    rate_limiter.reset(rate_limit_key)
    # commit only on success: a failed login has nothing to persist
    await session.commit()
    return token_pair_to_response(access_token, refresh_token)


@router.post("/refresh")
async def refresh(
    request: Request,
    auth_service: FromDishka[AuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    refresh_token = request.cookies.get("refresh_token")
    access_token, refresh_token = await auth_service.refresh(refresh_token)
    return token_pair_to_response(access_token, refresh_token)


@router.post("/change_password")
async def change_password(
    old_password: Annotated[str, Body()],
    new_password: Annotated[str, Body(min_length=8, max_length=128)],
    auth_service: FromDishka[AuthService],
    rate_limiter: FromDishka[LoginRateLimiter],
    payload: AccessTokenPayload = Depends(access_token_payload),
    _session: AsyncSession = Depends(auto_commit),
):
    # a stolen access token must not allow brute-forcing the current password
    rate_limit_key = f"pw:{payload.user_id}"
    rate_limiter.check(rate_limit_key)
    try:
        access_token, refresh_token = await auth_service.change_password(payload.user_id, old_password, new_password)
    except InvalidCurrentPasswordError:
        rate_limiter.record(rate_limit_key)
        raise
    rate_limiter.reset(rate_limit_key)
    return token_pair_to_response(access_token, refresh_token)


@router.post("/logout")
async def logout(
    request: Request,
    auth_service: FromDishka[AuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    await auth_service.logout(request.cookies.get("refresh_token"))
    response = Response(status_code=204)
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return response


@router.get("/config")
async def auth_config():
    telegram_login = bool(settings.BOT_TOKEN and settings.BOT_USERNAME)
    return {
        "telegram_login": telegram_login,
        "telegram_bot_username": settings.BOT_USERNAME if telegram_login else None,
        "google_login": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
    }


def client_ip(request: Request) -> str:
    # X-Real-IP is set by our nginx and cannot be spoofed as long as the backend
    # port is not published; the client-controlled X-Forwarded-For is not trusted
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
        max_age=int(timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES).total_seconds()),
    )


def token_pair_to_response(access_token: str, refresh_token: str):
    response = JSONResponse(
        content={
            'access_token': access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    )
    set_refresh_cookie(response, refresh_token)
    return response
