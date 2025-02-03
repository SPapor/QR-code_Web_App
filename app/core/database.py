from typing import AsyncIterable, NewType

import databases
import sqlalchemy
from databases import Database
from dishka import Provider, Scope, provide

metadata = sqlalchemy.MetaData()

DatabaseUrl = NewType("DatabaseUrl", str)
_Database = NewType("_Database", Database)


class ConnectionProvider(Provider):
    def __init__(self, uri):
        super().__init__()
        self.uri = uri

    @provide(scope=Scope.APP)
    def db_url(self) -> DatabaseUrl:
        return self.uri

    @provide(scope=Scope.APP)
    def _database(self) -> _Database:
        return _Database(databases.Database(self.uri))

    @provide(scope=Scope.APP)
    async def database(self, db: _Database) -> AsyncIterable[Database]:
        await db.connect()
        yield db
        await db.disconnect()


def create_tables(db_url: DatabaseUrl):
    engine = sqlalchemy.create_engine(db_url, connect_args={"check_same_thread": False})
    metadata.create_all(engine)
