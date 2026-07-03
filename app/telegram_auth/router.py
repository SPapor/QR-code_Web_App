from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.router import token_pair_to_response
from core.dependencies import auto_commit
from telegram_auth.dependencies import require_bot_secret
from telegram_auth.services import TelegramAuthService

router = APIRouter(route_class=DishkaRoute, dependencies=[Depends(require_bot_secret)])


@router.post("/exchange")
async def exchange(
    telegram_id: Annotated[int, Body(embed=True)],
    telegram_auth_service: FromDishka[TelegramAuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    access_token, refresh_token = await telegram_auth_service.exchange(telegram_id)
    return token_pair_to_response(access_token, refresh_token)


@router.post("/link")
async def link(
    telegram_id: Annotated[int, Body()],
    username: Annotated[str, Body()],
    password: Annotated[str, Body()],
    telegram_auth_service: FromDishka[TelegramAuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    access_token, refresh_token = await telegram_auth_service.link(telegram_id, username, password)
    return token_pair_to_response(access_token, refresh_token)
