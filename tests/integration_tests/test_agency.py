import typing
import uuid
from typing import Sequence

import pytest
from results import Result

from currency_convert.domain.agency.entities.agency import Agency, UnprocessedRate
from currency_convert.domain.agency.valueobjects.currency import Currency
from currency_convert.domain.agency.valueobjects.money import Money
from currency_convert.domain.agency.valueobjects.rate import Rate
from currency_convert.domain.primitives.entity import EntityError


class FakeRatesRepository:
    def __init__(self) -> None:
        self.rates: list[Rate] = []

    def add(self, rate: Rate) -> Result[None, EntityError]:
        self.rates.append(rate)
        return Result.Ok(None)

    def get_all(self) -> Result[Sequence[Rate], EntityError]:
        return Result.Ok(self.rates)

    def get(
        self, filter: typing.Callable[[Rate], bool]
    ) -> Result[Sequence[Rate], EntityError]:
        return self.get_all().map(
            lambda rates: [rate for rate in rates if filter(rate)]
        )


@pytest.fixture
def agency() -> Agency:
    repository = FakeRatesRepository()
    return Agency(
        address="https://test.com",
        id_=uuid.uuid4(),
        base=Currency.create("USD").unwrap(),
        name="Test Agency",
        country="Test Country",
        # rates_repository=repository,
    )


def test_add_rate(agency: Agency) -> None:
    result = agency.add_rate("USD", "EUR", "0.85", "2023-10-01T00:00:00")
    assert result.is_ok()
    assert len(agency.rates) == 1


def test_add_rates(agency: Agency) -> None:
    rates = [
        UnprocessedRate(
            currency_from="USD",
            currency_to="EUR",
            rate="0.85",
            date="2023-10-01T00:00:00",
        ),
        UnprocessedRate(
            currency_from="USD",
            currency_to="GBP",
            rate="0.75",
            date="2023-10-01T00:00:00",
        ),
    ]
    result = agency.add_rates(rates)
    assert result.is_ok()
    assert len(agency.rates) == 2


def test_get_rate(agency: Agency) -> None:
    agency.add_rate("USD", "EUR", "0.85", "2023-10-01T00:00:00")
    result = agency.get_rate("USD", "EUR", "2023-10-01T00:00:00")
    assert result.is_ok()
    assert result.unwrap().rate == Money.create("0.85").unwrap()
    result = agency.get_rate("EUR", "USD", "2023-10-01T00:00:00")
    assert result.is_ok()
    assert result.unwrap().rate == Money.create("1.17647059").unwrap()


def test_list_rates(agency: Agency) -> None:
    agency.add_rate("USD", "EUR", "0.85", "2023-10-01T00:00:00")
    agency.add_rate("USD", "GBP", "0.75", "2023-10-01T00:00:00")
    result = agency.list_rates()
    assert result.is_ok()
    assert len(result.unwrap()) == 2


def test_add_unprocessable_rates(agency: Agency) -> None:
    rates = [
        UnprocessedRate(
            currency_from="INVALID",
            currency_to="EUR",
            rate="0.85",
            date="2023-10-01T00:00:00",
        ),
        UnprocessedRate(
            currency_from="USD",
            currency_to="INVALID",
            rate="0.75",
            date="2023-10-01T00:00:00",
        ),
    ]
    result = agency.add_rates(rates)
    assert result.is_err()
    assert len(result.unwrap_err()) == 2
    assert len(agency.rates) == 0


def test_get_rate_no_base_currency(agency: Agency) -> None:
    # Add rates that do not include the base currency
    agency.add_rate("USD", "EUR", "0.85", "2023-10-01T00:00:00")
    agency.add_rate("USD", "JPY", "150.00", "2023-10-01T00:00:00")
    agency.add_rate("USD", "GBP", "0.75", "2023-10-01T00:00:00")

    # Attempt to get a rate that requires the base currency
    result = agency.get_rate("EUR", "JPY", "2023-10-01T00:00:00")
    assert result.is_ok()
    assert (
        result.unwrap()
        == Rate.create(
            currency_from="EUR",
            currency_to="JPY",
            rate="176.47058850",
            iso_str="2023-10-01T00:00:00",
        ).unwrap()
    )


def test_get_rate_with_date_range(agency: Agency) -> None:
    # Add rates for different dates
    agency.add_rate("USD", "EUR", "0.85", "2023-10-01T00:00:00")
    agency.add_rate("USD", "EUR", "0.86", "2023-09-30T00:00:00")
    agency.add_rate("USD", "EUR", "0.87", "2023-09-29T00:00:00")

    # Attempt to get a rate for a date range
    result = agency.get_rate("USD", "EUR", "2023-09-29T00:00:00", "2023-10-01T00:00:00")
    assert result.is_ok()
    assert result.unwrap().rate == Money.create("0.85").unwrap()
