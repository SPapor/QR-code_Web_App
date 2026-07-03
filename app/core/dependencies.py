from dishka.integrations.fastapi import FromDishka, inject
from sqlalchemy.ext.asyncio import AsyncSession


@inject
async def auto_commit(session: FromDishka[AsyncSession]):
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
