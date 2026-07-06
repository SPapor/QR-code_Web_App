from sqlalchemy import UUID, BigInteger, Column, ForeignKey, Index, String, Table

from core.database import metadata

qr_code_table = Table(
    'qr_code',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True),
    Column("name", String, nullable=False),
    Column("link", String, nullable=False),
    Column("scan_count", BigInteger, nullable=False, server_default="0"),
    Column("last_scan_at", BigInteger, nullable=True),
    Column("fill_color", String, nullable=False, server_default="#000000"),
    # gradient end color; solid fill when NULL
    Column("fill_color2", String, nullable=True),
    Column("back_color", String, nullable=False, server_default="#ffffff"),
    Column("style", String, nullable=False, server_default="square"),
)

scan_event_table = Table(
    'scan_event',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('qr_code_id', UUID(as_uuid=True), nullable=False),
    Column('ts', BigInteger, nullable=False),
    # covers both the stats range query and retention pruning
    Index('ix_scan_event_qr_code_id_ts', 'qr_code_id', 'ts'),
)
