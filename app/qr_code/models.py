import uuid
from dataclasses import dataclass, field
from uuid import UUID
import qrcode
from PIL import Image

@dataclass(kw_only=True)
class QrCode:
    id: UUID = field(default_factory=uuid.uuid4)
    user_id: UUID
    name: str
    link: str

    def get_image(self) -> Image.Image:
        qr = qrcode.main.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(self.link)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        return img
