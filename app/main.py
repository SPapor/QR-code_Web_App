import asyncio
import functools
from contextlib import asynccontextmanager, suppress

from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

import auth.api_errors
import auth.errors
import core.api_errors
import core.errors
import google_auth.api_errors
import qr_code.api_errors
import telegram_auth.api_errors
import user.api_errors
from auth.providers import AuthProvider
from auth.router import router as auth_router
from core.database import ConnectionProvider
from core.migrations import upgrade_database
from core.providers import DataclassSerializerProvider
from core.settings import settings
from google_auth.providers import GoogleAuthProvider
from google_auth.router import router as google_auth_router
from qr_code.providers import QrCodeProvider
from qr_code.router import router as qr_code_router
from telegram_auth.providers import TelegramAuthProvider
from telegram_auth.router import public_router as telegram_auth_public_router
from telegram_auth.router import router as telegram_auth_router
from user.models import User
from user.providers import UserProvider
from user.router import router as user_router
from user.services import UserService


@asynccontextmanager
async def lifespan(app: FastAPI, container: AsyncContainer):
    await asyncio.to_thread(upgrade_database)
    async with container(scope=Scope.REQUEST) as request_container:
        user_service = await request_container.get(UserService)
        session = await request_container.get(AsyncSession)

        if settings.ADMIN_USERNAME is not None and settings.ADMIN_PASSWORD is not None:
            with suppress(User.AlreadyExistError):
                await user_service.register(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD)

        await session.commit()

    yield
    await container.close()


# noinspection PyShadowingNames
def create_app():
    app = FastAPI(lifespan=functools.partial(lifespan, container=container))

    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(qr_code_router, prefix="/qr_code")
    app.include_router(auth_router, prefix="/auth")
    app.include_router(user_router, prefix="/user")
    app.include_router(telegram_auth_router, prefix="/auth/telegram")
    app.include_router(telegram_auth_public_router, prefix="/auth/telegram")
    app.include_router(google_auth_router, prefix="/auth/google")

    auth.api_errors.register_exception_handlers(app)
    user.api_errors.register_exception_handlers(app)
    qr_code.api_errors.register_exception_handlers(app)
    telegram_auth.api_errors.register_exception_handlers(app)
    google_auth.api_errors.register_exception_handlers(app)
    core.api_errors.register_exception_handlers(app)
    return app


container = make_async_container(
    ConnectionProvider(settings.DB_URI),
    DataclassSerializerProvider(),
    UserProvider(),
    AuthProvider(),
    QrCodeProvider(),
    TelegramAuthProvider(),
    GoogleAuthProvider(),
)
app = create_app()
setup_dishka(container=container, app=app)
