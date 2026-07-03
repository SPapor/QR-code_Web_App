from pathlib import Path

from alembic import command
from alembic.config import Config

APP_ROOT = Path(__file__).resolve().parent.parent


def upgrade_database() -> None:
    """Apply pending alembic migrations up to head.

    Synchronous: alembic drives the async engine through asyncio.run inside
    migrations/env.py, so this must be called from a thread without a running
    event loop (e.g. via asyncio.to_thread).
    """
    cfg = Config(str(APP_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(APP_ROOT / "migrations"))
    command.upgrade(cfg, "head")
