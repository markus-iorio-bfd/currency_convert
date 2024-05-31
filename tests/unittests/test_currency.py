from currency_convert.domain.agency.valueobjects.currency import Currency
from currency_convert.domain.primitives.valueobject import ValueObjectError


def test_create__when_code_is_valid_length_should_return_currency_instance() -> None:
    result = Currency.create("USD")
    assert result.is_ok()
    currency = result.unwrap()
    assert currency.code == "USD"


def test_create__when_code_is_invalid_length_should_return_generic_error() -> None:
    result = Currency.create("US")
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)


def test_equality__when_currency_compared_with_same_string_should_return_true() -> None:
    currency = Currency.create("USD").unwrap()
    assert currency == "USD"


def test_equality__when_currency_compared_with_different_string_should_return_false() -> (
    None
):
    currency = Currency.create("USD").unwrap()
    assert currency != "EUR"


def test_equality__when_two_currencies_have_same_code_should_return_true() -> None:
    currency1 = Currency.create("USD").unwrap()
    currency2 = Currency.create("USD").unwrap()
    assert currency1 == currency2


def test_inequality__when_two_currencies_have_different_codes_should_return_false() -> (
    None
):
    currency1 = Currency.create("USD").unwrap()
    currency2 = Currency.create("EUR").unwrap()
    assert currency1 != currency2


def test_get_values__when_called_should_return_list_with_currency_code() -> None:
    currency = Currency.create("USD").unwrap()
    values = list(currency.get_values())
    assert values == ["USD"]
