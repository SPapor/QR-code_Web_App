from sqlalchemy import Column, Table, UUID, String, Boolean

from core.database import metadata

auth_table = Table(
    "auth",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("user_id", UUID, index=True),
    Column("username", String, unique=True, index=True),
    Column("password_hash", String),
    Column("is_admin", Boolean),
)
