from uuid import UUID

from core.crud_base import CrudBase
from core.repo_base import RepoBase
from core.serializer import Serializer
from core.types import DTO
from qr_code.models import QrCode
from qr_code.tables import qr_code_table


class QrCodeCrud(CrudBase[UUID, DTO]):
    table = qr_code_table


class QrCodeRepo(RepoBase[UUID, QrCode]):
    crud: QrCodeCrud

    def __init__(self, crud: QrCodeCrud, serializer: Serializer[QrCode, DTO]):
        super().__init__(crud, serializer)
