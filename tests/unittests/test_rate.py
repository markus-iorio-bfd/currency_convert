import datetime

from currency_convert.domain.agency.valueobjects.currency import Currency
from currency_convert.domain.agency.valueobjects.money import Money
from currency_convert.domain.agency.valueobjects.rate import Rate
from currency_convert.domain.primitives.valueobject import ValueObjectError


def test_create__when_all_parameters_are_valid_should_return_rate_instance() -> None:
    result = Rate.create("USD", "EUR", "0.85", "2023-10-01T00:00:00")
    assert result.is_ok()
    rate = result.unwrap()
    assert rate.currency_from == Currency("USD")
    assert rate.currency_to == Currency("EUR")
    assert rate.rate == Money.create("0.85").unwrap()
    assert rate.date == datetime.datetime(2023, 10, 1, 0, 0, 0)


def test_create__when_currency_code_is_invalid_should_return_generic_error() -> None:
    result = Rate.create("US", "EUR", "0.85", "2023-10-01T00:00:00")
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)


def test_create__when_rate_format_is_invalid_should_return_generic_error() -> None:
    result = Rate.create("USD", "EUR", "invalid_rate", "2023-10-01T00:00:00")
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)


def test_create__when_date_format_is_invalid_should_return_value_error() -> None:
    result = Rate.create("USD", "EUR", "0.85", "invalid_date")
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)


def test_create__when_rate_is_zero_should_return_generic_error() -> None:
    result = Rate.create("USD", "EUR", "0.00", "2023-10-01T00:00:00")
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)
