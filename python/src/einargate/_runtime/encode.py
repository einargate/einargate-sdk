"""Building blocks of the generated encoders, which write wire JSON."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Final, TypeVar, final

from .unknown import UnknownValue

T = TypeVar("T")


@final
class NotGiven:
    """The default of an optional field with three states.

    Left out (``NOT_GIVEN``), ``None`` and a value mean different things,
    e.g. a permission's country: the location's default, none, or this one.
    """

    def __repr__(self) -> str:
        return "NOT_GIVEN"

    def __bool__(self) -> bool:
        return False


NOT_GIVEN: Final = NotGiven()


def timestamp(value: datetime, name: str = "timestamp") -> str:
    """ISO 8601 in UTC; a naive ``datetime`` is refused, not guessed."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            f"{name} must be a timezone-aware datetime, e.g. datetime.now(timezone.utc)"
        )
    utc = value.astimezone(timezone.utc)
    return utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def enum_value(value: str | UnknownValue) -> str:
    """An enum value as sent, known or not."""
    return value.unknown if isinstance(value, UnknownValue) else value


def empty_if_none(value: str | None) -> str:
    """``None`` is sent as ``""``, how the API says "none" in a few fields."""
    return "" if value is None else value


def compact(value: dict[str, object]) -> dict[str, object]:
    """Leaves out the members whose value is ``None`` or ``NOT_GIVEN``."""
    return {
        key: member
        for key, member in value.items()
        if member is not None and not isinstance(member, NotGiven)
    }


def query_integer(value: int | None) -> str | None:
    return None if value is None else str(value)


def query_boolean(value: bool | None) -> str | None:
    return None if value is None else ("true" if value else "false")


def query_timestamp(value: datetime | None, name: str) -> str | None:
    return None if value is None else timestamp(value, name)


def query_enum(value: str | UnknownValue | None) -> str | None:
    return None if value is None else enum_value(value)


def optional(value: T | None, encode: Callable[[T], object]) -> object:
    """Encodes a member that may be absent."""
    return None if value is None else encode(value)


def three_state(value: str | NotGiven | None) -> str | NotGiven:
    """Left out stays out, ``None`` is sent as ``""``."""
    if isinstance(value, NotGiven):
        return value
    return empty_if_none(value)
