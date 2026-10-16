"""Building blocks of the generated decoders.

They check every success body against the contract while turning it into
the library's types; a body that does not match becomes an
``UnexpectedResponse`` error. Decoding is lenient where the contract lets the
API grow: unknown members are ignored, and unknown enum values and union
variants become ``UnknownValue``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from typing import TypeVar, cast

from .unknown import UnknownValue

T = TypeVar("T")
S = TypeVar("S", bound=str)

Decoder = Callable[[object, str], T]
JsonObject = Mapping[str, object]


class DecodeError(Exception):
    """Raised inside a decoder; the transport turns it into a result."""

    def __init__(self, path: str, expected: str) -> None:
        super().__init__(f"{path or 'the body'}: expected {expected}")
        self.path = path
        self.expected = expected


def object_(value: object, path: str) -> JsonObject:
    if not isinstance(value, dict):
        raise DecodeError(path, "an object")
    return cast(JsonObject, value)


def string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise DecodeError(path, "a string")
    return value


def number(value: object, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DecodeError(path, "a number")
    return value


def integer(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        raise DecodeError(path, "an integer")
    return value


def boolean(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise DecodeError(path, "a boolean")
    return value


def timestamp(value: object, path: str) -> datetime:
    """An ISO 8601 timestamp, as a timezone-aware ``datetime``."""
    text = string(value, path)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise DecodeError(path, "an ISO 8601 timestamp") from None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def literal(value: object, path: str, expected: T) -> T:
    if value != expected or isinstance(value, bool) != isinstance(expected, bool):
        raise DecodeError(path, repr(expected))
    return expected


def enum_value(value: object, path: str, values: tuple[S, ...]) -> S | UnknownValue:
    """A known value, or an ``UnknownValue`` for one added since this release."""
    text = string(value, path)
    for known in values:
        if known == text:
            return known
    return UnknownValue(text)


def array(value: object, path: str, item: Decoder[T]) -> tuple[T, ...]:
    if not isinstance(value, list):
        raise DecodeError(path, "an array")
    elements = cast("list[object]", value)
    return tuple(
        item(element, f"{path}.{index}") for index, element in enumerate(elements)
    )


def non_empty_array(value: object, path: str, item: Decoder[T]) -> tuple[T, ...]:
    items = array(value, path, item)
    if not items:
        raise DecodeError(path, "at least one item")
    return items


def json_object(value: object, path: str) -> JsonObject:
    return object_(value, path)


def null_if_empty(value: object, path: str) -> str | None:
    """``""`` is how the API says "none" in a few fields."""
    text = string(value, path)
    return None if text == "" else text


def required(value: JsonObject, key: str, path: str, decode: Decoder[T]) -> T:
    """A member that must be present."""
    return decode(value.get(key), join(path, key))


def optional(value: JsonObject, key: str, path: str, decode: Decoder[T]) -> T | None:
    """A member that may be absent; ``null`` counts as absent."""
    member = value.get(key)
    return None if member is None else decode(member, join(path, key))


def join(path: str, key: str) -> str:
    return f"{path}.{key}" if path else key


def literal_decoder(expected: T) -> Decoder[T]:
    return lambda value, path: literal(value, path, expected)


def array_decoder(item: Decoder[T]) -> Decoder[tuple[T, ...]]:
    return lambda value, path: array(value, path, item)


def non_empty_array_decoder(item: Decoder[T]) -> Decoder[tuple[T, ...]]:
    return lambda value, path: non_empty_array(value, path, item)


def python_name(wire_path: str) -> str:
    """A path of the API's, e.g. ``query.licensePlate``, in this library's
    names: ``license_plate``."""
    path = wire_path
    for prefix in ("query.", "path.", "header."):
        if path.startswith(prefix):
            path = path[len(prefix) :]
    parts: list[str] = []
    for part in path.split("."):
        if part.isdigit():
            parts.append(part)
            continue
        snake = ""
        for index, char in enumerate(part):
            if char.isupper() and index > 0 and not part[index - 1].isupper():
                snake += "_"
            snake += "_" if char == "-" else char.lower()
        parts.append(snake + "_" if snake in ("from",) else snake)
    return ".".join(parts)
