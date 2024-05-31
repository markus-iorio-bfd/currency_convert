from __future__ import annotations

import dataclasses
import decimal
import typing
from typing import Iterator

from results import Result

from currency_convert.domain.primitives.valueobject import ValueObject, ValueObjectError

_Decimal: typing.TypeAlias = (
    decimal.Decimal | float | str | tuple[int, typing.Sequence[int], int]
)


class MoneyError(ValueObjectError):
    """Base class for errors related to Money."""


class FormatError(MoneyError):
    """Format error."""


class NegativeError(MoneyError):
    """Negative error."""


@dataclasses.dataclass(frozen=True, slots=True, eq=False)
class Money(ValueObject[decimal.Decimal]):
    PRECISION: typing.ClassVar[decimal.Decimal] = decimal.Decimal(10) ** -8
    ERROR_MSG: typing.ClassVar[str] = "Money value must be positive. Got: {{value}}"
    value: decimal.Decimal

    def get_values(self) -> Iterator[decimal.Decimal]:
        yield self.value

    @classmethod
    def create(cls, value: _Decimal) -> Result[typing.Self, ValueObjectError]:
        try:
            v = decimal.Decimal(value).quantize(cls.PRECISION)
        except decimal.DecimalException as exc:
            return Result.Err(FormatError.from_exc(exc))
        else:
            if cls.is_positive(v):
                return Result.Ok(cls(v))
            err = NegativeError(cls.ERROR_MSG.format(value=value))
            return Result.Err(err)

    @classmethod
    def is_positive(cls, value: decimal.Decimal) -> bool:
        return value > decimal.Decimal(0)

    def __add__(self, other: Money) -> Money:
        return Money(self.value + other.value)

    def __sub__(self, other: Money) -> Money:
        return Money(self.value - other.value)

    def __mul__(self, other: Money) -> Money:
        return Money(self.value * other.value)

    def __truediv__(self, other: Money) -> Money:
        return Money(self.value / other.value)

    def __floordiv__(self, other: Money) -> Money:
        return Money(self.value // other.value)

    def __mod__(self, other: Money) -> Money:
        return Money(self.value % other.value)

    def __pow__(self, other: Money) -> Money:
        return Money(self.value**other.value)
