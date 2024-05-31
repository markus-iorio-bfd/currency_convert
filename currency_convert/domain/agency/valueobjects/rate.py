from __future__ import annotations

import dataclasses
import datetime
import typing
from typing import Iterator

from results import Result

from currency_convert.domain.agency.valueobjects.currency import Currency
from currency_convert.domain.agency.valueobjects.money import Money, _Decimal
from currency_convert.domain.primitives.valueobject import ValueObject, ValueObjectError


class RateError(ValueObjectError):
    """Base class for errors related to Rate."""


class InvalidDateError(RateError):
    """Invalid date error."""


@dataclasses.dataclass(frozen=True, slots=True, eq=False)
class Rate(ValueObject[Currency | Money | datetime.datetime]):
    currency_from: Currency
    currency_to: Currency
    rate: Money
    date: datetime.datetime

    def get_values(self) -> Iterator[Currency | Money | datetime.datetime]:
        yield self.currency_from
        yield self.currency_to
        yield self.rate
        yield self.date

    @classmethod
    def create(
        cls,
        currency_from: str,
        currency_to: str,
        rate: _Decimal,
        iso_str: str,
    ) -> Result[typing.Self, ValueObjectError]:
        def create_currency_pair(
            cf: Currency,
        ) -> Result[tuple[Currency, Currency], ValueObjectError]:
            return Currency.create(currency_to).map(lambda ct: (cf, ct))

        def create_rate(
            cf_ct: tuple[Currency, Currency],
        ) -> Result[tuple[Currency, Currency, Money], ValueObjectError]:
            return Money.create(rate).map(lambda r: (*cf_ct, r))

        def create_datetime(
            cf_ct_r: tuple[Currency, Currency, Money],
        ) -> Result[
            tuple[Currency, Currency, Money, datetime.datetime],
            ValueObjectError,
        ]:
            from_iso = datetime.datetime.fromisoformat
            return (
                Result.as_result(from_iso)(iso_str)
                .map_err(lambda exc: InvalidDateError.from_exc(exc))  # type: ignore [return-value]
                .map(lambda dt: (*cf_ct_r, dt))
            )

        return (
            Currency.create(currency_from)
            .and_then(create_currency_pair)
            .and_then(create_rate)
            .and_then(create_datetime)
            .map(lambda cf_ct_r_dt: cls(*cf_ct_r_dt))
        )

    def multiply(self, other: Rate) -> Result[Rate, ValueObjectError]:
        calculation = next(self.rate.get_values()) * next(other.rate.get_values())
        return Money.create(calculation).and_then(
            lambda m: Rate.create(
                other.currency_from.code,
                self.currency_to.code,
                next(m.get_values()),
                self.date.isoformat(),
            )
        )

    def invert(self) -> Result[Rate, ValueObjectError]:
        calculation = 1 / next(self.rate.get_values())
        return Money.create(calculation).and_then(
            lambda m: Rate.create(
                self.currency_to.code,
                self.currency_from.code,
                next(m.get_values()),
                self.date.isoformat(),
            )
        )

    def get_rate(self) -> Money:
        return self.rate
