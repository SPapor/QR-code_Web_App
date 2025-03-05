from typing import Sequence
from uuid import UUID

from PIL import Image

from qr_code.dal import QrCodeRepo
from qr_code.models import QrCode


class QrCodeService:
    def __init__(self, qr_code_repo: QrCodeRepo):
        self.qr_code_repo = qr_code_repo

    async def get_image_by_qr_code_id(self, id: UUID) -> Image.Image:
        qr_code = await self.qr_code_repo.get_by_id(id)
        return qr_code.get_image()

    async def get_all(self) -> Sequence[QrCode]:
        return await self.qr_code_repo.get_all()
