from contextlib import asynccontextmanager

from dishka import make_async_container, Scope
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

import auth.errors
import core.errors
import user.errors
from auth.providers import AuthProvider
from auth.router import router as auth_router
from auth.services import AuthService
from core.database import ConnectionProvider, create_tables
from core.providers import DataclassSerializerProvider
from core.settings import settings
from qr_code.providers import QrCodeProvider
from qr_code.router import router as qr_code_router
from user.models import User
from user.providers import UserProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables(await container.get(AsyncEngine))

    if settings.ADMIN_USERNAME is not None and settings.ADMIN_PASSWORD is not None:
        async with container(scope=Scope.REQUEST) as request_container:
            auth_service = await request_container.get(AuthService)
            session = await request_container.get(AsyncSession)
            try:
                await auth_service.register(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD)
            except User.AlreadyExistError:
                pass
            else:
                await session.commit()

    yield
    await container.close()


app = FastAPI(lifespan=lifespan)

container = make_async_container(
    ConnectionProvider(f"sqlite+aiosqlite:///./{settings.db_name}"),
    DataclassSerializerProvider(),
    UserProvider(),
    AuthProvider(),
    QrCodeProvider(),
)
setup_dishka(container=container, app=app)
app.include_router(qr_code_router, prefix="/qr_code")
app.include_router(auth_router, prefix="/auth")

auth.errors.register_exception_handlers(app)
core.errors.register_exception_handlers(app)
user.errors.register_exception_handlers(app)
