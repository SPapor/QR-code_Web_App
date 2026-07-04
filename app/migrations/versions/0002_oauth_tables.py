"""oauth tables: telegram_link_code, google_link

Revision ID: 0002
Revises: 0001

"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_link_code",
        sa.Column("code", sa.String(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "google_link",
        sa.Column("google_sub", sa.String(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
    )
    op.create_index(op.f("ix_google_link_user_id"), "google_link", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("google_link")
    op.drop_table("telegram_link_code")
