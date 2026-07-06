import io
from typing import Annotated, Literal
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.dependencies import logged_in_user_id
from core.dependencies import auto_commit
from qr_code.models import QrCode, contrast_ratio, render_qr_image
from qr_code.services import QrCodeService

router = APIRouter(route_class=DishkaRoute)

# QR content never changes for a given id, so browsers may cache the rendered image
IMAGE_CACHE_HEADERS = {"Cache-Control": "public, max-age=86400"}


# link-preview fetchers of messengers/social networks; their hits are not real visits
PREVIEW_BOT_UA_MARKERS = (
    "telegrambot",
    "whatsapp",
    "facebookexternalhit",
    "twitterbot",
    "slackbot",
    "discordbot",
    "linkedinbot",
    "skypeuripreview",
    "viber",
)


HEX_COLOR = r"^#[0-9a-fA-F]{6}$"
# below this WCAG ratio between modules and background scanners start to struggle
MIN_QR_CONTRAST = 2.5


class QrStylePayload(BaseModel):
    fill_color: str = Field("#000000", pattern=HEX_COLOR)
    fill_color2: str | None = Field(None, pattern=HEX_COLOR)  # radial-gradient edge; solid when omitted
    back_color: str = Field("#ffffff", pattern=HEX_COLOR)
    style: Literal["square", "rounded", "dots"] = "square"

    @model_validator(mode="after")
    def check_contrast(self) -> "QrStylePayload":
        for color in (self.fill_color, self.fill_color2):
            if color is not None and contrast_ratio(color, self.back_color) < MIN_QR_CONTRAST:
                raise ValueError("not enough contrast between code and background to scan reliably")
        return self


# body, not query: user links must not end up in access logs
class QrCodePayload(QrStylePayload):
    name: str = Field(min_length=1, max_length=100)
    link: str = Field(min_length=1, max_length=2048, pattern=r"^https?://")


@router.get("/{qr_code_id}/image")
async def read_item(
    qr_code_id: UUID,
    qr_code_service: FromDishka[QrCodeService],
    fmt: Literal["png", "svg"] = "png",
    scale: int = Query(10, ge=4, le=40),
):
    if fmt == "svg":
        svg = await qr_code_service.get_svg_by_qr_code_id(qr_code_id)
        return Response(content=svg, media_type="image/svg+xml", headers=IMAGE_CACHE_HEADERS)
    image = await qr_code_service.get_image_by_qr_code_id(qr_code_id, box_size=scale)
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_bytes = image_io.getvalue()
    return Response(content=image_bytes, media_type="image/png", headers=IMAGE_CACHE_HEADERS)


@router.get("/style/preview")
async def style_preview(
    style: Annotated[QrStylePayload, Query()],
    _user_id: UUID = Depends(logged_in_user_id),
):
    # live preview for the editor: renders a sample payload with the requested style
    image = render_qr_image(
        "https://example.com/preview", style.fill_color, style.fill_color2, style.back_color, style.style
    )
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    return Response(content=image_io.getvalue(), media_type="image/png")


@router.get("/")
async def get_all_user_qr_codes(qr_code_service: FromDishka[QrCodeService], user_id: UUID = Depends(logged_in_user_id)):
    return await qr_code_service.get_all_user_qr_codes(user_id)


@router.post("/")
async def create_qr_code(
    qr_code_service: FromDishka[QrCodeService],
    payload: QrCodePayload,
    user_id: UUID = Depends(logged_in_user_id),
    _session: AsyncSession = Depends(auto_commit),
):
    return await qr_code_service.create_qr_code(user_id, **payload.model_dump())


@router.delete("/{qr_code_id}")
async def delete_qr_code(
    qr_code_service: FromDishka[QrCodeService],
    qr_code_id: UUID,
    user_id: UUID = Depends(logged_in_user_id),
    _session: AsyncSession = Depends(auto_commit),
):
    await qr_code_service.delete_qr_code(user_id, qr_code_id)
    return {"ok": True}


@router.get("/{qr_code_id}/stats")
async def scan_stats(
    qr_code_id: UUID,
    qr_code_service: FromDishka[QrCodeService],
    days: int = Query(30, ge=1, le=90),
    user_id: UUID = Depends(logged_in_user_id),
):
    return await qr_code_service.get_scan_stats(user_id, qr_code_id, days)


@router.api_route("/{qr_code_id}", methods=["GET", "HEAD"])
async def redirect(
    qr_code_id: UUID,
    request: Request,
    qr_code_service: FromDishka[QrCodeService],
    _session: AsyncSession = Depends(auto_commit),
) -> RedirectResponse:
    # HEAD requests and link-preview bots would inflate the stats without being real visits
    user_agent = request.headers.get("user-agent", "").lower()
    if request.method == "HEAD" or any(marker in user_agent for marker in PREVIEW_BOT_UA_MARKERS):
        qr_code = await qr_code_service.get_by_id(qr_code_id)
    else:
        qr_code = await qr_code_service.register_scan(qr_code_id)
    return RedirectResponse(url=qr_code.link, status_code=status.HTTP_302_FOUND)


@router.put("/{qr_code_id}")
async def edit(
    qr_code_service: FromDishka[QrCodeService],
    qr_code_id: UUID,
    payload: QrCodePayload,
    user_id: UUID = Depends(logged_in_user_id),
    _session: AsyncSession = Depends(auto_commit),
) -> QrCode:
    return await qr_code_service.update_qr_code(user_id, qr_code_id, **payload.model_dump())
