"""qr style columns: colors, gradient and module shape

Revision ID: 0008
Revises: 0007

"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("qr_code", schema=None) as batch_op:
        batch_op.add_column(sa.Column("fill_color", sa.String(), server_default="#000000", nullable=False))
        batch_op.add_column(sa.Column("fill_color2", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("back_color", sa.String(), server_default="#ffffff", nullable=False))
        batch_op.add_column(sa.Column("style", sa.String(), server_default="square", nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("qr_code", schema=None) as batch_op:
        batch_op.drop_column("style")
        batch_op.drop_column("back_color")
        batch_op.drop_column("fill_color2")
        batch_op.drop_column("fill_color")
