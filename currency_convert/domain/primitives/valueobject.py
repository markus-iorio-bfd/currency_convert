from __future__ import annotations

import abc
import dataclasses
import typing

from currency_convert.domain.primitives.error import ConverterError

T = typing.TypeVar("T")


class ValueObjectError(ConverterError):
    """Base class for errors related to ValueObjects."""


@dataclasses.dataclass(frozen=True, slots=True)
class ValueObject(abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def get_values(self) -> typing.Iterator[T]:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self._equals(other)

    def _equals(self, other: ValueObject[T]) -> bool:
        _zipped = self.get_values(), other.get_values()
        return all(self == other for self, other in zip(*_zipped))

    def __hash__(self) -> int:
        return hash(self.get_values()) * 41
