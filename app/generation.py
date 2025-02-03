from typing import Any

import qrcode
from PIL import Image


def generator_qrcode(link_id: Any) -> Image.Image:
    qr = qrcode.main.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(link_id)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    return img
