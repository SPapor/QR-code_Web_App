from typing import AsyncIterable, NewType

import sqlalchemy
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

metadata = sqlalchemy.MetaData()

DatabaseUrl = NewType("DatabaseUrl", str)


class ConnectionProvider(Provider):
    def __init__(self, uri):
        super().__init__()
        self.uri = uri

    @provide(scope=Scope.APP)
    def db_url(self) -> DatabaseUrl:
        return DatabaseUrl(self.uri)

    @provide(scope=Scope.APP)
    def engine(self, db_url: DatabaseUrl) -> AsyncEngine:
        engine = create_async_engine(str(db_url), echo=False)
        if engine.dialect.name == "sqlite":

            @sqlalchemy.event.listens_for(engine.sync_engine, "connect")
            def set_sqlite_pragmas(dbapi_connection, _connection_record):
                # WAL lets scan redirects write while readers are active;
                # busy_timeout waits out short write locks instead of raising "database is locked"
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA busy_timeout=5000")
                cursor.close()

        return engine

    @provide(scope=Scope.REQUEST)
    async def session(self, engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
        async with AsyncSession(engine) as session:
            yield session


async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
