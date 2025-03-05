import asyncio
from contextlib import asynccontextmanager

from dishka import make_async_container
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
from qr_code.dal import QrCodeRepo
from qr_code.providers import QrCodeProvider
from qr_code.router import router as qr_code_router
from user.dal import UserRepo
from user.models import User
from user.providers import UserProvider

app = FastAPI()

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await container.close()


async def main():
    await create_tables(await container.get(AsyncEngine))
    async with container() as request_container:
        user_repo = await request_container.get(UserRepo)
        await request_container.get(QrCodeRepo)
        await request_container.get(AsyncSession)

        password_hash = AuthService.get_password_hash('asd')
        user = User(username="Batman", password_hash=password_hash)
        await user_repo.create(user)
        # qr_code = QrCode(user_id=user.id, name="Batman", link="https://coub.com/view/d4rmv")
        # await user_repo.create(user)
        # await qr_code_repo.create(qr_code)
        # await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
