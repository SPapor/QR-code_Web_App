from sqlalchemy import UUID, BigInteger, Column, ForeignKey, String, Table

from core.database import metadata

telegram_link_table = Table(
    "telegram_link",
    metadata,
    Column("telegram_id", BigInteger, primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, unique=True, index=True),
)

telegram_link_code_table = Table(
    "telegram_link_code",
    metadata,
    Column("code", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), nullable=False),
    Column("expires_at", BigInteger, nullable=False),
)
