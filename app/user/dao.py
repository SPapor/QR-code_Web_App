from uuid import UUID

from core.crud_base import CrudBase, DTO
from user.tables import user_table


class UserCrud(CrudBase[UUID, DTO]):
    table = user_table
