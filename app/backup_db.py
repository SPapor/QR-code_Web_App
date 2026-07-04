"""Periodic sqlite backup with rotation and optional offsite copy to Telegram.

Uses the sqlite online backup API, so it is safe to run against a live database.
Run once (default) or in a loop with --interval; old backups beyond --keep are deleted.
If BOT_TOKEN and BACKUP_TELEGRAM_CHAT_ID env vars are set, each snapshot is also
sent as a document to that Telegram chat (files persist in Telegram's cloud).
"""

import argparse
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("backup_db")

BACKUP_GLOB = "database-*.sqlite"


def backup_once(db_path: Path, backup_dir: Path, keep: int) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / f"database-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}.sqlite"

    source = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=30)
    try:
        target = sqlite3.connect(dest)
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()

    for old in sorted(backup_dir.glob(BACKUP_GLOB))[:-keep]:
        old.unlink()
    return dest


def send_to_telegram(backup: Path, bot_token: str, chat_id: str) -> None:
    import httpx  # only needed when the offsite copy is enabled

    with backup.open("rb") as f:
        response = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
            data={"chat_id": chat_id, "caption": "qr-menu db backup", "disable_notification": True},
            files={"document": (backup.name, f, "application/octet-stream")},
            timeout=60,
        )
    response.raise_for_status()
    if not response.json().get("ok"):
        raise RuntimeError(f"telegram sendDocument failed: {response.text[:200]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("database.sqlite"), help="path to the sqlite database")
    parser.add_argument("--dir", type=Path, default=Path("backups"), help="directory to store backups in")
    parser.add_argument("--keep", type=int, default=14, help="number of backups to keep")
    parser.add_argument("--interval", type=int, default=None, help="seconds between backups; omit to run once")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # httpx logs full request URLs at INFO, which would leak the bot token into container logs
    logging.getLogger("httpx").setLevel(logging.WARNING)

    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("BACKUP_TELEGRAM_CHAT_ID")
    if not (bot_token and chat_id):
        logger.info("offsite copy disabled: set BOT_TOKEN and BACKUP_TELEGRAM_CHAT_ID to enable it")

    while True:
        try:
            dest = backup_once(args.db, args.dir, args.keep)
            logger.info("backed up %s -> %s", args.db, dest)
            if bot_token and chat_id:
                send_to_telegram(dest, bot_token, chat_id)
                logger.info("sent %s to telegram chat", dest.name)
        except Exception:
            logger.exception("backup of %s failed", args.db)
            if args.interval is None:
                raise
        if args.interval is None:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
