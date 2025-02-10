from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import is_dataclass
from typing import Protocol


class Serializer[Model, DTO](Protocol):
    def serialize(self, obj: Model) -> DTO:
        pass

    def deserialize(self, obj: DTO) -> Model:
        pass

    @property
    def flat(self) -> Serializer[list[Model], list[DTO]]:
        pass


class SerializerBase[Model, DTO](ABC, Serializer[Model, DTO]):
    @abstractmethod
    def serialize(self, obj: Model) -> DTO:
        pass

    @abstractmethod
    def deserialize(self, obj: DTO) -> Model:
        pass

    @property
    def flat(self) -> Serializer[list[Model], list[DTO]]:
        return FlatSerializer(self)


class FlatSerializer[Model, DTO](SerializerBase[list[Model], list[DTO]]):
    def __init__(self, serializer: Serializer[Model, DTO]):
        self.serializer = serializer

    def serialize(self, objs: list[Model]) -> list[DTO]:
        return [self.serializer.serialize(obj) for obj in objs]

    def deserialize(self, objs: list[DTO]) -> list[Model]:
        return [self.serializer.deserialize(obj) for obj in objs]


class DataclassSerializer[Model, DTO](SerializerBase[Model, DTO]):
    model: type[Model]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "model"):
            raise TypeError(f"Class '{cls.__name__}' must define a 'model' attribute.")
        if not isinstance(cls.model, type):
            raise TypeError(
                f"Attribute 'model' of class '{cls.__name__}' must be a dataclass type. "
                f"Got '{cls.model}' with type '{type(cls.model).__name__}'."
            )
        if not is_dataclass(cls.model):
            raise TypeError(f"Attribute 'model' of class '{cls.__name__}' must be a dataclass. Got '{cls.model}'.")

    def serialize(self, obj: Model) -> DTO:
        return dataclasses.asdict(obj)

    def deserialize(self, obj: DTO) -> Model:
        return self.model(**obj)
