"""The failures a call can return (ADR-0019, ADR-0022).

Every call returns a result whose error is one of its route's problem types
or one of the errors below; ``error.type`` tells them apart.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, TypeAlias


@dataclass(frozen=True, slots=True, kw_only=True)
class ProblemBase:
    """The members of every problem (RFC 9457 problem details)."""

    title: str
    detail: str | None = None
    """What happened in this case"""
    instance: str | None = None
    """The request path"""
    request_id: str
    """Send it to support"""
    hint: str
    """What to do about a problem of this type"""
    docs_url: str
    """The error catalogue's page of the type"""
    retry_after_seconds: int | None = None
    """Seconds to wait, from ``Retry-After``, when the response had one"""
    message: str
    """One line for logs: the type, status, detail, hint and request id"""
    body: Mapping[str, object]
    """The body as sent, including members this version does not know"""

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True, kw_only=True)
class UnknownProblem:
    """An error response that is not a problem of a declared type.

    A type added after this version was released, or a body that is not a
    problem at all (a proxy's error page). Handle it by its status.
    """

    type: Literal["unknown-problem"] = "unknown-problem"
    status: int
    problem_type: str | None = None
    """The body's ``type``, when it had one"""
    title: str | None = None
    detail: str | None = None
    request_id: str | None = None
    retry_after_seconds: int | None = None
    message: str
    body: object

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True, kw_only=True)
class NetworkError:
    """The request did not reach the API, or its response did not arrive."""

    type: Literal["network"] = "network"
    message: str
    request_sent: bool
    """``False`` when no connection could be made, so the request was not
    sent; ``True`` when it may have reached the API, so a write may have
    happened"""
    cause: BaseException

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True, kw_only=True)
class RequestTimeout:
    """No response within the timeout, for the last attempt."""

    type: Literal["timeout"] = "timeout"
    message: str
    timeout_seconds: float

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True, kw_only=True)
class UnexpectedResponse:
    """A success response that does not match the API's contract.

    It is a bug on the API's side: send the request id to support.
    """

    type: Literal["unexpected-response"] = "unexpected-response"
    status: int
    request_id: str | None = None
    path: str
    """Where the body differs from the contract, e.g. ``items.0.gateId``"""
    message: str
    body: object

    def __str__(self) -> str:
        return self.message


CallError: TypeAlias = (
    UnknownProblem | NetworkError | RequestTimeout | UnexpectedResponse
)
"""The errors every call can return besides its problem types"""


class EinarGateError(Exception):
    """Raised by ``unwrap()`` on a failure; ``error`` is the result's error."""

    def __init__(self, error: object) -> None:
        super().__init__(str(error))
        self.error = error
