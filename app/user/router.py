from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from auth.dependencies import access_token_payload
from auth.rate_limit import RegisterRateLimiter
from auth.router import client_ip, token_pair_to_response
from auth.services import AccessTokenPayload
from core.dependencies import auto_commit
from google_auth.dal import GoogleLinkRepo
from telegram_auth.dal import TelegramLinkRepo
from user.services import UserService

router = APIRouter(route_class=DishkaRoute)


@router.get("/me")
async def me(
    telegram_link_repo: FromDishka[TelegramLinkRepo],
    google_link_repo: FromDishka[GoogleLinkRepo],
    payload: AccessTokenPayload = Depends(access_token_payload),
):
    telegram_link = await telegram_link_repo.get_by_user_id(payload.user_id)
    google_link = await google_link_repo.get_by_user_id(payload.user_id)
    return {
        "username": payload.username,
        "telegram_linked": telegram_link is not None,
        "google_linked": google_link is not None,
    }


@router.post("/register")
async def register(
    request: Request,
    username: Annotated[str, Body(min_length=3, max_length=64, pattern=r"^\S+$")],
    password: Annotated[str, Body(min_length=8, max_length=128)],
    user_service: FromDishka[UserService],
    rate_limiter: FromDishka[RegisterRateLimiter],
    _session: AsyncSession = Depends(auto_commit),
):
    rate_limit_key = client_ip(request)
    rate_limiter.check(rate_limit_key)
    rate_limiter.record(rate_limit_key)
    access_token, refresh_token = await user_service.register(username, password)
    return token_pair_to_response(access_token, refresh_token)
