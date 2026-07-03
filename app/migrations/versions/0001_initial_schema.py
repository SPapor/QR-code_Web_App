"""initial schema: user, auth, qr_code, telegram_link

Adopts pre-alembic databases: tables created earlier by metadata.create_all
are detected and left untouched, only the alembic version gets stamped.

Revision ID: 0001
Revises:

"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing = sa.inspect(op.get_bind()).get_table_names()

    if "user" not in existing:
        op.create_table(
            "user",
            sa.Column("id", sa.UUID(), primary_key=True),
            sa.Column("username", sa.String(), nullable=False, unique=True),
        )

    if "auth" not in existing:
        op.create_table(
            "auth",
            sa.Column("id", sa.UUID(), primary_key=True),
            sa.Column("user_id", sa.UUID()),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("password_hash", sa.String(), nullable=False),
            sa.Column("is_admin", sa.Boolean(), nullable=False),
        )
        op.create_index(op.f("ix_auth_user_id"), "auth", ["user_id"])
        op.create_index(op.f("ix_auth_username"), "auth", ["username"], unique=True)

    if "qr_code" not in existing:
        op.create_table(
            "qr_code",
            sa.Column("id", sa.UUID(), primary_key=True),
            sa.Column("user_id", sa.UUID(), sa.ForeignKey("user.id"), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("link", sa.String(), nullable=False),
        )
        op.create_index(op.f("ix_qr_code_user_id"), "qr_code", ["user_id"])

    if "telegram_link" not in existing:
        op.create_table(
            "telegram_link",
            sa.Column("telegram_id", sa.BigInteger(), primary_key=True),
            sa.Column("user_id", sa.UUID(), sa.ForeignKey("user.id"), nullable=False),
        )
        op.create_index(op.f("ix_telegram_link_user_id"), "telegram_link", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("telegram_link")
    op.drop_table("qr_code")
    op.drop_table("auth")
    op.drop_table("user")
