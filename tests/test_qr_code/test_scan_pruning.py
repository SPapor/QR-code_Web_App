import time
import uuid

import pytest_asyncio

from qr_code.models import QrCode, ScanEvent
from qr_code.services import SCAN_EVENT_RETENTION_SECONDS, QrCodeService


@pytest_asyncio.fixture
async def qr_code_service(request_container) -> QrCodeService:
    return await request_container.get(QrCodeService)


async def test_register_scan_prunes_events_older_than_retention(qr_code_service):
    qr_code = await qr_code_service.qr_code_repo.create_and_get(
        QrCode(user_id=uuid.uuid4(), name='test', link='https://example.com')
    )
    now = int(time.time())
    old_ts = now - SCAN_EVENT_RETENTION_SECONDS - 60
    fresh_ts = now - 60
    await qr_code_service.scan_event_repo.create(ScanEvent(qr_code_id=qr_code.id, ts=old_ts))
    await qr_code_service.scan_event_repo.create(ScanEvent(qr_code_id=qr_code.id, ts=fresh_ts))

    await qr_code_service.register_scan(qr_code.id)

    timestamps = await qr_code_service.scan_event_repo.get_ts_since(qr_code.id, 0)
    assert old_ts not in timestamps
    assert fresh_ts in timestamps
    assert len(timestamps) == 2  # the fresh pre-existing event + the scan itself
