"""composite index on scan_event (qr_code_id, ts) for stats and pruning

Revision ID: 0007
Revises: 0006

"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(op.f("ix_scan_event_qr_code_id"), table_name="scan_event")
    op.create_index("ix_scan_event_qr_code_id_ts", "scan_event", ["qr_code_id", "ts"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scan_event_qr_code_id_ts", table_name="scan_event")
    op.create_index(op.f("ix_scan_event_qr_code_id"), "scan_event", ["qr_code_id"], unique=False)
