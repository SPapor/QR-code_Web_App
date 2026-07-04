from sqlalchemy import UUID, Column, ForeignKey, String, Table

from core.database import metadata

google_link_table = Table(
    "google_link",
    metadata,
    Column("google_sub", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, unique=True, index=True),
    Column("email", String, nullable=False),
)
