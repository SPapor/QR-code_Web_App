from typing import Any, Mapping

# rows come back from sqlalchemy as RowMapping (whose key type is wider than str),
# so the alias is intentionally Mapping[Any, Any]
DTO = Mapping[Any, Any]
