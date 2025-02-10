from uuid import UUID

from core.crud_base import DTO, CrudBase
from core.serializer import DataclassSerializer
from user.models import User
from user.tables import user_table


class UserCrud(CrudBase[UUID, DTO]):
    table = user_table


class UserSerializer(DataclassSerializer[User, DTO]):
    model = User
