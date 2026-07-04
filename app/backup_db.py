"""Periodic sqlite backup with rotation.

Uses the sqlite online backup API, so it is safe to run against a live database.
Run once (default) or in a loop with --interval; old backups beyond --keep are deleted.
"""

import argparse
import logging
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("database.sqlite"), help="path to the sqlite database")
    parser.add_argument("--dir", type=Path, default=Path("backups"), help="directory to store backups in")
    parser.add_argument("--keep", type=int, default=14, help="number of backups to keep")
    parser.add_argument("--interval", type=int, default=None, help="seconds between backups; omit to run once")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    while True:
        try:
            dest = backup_once(args.db, args.dir, args.keep)
            logger.info("backed up %s -> %s", args.db, dest)
        except Exception:
            logger.exception("backup of %s failed", args.db)
            if args.interval is None:
                raise
        if args.interval is None:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
