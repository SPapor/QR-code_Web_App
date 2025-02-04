import uuid

from sqlalchemy import UUID, Column, String, Table

from core.database import metadata

user_table = Table(
    'user',
    metadata,
    Column('id', UUID(as_uuid=True), default=uuid.uuid4, primary_key=True),
    Column('username', String, unique=True),
)
