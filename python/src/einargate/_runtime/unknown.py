from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UnknownValue:
    """A value that this version of the library does not know.

    An enum value or a union variant that the API added after this version
    was released. The API may add them within v1, so every enum and union in
    a response includes ``UnknownValue``, and an exhaustive ``match`` needs a
    case for it. It is not a ``str``, so that comparing it with a known value
    is never true by accident; ``str(value)`` gives the value as sent.
    """

    unknown: str
    """The value as the API sent it"""

    def __str__(self) -> str:
        return self.unknown


def is_unknown(value: object) -> bool:
    """Whether a value is one this version of the library does not know."""
    return isinstance(value, UnknownValue)
