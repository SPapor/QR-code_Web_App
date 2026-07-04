"""refresh_session table for revocable, single-use refresh tokens

Revision ID: 0003
Revises: 0002

"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_session",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("auth_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
    )
    op.create_index(op.f("ix_refresh_session_auth_id"), "refresh_session", ["auth_id"], unique=False)


def downgrade() -> None:
    op.drop_table("refresh_session")
