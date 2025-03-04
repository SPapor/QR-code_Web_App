
from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter
from fastapi.responses import Response

from test_user.conftest import user_serializer
from user.services import UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(route_class=DishkaRoute)


@router.post("/register")
async def register(username:str, password:str,session:FromDishka[AsyncSession], user_service: FromDishka[UserService]):
    user, token_pair = await user_service.register(username,password)
    await session.commit()
    return token_pair

@router.post("/login")
async def login(username:str, password:str, user_service: FromDishka[UserService]):
    taken_pair = await user_service.login(username, password)
    return taken_pair

@router.post("/refresh")
async def refresh(refresh_token:str, user_service: FromDishka[UserService]):
    refresh_token, access_token = await user_service.refresh(refresh_token)
    return refresh_token, access_token



