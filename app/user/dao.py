from uuid import UUID

from core.crud_base import CrudBase
from core.repo_base import RepoBase
from core.serializer import DataclassSerializer
from core.types import DTO
from user.models import User
from user.tables import user_table


class UserCrud(CrudBase[UUID, DTO]):
    table = user_table


class UserSerializer(DataclassSerializer[User, DTO]):
    model = User


class UserRepo(RepoBase[UUID, User]):
    def __init__(self, crud: UserCrud, serializer: UserSerializer):
        super().__init__(crud, serializer)
