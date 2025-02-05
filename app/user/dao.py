from uuid import UUID

from core.crud_base import DTO, CrudBase
from user.tables import user_table


class UserCrud(CrudBase[UUID, DTO]):
    table = user_table
