import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_select_1(database):
    assert await database.fetch_val(select(1)) == 1
