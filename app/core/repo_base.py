from core.crud_base import DTO, CrudBase
from core.serializer import Serializer


class RepoBase[ID, Model]:
    def __init__(self, crud: CrudBase[ID, DTO], serializer: Serializer[Model, DTO]):
        self.crud = crud
        self.serializer = serializer

    async def get_by_id(self, id_: ID) -> Model:
        dto = await self.crud.get_by_id(id_)
        return self.serializer.deserialize(dto)
