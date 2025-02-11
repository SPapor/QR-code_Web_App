from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import is_dataclass
from typing import Protocol

from core.types import DTO


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


class DataclassSerializer[Model, T_DTO: DTO](SerializerBase[Model, T_DTO]):
    def __init__(self, model: type[Model]):
        self.model = model
        if not isinstance(model, type) or not is_dataclass(model):
            raise TypeError(f"Argument 'model' must be a dataclass class. Got '{model}'.")

    def serialize(self, obj: Model) -> DTO:
        return dataclasses.asdict(obj)

    def deserialize(self, obj: DTO) -> Model:
        return self.model(**obj)
