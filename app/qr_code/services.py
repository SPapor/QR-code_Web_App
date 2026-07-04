import time
from typing import Sequence
from uuid import UUID

from PIL import Image

from qr_code.dal import QrCodeRepo
from qr_code.models import QrCode


class QrCodeService:
    def __init__(self, qr_code_repo: QrCodeRepo):
        self.qr_code_repo = qr_code_repo

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
        await self.qr_code_repo.increment_scan_count(id, int(time.time()))
        return qr_code

    async def update_qr_code(self, user_id: UUID, qr_code_id: UUID, name: str, link: str) -> QrCode:
        qr_code = await self.qr_code_repo.get_by_id(qr_code_id)
        if qr_code.user_id != user_id:
            raise QrCode.NotFoundError
        qr_code.link = link
        qr_code.name = name
        return await self.qr_code_repo.update_and_get(qr_code)
