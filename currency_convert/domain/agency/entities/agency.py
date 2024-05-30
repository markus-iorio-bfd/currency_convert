from __future__ import annotations

import dataclasses
import logging
import typing
from datetime import datetime
from functools import partial
from typing import Sequence

from results import Null, Option, Result, Some
from typing_extensions import TypedDict

from currency_convert.domain.agency.valueobjects.currency import Currency
from currency_convert.domain.agency.valueobjects.money import _Decimal
from currency_convert.domain.agency.valueobjects.rate import Rate
from currency_convert.domain.primitives.entity import AggregateRoot
from currency_convert.domain.primitives.error import GenericError

_logger = logging.getLogger(__name__)


class UnprocessedRate(TypedDict):
    currency_from: str
    currency_to: str
    rate: _Decimal
    date: str


class UnprocessableRate(UnprocessedRate):
    pass


@dataclasses.dataclass(slots=True, eq=False)
class Agency(AggregateRoot):
    base: Currency
    name: str
    address: str
    country: str
    rates: list[Rate] = dataclasses.field(default_factory=list)

    def add_rate(
        self,
        currency_from: str,
        currency_to: str,
        rate: _Decimal,
        date: str,
    ) -> Result[Null[None], GenericError]:
        return (
            Rate.create(currency_from, currency_to, rate, date)
            .and_then(Result.as_result(self.rates.append))
            .map(Null)
        )

    def add_rates(
        self,
        rates: list[UnprocessedRate],
    ) -> Result[Null[None], list[UnprocessableRate]]:
        unprocessable = [
            rate
            for rate in rates
            if self.add_rate(
                rate["currency_from"],
                rate["currency_to"],
                rate["rate"],
                rate["date"],
            ).is_err()
        ]
        return Result.Err(unprocessable) if unprocessable else Result.Ok(Null(None))

    def get_rate(
        self,
        currency_from: str,
        currency_to: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Result[Rate, GenericError]:
        if start_date is None:
            start_date = datetime.now().isoformat()
        if end_date is None:
            end_date = datetime.now().isoformat()

        def filter_on(currency: str, start_date: str, end_date: str, r: Rate) -> bool:
            return (
                r.currency_to == currency
                and start_date <= r.date.isoformat() <= end_date
            )

        def find_rate(
            currency: str,
            start_date: str,
            end_date: str,
        ) -> Result[Rate, GenericError]:
            f = partial(filter_on, currency, start_date, end_date)
            return self.iter(f).ok_or_else(GenericError)

        if self.is_base_currency(currency_from):
            return find_rate(currency_to, start_date, end_date)
        if self.is_base_currency(currency_to):
            return find_rate(currency_from, start_date, end_date).and_then(Rate.invert)
        return (
            find_rate(currency_from, start_date, end_date)
            .and_then(Rate.invert)
            .and_then(
                lambda rf: find_rate(currency_to, start_date, end_date).and_then(
                    partial(Rate.multiply, other=rf)
                )
            )
        )

    def iter(
        self,
        predicate: typing.Callable[[Rate], bool],
    ) -> Option[Rate, typing.Any]:
        try:
            return next(Some(r) for r in self.rates if predicate(r))
        except StopIteration:
            return Null(None)

    @Result.as_result
    def list_rates(self) -> Sequence[Rate]:
        return tuple(self.rates)

    def is_base_currency(self, currency: str) -> bool:
        return currency == self.base
