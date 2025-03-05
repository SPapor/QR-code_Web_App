from typing import ClassVar, Callable

from core.error import ResourceNotFoundException


class Model:
    NotFoundException: ClassVar[Callable[[], ResourceNotFoundException]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        class NotFoundException(ResourceNotFoundException):
            def __init__(self):
                super().__init__(cls.__name__)

        cls.NotFoundException = NotFoundException
