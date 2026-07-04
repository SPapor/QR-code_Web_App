from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse

from auth.router import set_refresh_cookie
from core.dependencies import auto_commit
from google_auth.errors import GoogleAuthError
from google_auth.services import GoogleAuthService

router = APIRouter(route_class=DishkaRoute)


@router.get("/login")
async def google_login(google_auth_service: FromDishka[GoogleAuthService]):
    return RedirectResponse(url=google_auth_service.build_auth_url())


@router.get("/callback")
async def google_callback(
    request: Request,
    google_auth_service: FromDishka[GoogleAuthService],
    _session: AsyncSession = Depends(auto_commit),
):
    params = request.query_params
    if params.get("error") or not params.get("code"):
        return RedirectResponse(url="/?oauth=error")
    try:
        google_auth_service.verify_state(params.get("state"))
        access_token, refresh_token = await google_auth_service.login_with_code(params["code"])
    except GoogleAuthError:
        return RedirectResponse(url="/?oauth=error")
    response = RedirectResponse(url="/?oauth=ok")
    set_refresh_cookie(response, refresh_token)
    return response
