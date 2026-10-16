"""Sends one call: builds the request, retries what is safe to retry, and
turns the response into a result. Nothing here raises for anything the API
or the network does (ADR-0022)."""

from __future__ import annotations

import asyncio
import email.utils
import json
import threading
import time
from collections.abc import Awaitable, Callable, Generator, Mapping
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from typing import Any, Generic, Literal, TypeVar, cast
from urllib.parse import quote

import httpx

from .decode import DecodeError, JsonObject
from .errors import NetworkError, RequestTimeout, UnexpectedResponse, UnknownProblem
from .result import Err, Ok, ResponseInfo, Result

T = TypeVar("T")

IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
REPLAYED_HEADER = "Idempotent-Replayed"
REQUEST_ID_HEADER = "x-amzn-requestid"
MAX_RETRY_AFTER_SECONDS = 60
"""A longer ``Retry-After`` is returned to the caller rather than waited for"""
BASE_BACKOFF_SECONDS = 0.5
MAX_BACKOFF_SECONDS = 8.0


@dataclass(slots=True)
class Deadline:
    """A monotonic time that bounds every attempt and retry of the calls made
    while it is set, and whether it cut one short"""

    at: float
    cut_short: bool = False
    _responses: set[httpx.Response] = field(default_factory=lambda: set())
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def remaining(self) -> float:
        return self.at - time.monotonic()

    def track(self, response: httpx.Response) -> None:
        with self._lock:
            self._responses.add(response)

    def untrack(self, response: httpx.Response) -> None:
        with self._lock:
            self._responses.discard(response)

    def abort(self) -> None:
        """Closes the responses still being read, which ends their reads."""
        self.cut_short = True
        with self._lock:
            responses = list(self._responses)
        for response in responses:
            response.close()


_DEADLINE: ContextVar[Deadline | None] = ContextVar("einargate_deadline", default=None)


@contextmanager
def deadline(seconds: float) -> Generator[Deadline, None, None]:
    """Bounds the calls made in the block, retries and their waits included."""
    current = _DEADLINE.get()
    at = time.monotonic() + seconds
    scope = Deadline(at if current is None else min(at, current.at))
    token = _DEADLINE.set(scope)
    try:
        yield scope
    finally:
        _DEADLINE.reset(token)


def clear_deadline() -> None:
    """Leaves the current context without a deadline, for work that outlives
    the call that starts it"""
    _DEADLINE.set(None)


def attempt_timeout(seconds: float) -> float | None:
    """The attempt's timeout under the current deadline, or ``None`` when the
    deadline has passed"""
    scope = _DEADLINE.get()
    if scope is None:
        return seconds
    remaining = scope.remaining()
    if remaining <= 0:
        scope.cut_short = True
        return None
    return min(seconds, remaining)


def _allows(delay: float) -> bool:
    """Whether the current deadline leaves time to retry after ``delay``"""
    scope = _DEADLINE.get()
    if scope is None or delay < scope.remaining():
        return True
    scope.cut_short = True
    return False


def closed_error() -> Err[Any]:
    return Err(
        NetworkError(
            message="The Einar Gate client was closed",
            request_sent=False,
            cause=RuntimeError("closed"),
        )
    )


def _deadline_passed(seconds: float, idempotency_key: str | None) -> Err[Any]:
    """Nothing was sent, so a write gets its key without the resend hint"""
    return Err(
        RequestTimeout(
            message="The time given to the call ran out before it was sent.",
            timeout_seconds=seconds,
        ),
        idempotency_key=idempotency_key,
    )


@dataclass(frozen=True, slots=True)
class ProblemInfo:
    status: int | None = None
    """The response's HTTP status, which must be the problem type's"""
    retry_after_seconds: int | None = None


ProblemDecoder = Callable[[JsonObject, ProblemInfo], Any]


@dataclass(frozen=True, slots=True, kw_only=True)
class OperationSpec(Generic[T]):
    """One operation of the API, as the generated code describes it."""

    id: str
    method: str
    path: str
    """Relative to the base URL, e.g. ``/locations/{locationId}/gates``"""
    status: int
    """The success status the contract declares"""
    authenticated: bool
    idempotent: bool
    """A write that accepts an ``Idempotency-Key``"""
    decode: Callable[[object, str], T] | None = None
    """Decodes the success body; ``None`` when the success has none"""
    encode: Callable[[Any], object] | None = None
    """Writes success data as the API sends it, for the mock"""
    problems: Mapping[str, ProblemDecoder]
    """The problem types the operation declares, by slug"""


@dataclass(frozen=True, slots=True, kw_only=True)
class TransportConfig:
    api_key: str
    base_url: str
    timeout: float
    max_retries: int
    user_agent: str
    problem_type_base_uri: str
    random: Callable[[], float]
    new_idempotency_key: Callable[[], str]


@dataclass(frozen=True, slots=True)
class _Request:
    method: str
    url: str
    headers: dict[str, str]
    content: bytes | None


def _build_request(
    config: TransportConfig,
    spec: OperationSpec[Any],
    path: Mapping[str, str] | None,
    query: Mapping[str, str | None] | None,
    body: object,
    idempotency_key: str | None,
) -> _Request:
    url_path = spec.path
    for name in _path_parameters(spec.path):
        value = (path or {}).get(name)
        if value is None:
            raise TypeError(f"{spec.id}: the path parameter {name} is missing")
        url_path = url_path.replace("{" + name + "}", quote(value, safe=""))

    params = {name: value for name, value in (query or {}).items() if value is not None}
    url = config.base_url + url_path
    if params:
        url += "?" + str(httpx.QueryParams(params))

    headers = {
        "Accept": "application/json, application/problem+json",
        "User-Agent": config.user_agent,
    }
    if spec.authenticated:
        headers["Authorization"] = f"Bearer {config.api_key}"
    if idempotency_key is not None:
        headers[IDEMPOTENCY_KEY_HEADER] = idempotency_key
    content = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        content = json.dumps(body, ensure_ascii=False).encode("utf-8")

    return _Request(spec.method, url, headers, content)


def _path_parameters(path: str) -> list[str]:
    names: list[str] = []
    rest = path
    while "{" in rest:
        start = rest.index("{")
        end = rest.index("}", start)
        names.append(rest[start + 1 : end])
        rest = rest[end + 1 :]
    return names


def _parse_response(
    config: TransportConfig, spec: OperationSpec[T], response: httpx.Response
) -> Result[T, Any]:
    request_id = response.headers.get(REQUEST_ID_HEADER)
    if response.is_success and response.status_code != spec.status:
        return Err(
            UnexpectedResponse(
                status=response.status_code,
                request_id=request_id,
                path="",
                message=(
                    f"The Einar Gate API answered {spec.id} with "
                    f"{response.status_code}, where its contract says "
                    f"{spec.status}. This is a bug on the API's side"
                    + (f"; request id {request_id}." if request_id else ".")
                ),
                body=response.text,
            )
        )
    if response.is_success:
        info = ResponseInfo(
            status=response.status_code,
            request_id=request_id,
            replayed=response.headers.get(REPLAYED_HEADER) == "true",
        )
        if spec.decode is None:
            return Ok(None, info)  # type: ignore[arg-type]
        body = _parse_json(response.text)
        try:
            if body is _NOT_JSON:
                raise DecodeError("", "a JSON body")
            return Ok(spec.decode(body, ""), info)
        except DecodeError as error:
            return Err(
                UnexpectedResponse(
                    status=response.status_code,
                    request_id=request_id,
                    path=error.path,
                    message=(
                        f"The Einar Gate API answered {spec.id} with a body "
                        f"that does not match its contract ({error}). This "
                        "is a bug on the API's side"
                        + (f"; request id {request_id}." if request_id else ".")
                    ),
                    body=response.text if body is _NOT_JSON else body,
                )
            )

    parsed = _parse_json(response.text)
    error_body = response.text if parsed is _NOT_JSON else parsed
    retry_after = _parse_retry_after(response.headers.get("Retry-After"))
    info = ProblemInfo(status=response.status_code, retry_after_seconds=retry_after)

    problem = _json_object(error_body)
    if problem is not None:
        problem_type = problem.get("type")
        base = config.problem_type_base_uri
        if isinstance(problem_type, str) and problem_type.startswith(base):
            decoder = spec.problems.get(problem_type[len(base) :])
            if decoder is not None:
                try:
                    return Err(decoder(problem, info))
                except DecodeError:
                    pass

    return Err(
        unknown_problem(response.status_code, error_body, request_id, retry_after)
    )


def unknown_problem(
    status: int,
    body: object,
    request_id: str | None = None,
    retry_after_seconds: int | None = None,
) -> UnknownProblem:
    """An error body that is not a problem of a declared type."""
    problem = _json_object(body) or {}

    def text(key: str) -> str | None:
        value = problem.get(key)
        return value if isinstance(value, str) else None

    problem_type = text("type")
    title = text("title")
    detail = text("detail")
    request_id = text("requestId") or request_id
    message = f"The Einar Gate API answered {status}"
    if problem_type:
        message += f" with a problem this version does not know ({problem_type})"
    if detail or title:
        message += f": {detail or title}"
    message += ". Handle it by its status."
    if request_id:
        message += f" Request id {request_id}."

    return UnknownProblem(
        status=status,
        problem_type=problem_type,
        title=title,
        detail=detail,
        request_id=request_id,
        retry_after_seconds=retry_after_seconds,
        message=message,
        body=body,
    )


def _retry_delay(
    config: TransportConfig, spec: OperationSpec[Any], error: Any, attempt: int
) -> float | None:
    """Seconds to wait before retrying, or ``None`` when it must not be.

    A read is retried after any transient failure. A write is retried only
    when it cannot have run: the usage plan refused it (``rate-limited`` per
    second, ``provisioning``), an earlier attempt with the same idempotency
    key is still running, or no connection could be made. After a timeout, a
    network error once the request was sent, or a 5xx, a write may have run
    (the API releases the idempotency key of a write that fails, so a retry
    would run it again), and opening a gate twice is not a retry's call to
    make: the failure goes back to the caller with its idempotency key.
    """
    if attempt >= config.max_retries:
        return None
    read = spec.method == "GET"

    def backoff() -> float:
        ceiling = min(MAX_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * 2**attempt)
        return ceiling / 2 + ceiling / 2 * config.random()

    def after(seconds: int | None) -> float | None:
        if seconds is None:
            return backoff()
        return float(seconds) if seconds <= MAX_RETRY_AFTER_SECONDS else None

    retry_after = getattr(error, "retry_after_seconds", None)
    kind = error.type
    if kind == "network":
        return backoff() if read or not error.request_sent else None
    if kind in ("timeout", "internal"):
        return backoff() if read else None
    if kind == "service-unavailable":
        return after(retry_after) if read else None
    if kind == "rate-limited":
        return (
            after(retry_after) if getattr(error, "window", None) == "second" else None
        )
    if kind in ("provisioning", "idempotency-key-in-flight"):
        return after(retry_after)
    if kind == "unknown-problem":
        if error.status == 429 or (read and error.status in (502, 503, 504)):
            return after(retry_after)
    return None


def _write_outcome(error: Any) -> Literal["ran", "maybe", "no"]:
    """Whether a failed write happened: ``ran`` when the API answered success
    in a form the contract does not allow, ``maybe`` when the API may have run
    it and then failed or its answer was lost"""
    kind = error.type
    if kind == "unexpected-response":
        return "ran"
    if kind == "network":
        return "maybe" if error.request_sent else "no"
    if kind in ("timeout", "internal", "service-unavailable"):
        return "maybe"
    if kind == "unknown-problem" and error.status >= 500:
        return "maybe"
    return "no"


def _finish(result: Err[Any], idempotency_key: str | None) -> Err[Any]:
    """The failure of a write, with its key and, if it ran or may have, a
    message that says what to do before sending it again."""
    if idempotency_key is None:
        return result
    error = result.error
    outcome = _write_outcome(error)
    if outcome == "ran":
        error = replace(
            error,
            message=(
                f"{error.message} The write ran: do not send it again, but "
                "check its effect (for a gate opening, the events)."
            ),
        )
    elif outcome == "maybe":
        error = replace(
            error,
            message=(
                f"{error.message} The write may have happened: check its effect "
                "(for a gate opening, the events) before sending it again. If "
                f"you do, send it with idempotency_key='{idempotency_key}': the "
                "API replays the first response if that write completed, but "
                "runs it again if the API failed after running it."
            ),
        )
    return Err(error, idempotency_key=idempotency_key)


_NOT_JSON = object()


def _json_object(value: object) -> dict[str, object] | None:
    return cast("dict[str, object]", value) if isinstance(value, dict) else None


def _parse_json(text: str) -> object:
    if text == "":
        return _NOT_JSON
    try:
        return json.loads(text)
    except ValueError:
        return _NOT_JSON


def _parse_retry_after(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if value.isdigit():
        return int(value)
    try:
        date = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return max(0, int(date.timestamp() - time.time() + 0.999))


def _transport_error(error: httpx.HTTPError, timeout: float) -> Any:
    if isinstance(error, (httpx.ConnectError, httpx.ConnectTimeout)):
        return NetworkError(
            message=f"The Einar Gate API could not be reached: {error}",
            request_sent=False,
            cause=error,
        )
    if isinstance(error, httpx.PoolTimeout):
        return NetworkError(
            message=f"No connection to the Einar Gate API was free within {timeout} s",
            request_sent=False,
            cause=error,
        )
    if isinstance(error, httpx.TimeoutException):
        return RequestTimeout(
            message=f"No response from the Einar Gate API within {timeout} s",
            timeout_seconds=timeout,
        )
    cause = error.__cause__ or error.__context__
    detail = f"{error} ({cause})" if cause and str(cause) != str(error) else str(error)
    return NetworkError(
        message=f"The Einar Gate API could not be reached: {detail}",
        request_sent=True,
        cause=error,
    )


class Transport:
    """Sends calls with an ``httpx.Client``."""

    def __init__(
        self,
        config: TransportConfig,
        client: httpx.Client,
        sleep: Callable[[float], object] | None = None,
    ) -> None:
        self.config = config
        self.client = client
        self._closed = threading.Event()
        # Wakes up when the client closes, so a retry's wait cannot keep it
        self._sleep = sleep or self._closed.wait

    def close(self) -> None:
        """Stops the calls in progress at their next retry."""
        self._closed.set()

    def _attempt(
        self, spec: OperationSpec[T], request: _Request, limit: float
    ) -> Result[T, Any]:
        response = self.client.send(
            self.client.build_request(
                request.method,
                request.url,
                headers=request.headers,
                content=request.content,
                timeout=limit,
            ),
            stream=True,
        )
        # Under a deadline, the response can be closed from the thread that
        # waits for it, which ends a read that would outlast the deadline
        scope = _DEADLINE.get()
        if scope is not None:
            scope.track(response)
        try:
            response.read()
        finally:
            if scope is not None:
                scope.untrack(response)
            response.close()
        return _parse_response(self.config, spec, response)

    def send(
        self,
        spec: OperationSpec[T],
        *,
        path: Mapping[str, str] | None = None,
        query: Mapping[str, str | None] | None = None,
        body: object = None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[T, Any]:
        if spec.idempotent and idempotency_key is None:
            idempotency_key = self.config.new_idempotency_key()
        request = _build_request(self.config, spec, path, query, body, idempotency_key)
        seconds = self.config.timeout if timeout is None else timeout

        attempt = 0
        while True:
            if self._closed.is_set():
                return _finish(closed_error(), idempotency_key)
            limit = attempt_timeout(seconds)
            if limit is None:
                return _deadline_passed(seconds, idempotency_key)
            try:
                result = self._attempt(spec, request, limit)
            except httpx.HTTPError as error:
                result = Err(_transport_error(error, limit))
            if isinstance(result, Ok):
                return result
            delay = _retry_delay(self.config, spec, result.error, attempt)
            if delay is None or not _allows(delay):
                return _finish(result, idempotency_key)
            self._sleep(delay)
            attempt += 1


class AsyncTransport:
    """Sends calls with an ``httpx.AsyncClient``."""

    def __init__(
        self,
        config: TransportConfig,
        client: httpx.AsyncClient,
        sleep: Callable[[float], Awaitable[object]] | None = None,
    ) -> None:
        self.config = config
        self.client = client
        self._closing = asyncio.Event()
        # Wakes up when the client closes, so a retry's wait cannot keep it
        self._sleep = sleep or self._pause

    @property
    def closed(self) -> bool:
        return self._closing.is_set()

    def close(self) -> None:
        """Stops the calls in progress at their next retry."""
        self._closing.set()

    async def _pause(self, seconds: float) -> None:
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._closing.wait(), seconds)

    async def send(
        self,
        spec: OperationSpec[T],
        *,
        path: Mapping[str, str] | None = None,
        query: Mapping[str, str | None] | None = None,
        body: object = None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[T, Any]:
        if spec.idempotent and idempotency_key is None:
            idempotency_key = self.config.new_idempotency_key()
        request = _build_request(self.config, spec, path, query, body, idempotency_key)
        seconds = self.config.timeout if timeout is None else timeout

        attempt = 0
        while True:
            if self.closed:
                return _finish(closed_error(), idempotency_key)
            limit = attempt_timeout(seconds)
            if limit is None:
                return _deadline_passed(seconds, idempotency_key)
            try:
                response = await self.client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    content=request.content,
                    timeout=limit,
                )
                await response.aread()
                result = _parse_response(self.config, spec, response)
            except httpx.HTTPError as error:
                result = Err(_transport_error(error, limit))
            if isinstance(result, Ok):
                return result
            delay = _retry_delay(self.config, spec, result.error, attempt)
            if delay is None or not _allows(delay):
                return _finish(result, idempotency_key)
            await self._sleep(delay)
            attempt += 1
