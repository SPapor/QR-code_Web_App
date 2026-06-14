from dishka.integrations.fastapi import inject, FromDishka
from sqlalchemy.ext.asyncio import AsyncSession


@inject
async def auto_commit(session: FromDishka[AsyncSession]):
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
