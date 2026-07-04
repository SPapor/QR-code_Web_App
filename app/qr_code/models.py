import uuid
from dataclasses import dataclass, field
from uuid import UUID

import qrcode
import qrcode.image.svg
from PIL import Image

from core.models import Model
from core.settings import settings


@dataclass(kw_only=True)
class QrCode(Model):
    id: UUID = field(default_factory=uuid.uuid4)
    user_id: UUID
    name: str
    link: str
    scan_count: int = 0
    last_scan_at: int | None = None

    def public_url(self) -> str:
        return settings.API_SCHEME + "://" + settings.API_URL + settings.QR_CODE_ENDPOINT.format(uuid=self.id)

    def get_image(self, box_size: int = 10) -> Image.Image:
        qr = qrcode.main.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=4,
        )
        qr.add_data(self.public_url())
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        return img

    def get_svg(self) -> bytes:
        qr = qrcode.main.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            border=4,
            image_factory=qrcode.image.svg.SvgPathFillImage,
        )
        qr.add_data(self.public_url())
        qr.make(fit=True)
        return qr.make_image().to_string()


@dataclass(kw_only=True)
class ScanEvent(Model):
    id: UUID = field(default_factory=uuid.uuid4)
    qr_code_id: UUID
    ts: int
