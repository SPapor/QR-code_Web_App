"""scan_event table for per-scan history

Revision ID: 0006
Revises: 0005

"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_event",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("qr_code_id", sa.UUID(), nullable=False),
        sa.Column("ts", sa.BigInteger(), nullable=False),
    )
    op.create_index(op.f("ix_scan_event_qr_code_id"), "scan_event", ["qr_code_id"], unique=False)


def downgrade() -> None:
    op.drop_table("scan_event")
