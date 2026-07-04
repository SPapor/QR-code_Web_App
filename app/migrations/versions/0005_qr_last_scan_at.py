"""last_scan_at column on qr_code

Revision ID: 0005
Revises: 0004

"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("qr_code", sa.Column("last_scan_at", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("qr_code", "last_scan_at")
