import time
import uuid

import pytest_asyncio

from qr_code.models import QrCode, ScanEvent
from qr_code.services import SCAN_EVENT_PRUNE_EVERY, SCAN_EVENT_RETENTION_SECONDS, QrCodeService


@pytest_asyncio.fixture
async def qr_code_service(request_container) -> QrCodeService:
    return await request_container.get(QrCodeService)


async def _make_qr_code_with_events(qr_code_service, scan_count):
    qr_code = await qr_code_service.qr_code_repo.create_and_get(
        QrCode(user_id=uuid.uuid4(), name='test', link='https://example.com', scan_count=scan_count)
    )
    now = int(time.time())
    old_ts = now - SCAN_EVENT_RETENTION_SECONDS - 60
    fresh_ts = now - 60
    await qr_code_service.scan_event_repo.create(ScanEvent(qr_code_id=qr_code.id, ts=old_ts))
    await qr_code_service.scan_event_repo.create(ScanEvent(qr_code_id=qr_code.id, ts=fresh_ts))
    return qr_code, old_ts, fresh_ts


async def test_register_scan_prunes_events_older_than_retention(qr_code_service):
    # scan_count is a multiple of the prune period (0), so this scan triggers pruning
    qr_code, old_ts, fresh_ts = await _make_qr_code_with_events(qr_code_service, scan_count=0)

    await qr_code_service.register_scan(qr_code.id)

    timestamps = await qr_code_service.scan_event_repo.get_ts_since(qr_code.id, 0)
    assert old_ts not in timestamps
    assert fresh_ts in timestamps
    assert len(timestamps) == 2  # the fresh pre-existing event + the scan itself


async def test_register_scan_skips_pruning_between_periods(qr_code_service):
    qr_code, old_ts, fresh_ts = await _make_qr_code_with_events(qr_code_service, scan_count=SCAN_EVENT_PRUNE_EVERY + 1)

    await qr_code_service.register_scan(qr_code.id)

    timestamps = await qr_code_service.scan_event_repo.get_ts_since(qr_code.id, 0)
    assert old_ts in timestamps  # not pruned on off-period scans
    assert len(timestamps) == 3
