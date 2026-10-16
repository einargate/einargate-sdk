"""A stand-in for the Einar Gate API, for testing code that uses the client.

The API has no sandbox. Register what each operation answers; the client
then runs exactly as against the API: it encodes requests, decodes responses
and maps problems the same way::

    from einargate import Err, GateRef
    from einargate.testing import MockEinarGate, MockReply

    mock = MockEinarGate()
    mock.on("open_gate", lambda call: MockReply.problem("gate-not-operable"))
    with mock.client() as eg:
        result = eg.gates.open(GateRef(gate_id="g1"))
    assert isinstance(result, Err) and result.error.type == "gate-not-operable"

A call to an operation with no ``on(...)`` comes back as a ``network`` error
whose message names the operation to register.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import unquote

import httpx

from ._client import AppInfo, AsyncEinarGate, EinarGate
from ._generated.mock import MockOperations, MockReply
from ._generated.models import PROBLEM_TYPES
from ._generated.operations import OPERATIONS, OperationName
from ._runtime.api_key import checksum
from ._runtime.mock import MockCall

MOCK_LOCATION_ID = "mock-location"
"""The location the mock clients are bound to unless told otherwise"""

_BASE_URL = "https://api.einargate.test/v1"


def _mock_api_key() -> str:
    body = "egk_" + "mock".ljust(30, "0")
    return body + checksum(body)


MOCK_API_KEY = _mock_api_key()
"""A well-formed API key value that no real API key has"""


MockHandler = Callable[[MockCall], MockReply[Any, str]]


class MockEinarGate(MockOperations):
    """Answers the client's requests from handlers registered per operation.

    ``on`` is typed per operation: a handler's ``MockReply.ok`` data must be
    the operation's, and ``MockReply.problem`` one of its problem types.
    """

    def __init__(self) -> None:
        self.calls: list[MockCall] = []
        """Every request the client sent, in order"""
        self._handlers: dict[str, MockHandler] = {}
        self.transport = httpx.MockTransport(self._handle)

    def _register(self, operation: str, handler: MockHandler) -> None:
        if operation not in OPERATIONS:
            raise ValueError(f"MockEinarGate: there is no operation {operation!r}")
        self._handlers[operation] = handler

    def calls_of(self, operation: OperationName) -> list[MockCall]:
        """The calls of one operation."""
        return [call for call in self.calls if call.operation == operation]

    def client(
        self,
        *,
        location_id: str | None = MOCK_LOCATION_ID,
        max_retries: int = 0,
        timeout: float = 30.0,
        app_info: AppInfo | None = None,
    ) -> EinarGate:
        """A client bound to ``MOCK_LOCATION_ID`` that does not retry."""
        return EinarGate(
            MOCK_API_KEY,
            location_id=location_id,
            base_url=_BASE_URL,
            timeout=timeout,
            max_retries=max_retries,
            http_client=httpx.Client(transport=self.transport),
            app_info=app_info,
        )

    def async_client(
        self,
        *,
        location_id: str | None = MOCK_LOCATION_ID,
        max_retries: int = 0,
        timeout: float = 30.0,
        app_info: AppInfo | None = None,
    ) -> AsyncEinarGate:
        """``client`` for the async client."""
        return AsyncEinarGate(
            MOCK_API_KEY,
            location_id=location_id,
            base_url=_BASE_URL,
            timeout=timeout,
            max_retries=max_retries,
            http_client=httpx.AsyncClient(transport=self.transport),
            app_info=app_info,
        )

    def _handle(self, request: httpx.Request) -> httpx.Response:
        # As sent, still percent-encoded
        path = request.url.raw_path.decode().split("?")[0].removeprefix("/v1")
        match = _match_operation(request.method, path)
        if match is None:
            raise httpx.ConnectError(
                f"MockEinarGate: no operation is {request.method} {path}"
            )
        operation, params = match
        content = request.read()
        call = MockCall(
            operation=operation,
            method=request.method,
            path=path,
            params=params,
            query=dict(request.url.params),
            body=json.loads(content) if content else None,
            headers={name.lower(): value for name, value in request.headers.items()},
        )
        self.calls.append(call)

        handler = self._handlers.get(operation)
        if handler is None:
            raise httpx.ConnectError(
                f"MockEinarGate: nothing answers {operation} "
                f"({request.method} {path}); call mock.on({operation!r}, ...) first"
            )
        return _response(operation, handler(call))


def _match_operation(method: str, path: str) -> tuple[str, dict[str, str]] | None:
    for name, spec in OPERATIONS.items():
        if spec.method != method:
            continue
        names = re.findall(r"\{([^{}]+)\}", spec.path)
        pattern = re.sub(r"\{[^{}]+\}", "([^/]+)", spec.path)
        found = re.fullmatch(pattern, path)
        if found:
            return name, {
                key: unquote(value)
                for key, value in zip(names, found.groups(), strict=True)
            }
    return None


def _response(operation: str, reply: MockReply[Any, str]) -> httpx.Response:
    spec = OPERATIONS[operation]
    headers = {"x-amzn-RequestId": "mock-request", **reply.headers}
    if reply.kind == "data":
        body: Any = (
            spec.encode(reply.data) if spec.encode and reply.data is not None else None
        )
        if spec.status == 204 or body is None:
            return httpx.Response(spec.status, headers=headers)
        return httpx.Response(spec.status, json=body, headers=headers)
    if reply.kind == "problem":
        problem = PROBLEM_TYPES[reply.problem_type or ""]
        return httpx.Response(
            problem.status,
            content=json.dumps(
                {
                    "type": problem.docs_url,
                    "title": problem.title,
                    "status": problem.status,
                    **({"detail": reply.detail} if reply.detail is not None else {}),
                    "requestId": "mock-request",
                    **reply.extensions,
                }
            ),
            headers={"Content-Type": "application/problem+json", **headers},
        )
    if reply.body is None:
        return httpx.Response(reply.status or 200, headers=headers)
    if isinstance(reply.body, str):
        return httpx.Response(reply.status or 200, text=reply.body, headers=headers)
    return httpx.Response(reply.status or 200, json=reply.body, headers=headers)


__all__ = [
    "MOCK_API_KEY",
    "MOCK_LOCATION_ID",
    "MockCall",
    "MockEinarGate",
    "MockHandler",
    "MockReply",
]
