import decimal

from currency_convert.domain.agency.valueobjects.money import Money
from currency_convert.domain.primitives.valueobject import ValueObjectError


def test_create_ok() -> None:
    result = Money.create(100)
    assert result.is_ok()
    assert result.unwrap() == Money(decimal.Decimal("100.00000000"))


def test_create_err_negative_value() -> None:
    result = Money.create(-100)
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)


def test_create_err_zero_value() -> None:
    result = Money.create(0)
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)


def test_create_err_invalid_value() -> None:
    result = Money.create("invalid")
    assert result.is_err()
    assert isinstance(result.unwrap_err(), ValueObjectError)
