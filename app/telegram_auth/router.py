import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse

from auth.dependencies import logged_in_user_id
from auth.router import set_refresh_cookie, token_pair_to_response
from core.dependencies import auto_commit
from core.settings import settings
from telegram_auth.dependencies import require_bot_secret
from telegram_auth.errors import TelegramAuthError
from telegram_auth.services import LINK_CODE_TTL_SECONDS, TelegramAuthService

logger = logging.getLogger(__name__)

router = APIRouter(route_class=DishkaRoute, dependencies=[Depends(require_bot_secret)])
# widget callback and link-code issuing are called by browsers, not by the bot
public_router = APIRouter(route_class=DishkaRoute)


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


@router.post("/link_by_code")
async def link_by_code(
    telegram_id: Annotated[int, Body()],
    code: Annotated[str, Body()],
    telegram_auth_service: FromDishka[TelegramAuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    access_token, refresh_token = await telegram_auth_service.link_by_code(telegram_id, code)
    return token_pair_to_response(access_token, refresh_token)


@public_router.get("/callback")
async def widget_callback(
    request: Request,
    telegram_auth_service: FromDishka[TelegramAuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    try:
        access_token, refresh_token = await telegram_auth_service.login_via_widget(dict(request.query_params))
    except TelegramAuthError as e:
        logger.warning("telegram widget callback failed: %s", type(e).__name__)
        return RedirectResponse(url="/?oauth=error")
    response = RedirectResponse(url="/?oauth=ok")
    set_refresh_cookie(response, refresh_token)
    return response


@public_router.post("/link_code")
async def create_link_code(
    telegram_auth_service: FromDishka[TelegramAuthService],
    user_id: UUID = Depends(logged_in_user_id),
    _session: AsyncSession = Depends(auto_commit),
):
    code = await telegram_auth_service.create_link_code(user_id)
    return {"code": code, "expires_in": LINK_CODE_TTL_SECONDS, "bot_username": settings.BOT_USERNAME}
