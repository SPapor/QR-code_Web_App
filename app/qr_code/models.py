import uuid
from dataclasses import dataclass, field
from uuid import UUID

import qrcode
import qrcode.image.svg
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer

from core.models import Model
from core.settings import settings

QR_STYLES = ("square", "rounded", "dots")

_MODULE_DRAWERS = {
    "square": SquareModuleDrawer,
    "rounded": RoundedModuleDrawer,
    "dots": CircleModuleDrawer,
}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(color_a: str, color_b: str) -> float:
    """WCAG contrast ratio between two hex colors (1..21)."""
    la = _relative_luminance(hex_to_rgb(color_a))
    lb = _relative_luminance(hex_to_rgb(color_b))
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass(kw_only=True)
class QrCode(Model):
    id: UUID = field(default_factory=uuid.uuid4)
    user_id: UUID
    name: str
    link: str
    scan_count: int = 0
    last_scan_at: int | None = None
    fill_color: str = "#000000"
    fill_color2: str | None = None  # radial-gradient edge color; solid fill when None
    back_color: str = "#ffffff"
    style: str = "square"

    def public_url(self) -> str:
        return settings.API_SCHEME + "://" + settings.API_URL + settings.QR_CODE_ENDPOINT.format(uuid=self.id)

    def get_image(self, box_size: int = 10) -> Image.Image:
        return render_qr_image(
            self.public_url(), self.fill_color, self.fill_color2, self.back_color, self.style, box_size
        )

    def get_svg(self) -> bytes:
        return render_qr_svg(self.public_url(), self.fill_color, self.back_color)


def render_qr_image(
    data: str, fill_color: str, fill_color2: str | None, back_color: str, style: str, box_size: int = 10
) -> Image.Image:
    qr = qrcode.main.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    back = hex_to_rgb(back_color)
    fill = hex_to_rgb(fill_color)
    if fill_color2 is not None:
        # center → edge gradient reads as volume ("3D" look)
        color_mask = RadialGradiantColorMask(back_color=back, center_color=fill, edge_color=hex_to_rgb(fill_color2))
    else:
        color_mask = SolidFillColorMask(back_color=back, front_color=fill)
    return qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=_MODULE_DRAWERS[style](),
        color_mask=color_mask,
    )


def render_qr_svg(data: str, fill_color: str, back_color: str) -> bytes:
    # SVG stays flat: solid fill only, gradients and module shapes are PNG-only
    factory = type(
        "ColoredSvgImage",
        (qrcode.image.svg.SvgPathFillImage,),
        {
            "QR_PATH_STYLE": {**qrcode.image.svg.SvgPathImage.QR_PATH_STYLE, "fill": fill_color},
            "background": back_color,
        },
    )
    qr = qrcode.main.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        border=4,
        image_factory=factory,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image().to_string()


@dataclass(kw_only=True)
class ScanEvent(Model):
    id: UUID = field(default_factory=uuid.uuid4)
    qr_code_id: UUID
    ts: int
