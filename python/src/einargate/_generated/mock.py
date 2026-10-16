# Generated from the Einar Gate OpenAPI document by packages/aws/scripts/sdk
# in the Einar Gate monorepo. Do not edit: change the route registry or the
# generator and run `npm run public-api:lock --workspace @einargate/aws`.

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, NoReturn, TypeVar, overload

from .._runtime import encode as e
from .._runtime.mock import MockCall
from .._runtime.page import Page
from . import models as t
from .operations import OperationName

D = TypeVar("D", covariant=True)
P = TypeVar("P", bound=str, covariant=True)
_D = TypeVar("_D")
_Plain = TypeVar(
    "_Plain",
    bound=Literal[
        "conflict",
        "forbidden",
        "gate-not-operable",
        "idempotency-key-in-flight",
        "idempotency-key-reuse",
        "internal",
        "invalid-owner",
        "limit-exceeded",
        "not-found",
        "provisioning",
        "service-unavailable",
        "unauthorized",
    ],
)


@dataclass(frozen=True, slots=True, kw_only=True)
class MockReply(Generic[D, P]):
    """What a mocked operation answers: build it with ``ok``, ``problem`` or ``raw``.
    ``MockEinarGate.on`` checks it against the operation: its data type and the problem
    types it declares.
    """

    kind: Literal["data", "problem", "raw"]
    data: D | None = None
    problem_type: P | None = None
    detail: str | None = None
    extensions: Mapping[str, object] = field(default_factory=lambda: {})
    """The problem’s own members, as sent"""
    status: int | None = None
    body: object = None
    headers: Mapping[str, str] = field(default_factory=lambda: {})

    @staticmethod
    def ok(
        data: _D = None, *, headers: Mapping[str, str] | None = None
    ) -> MockReply[_D, NoReturn]:
        """Success, with the operation’s data as the client returns it."""
        return MockReply(kind="data", data=data, headers=headers or {})

    @overload
    @staticmethod
    def problem(
        problem_type: Literal["invalid-request"],
        *,
        errors: Sequence[t.InvalidRequestIssue],
        detail: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MockReply[NoReturn, Literal["invalid-request"]]: ...

    @overload
    @staticmethod
    def problem(
        problem_type: Literal["rate-limited"],
        *,
        window: t.RateLimitWindow,
        detail: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MockReply[NoReturn, Literal["rate-limited"]]: ...

    @overload
    @staticmethod
    def problem(
        problem_type: _Plain,
        *,
        detail: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MockReply[NoReturn, _Plain]: ...

    @staticmethod
    def problem(
        problem_type: str,
        *,
        detail: str | None = None,
        headers: Mapping[str, str] | None = None,
        **extensions: Any,
    ) -> MockReply[Any, Any]:
        """A problem of a type the operation declares, e.g. ``not-found``, with the members
        of its type: ``window=`` for ``rate-limited``, ``errors=`` for
        ``invalid-request``.
        """
        return MockReply(
            kind="problem",
            problem_type=problem_type,
            detail=detail,
            extensions=_encode_extensions(problem_type, extensions),
            headers=headers or {},
        )

    @staticmethod
    def raw(
        status: int, body: object = None, *, headers: Mapping[str, str] | None = None
    ) -> MockReply[Any, Any]:
        """Any response at all, e.g. a body the contract does not allow."""
        return MockReply(kind="raw", status=status, body=body, headers=headers or {})


def _encode_extensions(
    problem_type: str, extensions: Mapping[str, Any]
) -> dict[str, object]:

    def member(name: str) -> Any:
        if name not in extensions:
            raise TypeError(f"MockReply.problem({problem_type!r}) needs {name}=")
        return extensions[name]

    if problem_type == "invalid-request":
        return {
            "errors": [
                t.encode_invalid_request_issue(item) for item in member("errors")
            ],
        }
    if problem_type == "rate-limited":
        return {"window": e.enum_value(member("window"))}
    return {}


_M = TypeVar("_M", bound="MockOperations")


class MockOperations:
    """``on`` for every operation, typed by its data and problems."""

    @overload
    def on(
        self: _M,
        operation: Literal["get_me"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Me,
                Literal[
                    "forbidden",
                    "internal",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["get_open_api_document"],
        handler: Callable[
            [MockCall],
            MockReply[
                Mapping[str, object],
                Literal["internal", "rate-limited", "service-unavailable"],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["get_location"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Location,
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["list_members"],
        handler: Callable[
            [MockCall],
            MockReply[
                Page[t.Member],
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["list_gates"],
        handler: Callable[
            [MockCall],
            MockReply[
                Page[t.Gate],
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["get_gate"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Gate,
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["open_gate"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Event,
                Literal[
                    "forbidden",
                    "gate-not-operable",
                    "idempotency-key-in-flight",
                    "idempotency-key-reuse",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["list_location_cameras"],
        handler: Callable[
            [MockCall],
            MockReply[
                Page[t.Camera],
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["list_gate_cameras"],
        handler: Callable[
            [MockCall],
            MockReply[
                Page[t.Camera],
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["get_camera"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Camera,
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["list_permissions"],
        handler: Callable[
            [MockCall],
            MockReply[
                Page[t.Permission],
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["create_location_permission"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.CreatePermissionResult,
                Literal[
                    "conflict",
                    "forbidden",
                    "idempotency-key-in-flight",
                    "idempotency-key-reuse",
                    "internal",
                    "invalid-owner",
                    "invalid-request",
                    "limit-exceeded",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["create_gate_permission"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.CreatePermissionResult,
                Literal[
                    "conflict",
                    "forbidden",
                    "idempotency-key-in-flight",
                    "idempotency-key-reuse",
                    "internal",
                    "invalid-owner",
                    "invalid-request",
                    "limit-exceeded",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["create_camera_permission"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.CreatePermissionResult,
                Literal[
                    "conflict",
                    "forbidden",
                    "idempotency-key-in-flight",
                    "idempotency-key-reuse",
                    "internal",
                    "invalid-owner",
                    "invalid-request",
                    "limit-exceeded",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["get_permission"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Permission,
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["replace_permission"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.Permission,
                Literal[
                    "conflict",
                    "forbidden",
                    "idempotency-key-in-flight",
                    "idempotency-key-reuse",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["delete_permission"],
        handler: Callable[
            [MockCall],
            MockReply[
                None,
                Literal[
                    "forbidden",
                    "idempotency-key-in-flight",
                    "idempotency-key-reuse",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["list_events"],
        handler: Callable[
            [MockCall],
            MockReply[
                Page[t.Event],
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    @overload
    def on(
        self: _M,
        operation: Literal["get_event"],
        handler: Callable[
            [MockCall],
            MockReply[
                t.EventWithAttachments,
                Literal[
                    "forbidden",
                    "internal",
                    "invalid-request",
                    "not-found",
                    "provisioning",
                    "rate-limited",
                    "service-unavailable",
                    "unauthorized",
                ],
            ],
        ],
    ) -> _M: ...

    def on(
        self: _M,
        operation: OperationName,
        handler: Callable[[MockCall], MockReply[Any, str]],
    ) -> _M:
        """Sets what an operation answers; the last handler set wins."""
        self._register(operation, handler)
        return self

    def _register(
        self, operation: str, handler: Callable[[MockCall], MockReply[Any, str]]
    ) -> None:
        raise NotImplementedError
