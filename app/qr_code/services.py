import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import UUID

from PIL import Image

from qr_code.dal import QrCodeRepo, ScanEventRepo
from qr_code.models import QrCode, ScanEvent

# the stats endpoint serves at most 90 days, older per-scan events are dropped
SCAN_EVENT_RETENTION_SECONDS = 90 * 24 * 3600
# pruning on every scan would add a delete to every redirect; once per N scans keeps the table bounded anyway
SCAN_EVENT_PRUNE_EVERY = 100


class QrCodeService:
    def __init__(self, qr_code_repo: QrCodeRepo, scan_event_repo: ScanEventRepo):
        self.qr_code_repo = qr_code_repo
        self.scan_event_repo = scan_event_repo

    async def get_image_by_qr_code_id(self, id: UUID, box_size: int = 10) -> Image.Image:
        qr_code = await self.qr_code_repo.get_by_id(id)
        return qr_code.get_image(box_size=box_size)

    async def get_svg_by_qr_code_id(self, id: UUID) -> bytes:
        qr_code = await self.qr_code_repo.get_by_id(id)
        return qr_code.get_svg()

    async def get_all(self) -> Sequence[QrCode]:
        return await self.qr_code_repo.get_all()

    async def get_all_user_qr_codes(self, user_id: UUID) -> Sequence[QrCode]:
        return await self.qr_code_repo.get_all_user_qr_codes(user_id)

    async def create_qr_code(self, user_id: UUID, name: str, link: str) -> QrCode:
        qr_code = QrCode(user_id=user_id, name=name, link=link)
        return await self.qr_code_repo.create_and_get(qr_code)

    async def delete_qr_code(self, user_id: UUID, qr_code_id: UUID) -> None:
        qr_code = await self.qr_code_repo.get_by_id(qr_code_id)
        if qr_code.user_id != user_id:
            raise QrCode.NotFoundError
        await self.qr_code_repo.delete(qr_code.id)

    async def get_by_id(self, id: UUID) -> QrCode:
        return await self.qr_code_repo.get_by_id(id)

    async def register_scan(self, id: UUID) -> QrCode:
        qr_code = await self.qr_code_repo.get_by_id(id)
        now = int(time.time())
        await self.qr_code_repo.increment_scan_count(id, now)
        await self.scan_event_repo.create(ScanEvent(qr_code_id=id, ts=now))
        if qr_code.scan_count % SCAN_EVENT_PRUNE_EVERY == 0:
            await self.scan_event_repo.delete_older_than(id, now - SCAN_EVENT_RETENTION_SECONDS)
        return qr_code

    async def get_scan_stats(self, user_id: UUID, qr_code_id: UUID, days: int = 30) -> dict:
        qr_code = await self.qr_code_repo.get_by_id(qr_code_id)
        if qr_code.user_id != user_id:
            raise QrCode.NotFoundError

        today = datetime.now(timezone.utc).date()
        first_day = today - timedelta(days=days - 1)
        since = int(datetime(first_day.year, first_day.month, first_day.day, tzinfo=timezone.utc).timestamp())
        timestamps = await self.scan_event_repo.get_ts_since(qr_code_id, since)
        by_day = Counter(datetime.fromtimestamp(ts, tz=timezone.utc).date() for ts in timestamps)
        day_range = (first_day + timedelta(days=i) for i in range(days))
        return {
            "days": [{"date": day.isoformat(), "count": by_day.get(day, 0)} for day in day_range],
            "total": qr_code.scan_count,
            "last_scan_at": qr_code.last_scan_at,
        }

    async def update_qr_code(self, user_id: UUID, qr_code_id: UUID, name: str, link: str) -> QrCode:
        qr_code = await self.qr_code_repo.get_by_id(qr_code_id)
        if qr_code.user_id != user_id:
            raise QrCode.NotFoundError
        qr_code.link = link
        qr_code.name = name
        return await self.qr_code_repo.update_and_get(qr_code)
