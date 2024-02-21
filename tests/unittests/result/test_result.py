import pytest

from currency_convert.core.domain.shared.result import (
    Failure,
    Result,
    Success,
    UnwrapFailedError,
)


def test_unwrap() -> None:
    assert Success(1).unwrap() == 1

    with pytest.raises(UnwrapFailedError):
        Failure(1).unwrap()


def test_value_or() -> None:
    assert Success(1).value_or(2) == 1
    assert Failure(1).value_or(2) == 2


def test_failure() -> None:
    assert Failure(1).failure() == 1

    with pytest.raises(UnwrapFailedError):
        Success(1).failure()


def test_is_success() -> None:
    assert Success(1).is_success()
    assert not Failure(1).is_success()


def test_is_failure() -> None:
    assert not Success(1).is_failure()
    assert Failure(1).is_failure()


def test_pattern_matching_success_type() -> None:
    o = Result.from_value("yay")
    match o:
        case Success(value):
            reached = True

    assert value == "yay"
    assert reached


def test_pattern_matching_failure_type() -> None:
    n = Result.from_failure("nay")
    match n:
        case Failure(value):
            reached = True

    assert value == "nay"
    assert reached


def test_slots() -> None:
    o = Success("yay")
    n = Failure("nay")
    with pytest.raises(AttributeError):
        o.some_arbitrary_attribute = 1  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        n.some_arbitrary_attribute = 1  # type: ignore[attr-defined]
