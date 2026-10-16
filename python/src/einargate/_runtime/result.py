from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Generic, Literal, NoReturn, TypeAlias, TypeVar

from .errors import EinarGateError

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)


@dataclass(frozen=True, slots=True)
class ResponseInfo:
    """What the API's response said besides its body."""

    status: int
    request_id: str | None = None
    """API Gateway's request id, for support"""
    replayed: bool = False
    """``True`` when the API replayed the stored response of an earlier
    request with the same idempotency key: the write had already happened"""


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """A successful call: ``data`` is what the API answered."""

    data: T
    response: ResponseInfo
    success: ClassVar[Literal[True]] = True

    def unwrap(self) -> T:
        """The data; a success never raises."""
        return self.data


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """A failed call: ``error.type`` says what happened."""

    error: E
    idempotency_key: str | None = None
    """The ``Idempotency-Key`` a write was sent with. When the write may have
    happened (a timeout, a network error after sending, a 5xx), check its
    effect before sending it again, and send it with this key: the API
    replays the first response if that write completed, but runs it again if
    the API failed after running it, because it does not keep the key of a
    failed write. After ``unexpected-response`` the write ran: check its
    effect, but do not send it again."""
    success: ClassVar[Literal[False]] = False

    def unwrap(self) -> NoReturn:
        """Raises an ``EinarGateError`` that carries the error."""
        raise EinarGateError(self.error)


Result: TypeAlias = Ok[T] | Err[E]
"""What every call returns: match ``Ok(data)`` or ``Err(error)``, or check
``isinstance(result, Err)``, which narrows the type (``result.success`` alone
does not). Nothing the API or the network does makes a call raise."""
