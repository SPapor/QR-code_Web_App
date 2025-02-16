import asyncio

from dishka import make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from core.database import ConnectionProvider, create_tables
from core.providers import DataclassSerializerProvider
from core.settings import settings
from qr_code.dal import QrCodeRepo
from qr_code.models import QrCode
from qr_code.providers import QrCodeProvider
from user.dal import UserRepo
from user.models import User
from user.providers import UserProvider


def get_container():
    return make_async_container(
        ConnectionProvider(f"sqlite+aiosqlite:///./{settings.db_name}"),
        DataclassSerializerProvider(),
        UserProvider(),
        QrCodeProvider(),
    )


async def main():
    container = get_container()
    await create_tables(await container.get(AsyncEngine))
    async with container() as request_container:
        user_repo = await request_container.get(UserRepo)
        qr_code_repo = await request_container.get(QrCodeRepo)
        session = await request_container.get(AsyncSession)
        user = User(username="Batman")
        qr_code = QrCode(user_id=user.id, name="Batman", link="https://coub.com/view/d4rmv")
        await user_repo.create(user)
        await qr_code_repo.create(qr_code)
        await session.commit()

if __name__ == '__main__':
    asyncio.run(main())
