from __future__ import annotations

import typing


class ConverterError(Exception):
    @classmethod
    def from_exc(cls, exc: Exception) -> typing.Self:
        cls.__cause__ = exc
        return cls()
