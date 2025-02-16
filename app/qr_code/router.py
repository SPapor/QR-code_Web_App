import io
from uuid import UUID

from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter
from fastapi.responses import Response

from qr_code.services import QrCodeService

router = APIRouter(route_class=DishkaRoute)


@router.get("/{qr_code_id}")
async def read_item(qr_code_id: UUID, qr_code_service: FromDishka[QrCodeService]):
    image = await qr_code_service.get_image_by_qr_code_id(qr_code_id)
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_bytes = image_io.getvalue()
    return Response(content=image_bytes, media_type="image/png")

@router.get("/")
async def get_all(qr_code_service: FromDishka[QrCodeService]):
    return await qr_code_service.get_all()