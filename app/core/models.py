from typing import ClassVar, Callable

from core import errors


class Model:
    NotFoundException: ClassVar[Callable[[], errors.NotFoundError]]
    AlreadyExistError: ClassVar[Callable[[], errors.AlreadyExistError]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        class NotFoundError(errors.NotFoundError):
            def __init__(self):
                super().__init__(cls.__name__)

            __qualname__ = f"{cls.__qualname__}.NotFoundError"

        cls.NotFoundException = NotFoundError

        class AlreadyExistError(errors.AlreadyExistError):
            def __init__(self):
                super().__init__(cls.__name__)

            __qualname__ = f"{cls.__qualname__}.AlreadyExistError"  # Fix traceback name

        cls.AlreadyExistError = AlreadyExistError
