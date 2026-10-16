"""What the resources share: the transport, and the API key's location.

Every location path needs the location. It comes from the client's options
or, on first use, from ``GET /me``. The lookup is shared by the calls that
wait for it and runs with the client's own timeout; each caller waits for it
with its own timeout. A failed lookup is not kept, even one that failed after its
callers stopped waiting, so the next call tries again.
"""

from __future__ import annotations

import asyncio
import contextlib
import contextvars
import sys
import threading
from collections.abc import Awaitable, Callable
from concurrent.futures import CancelledError as FutureCancelled
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from typing import Any

from .errors import RequestTimeout
from .result import Err, Ok, ResponseInfo, Result
from .transport import (
    AsyncTransport,
    Transport,
    attempt_timeout,
    clear_deadline,
    closed_error,
)


def _waited_too_long(timeout: float) -> Err[RequestTimeout]:
    return Err(
        RequestTimeout(
            message=(
                "No answer from the Einar Gate API about the API key's location "
                f"within {timeout} s"
            ),
            timeout_seconds=timeout,
        )
    )


def _failed(lookup: Future[Result[str, Any]] | asyncio.Task[Result[str, Any]]) -> bool:
    """Whether a lookup is over without the location"""
    if not lookup.done():
        return False
    if lookup.cancelled() or lookup.exception() is not None:
        return True
    return not isinstance(lookup.result(), Ok)


def _cancelling() -> bool:
    """Whether the current task is being cancelled; Python 3.10 cannot tell"""
    if sys.version_info < (3, 11):
        return False
    task = asyncio.current_task()
    return task is not None and task.cancelling() > 0


class ClientContext:
    def __init__(
        self,
        transport: Transport,
        location_id: str | None,
        look_up_location: Callable[[], Result[str, Any]],
    ) -> None:
        self.transport = transport
        self.send = transport.send
        self._fixed = location_id
        self._look_up = look_up_location
        self._location: Ok[str] | None = None
        self._lookup: Future[Result[str, Any]] | None = None
        self._executor: ThreadPoolExecutor | None = None
        self._closed = False
        self._lock = threading.Lock()

    def _run_lookup(self) -> Result[str, Any]:
        # Without the caller's deadline, which a new thread may inherit: the
        # lookup serves every caller
        clear_deadline()
        return self._look_up()

    def location_id(self, timeout: float | None) -> Result[str, Any]:
        if self._fixed is not None:
            return Ok(self._fixed, ResponseInfo(status=200))
        with self._lock:
            if self._location is not None:
                return self._location
            if self._closed:
                return closed_error()
            if self._lookup is not None and _failed(self._lookup):
                self._lookup = None
            if self._lookup is None:
                if self._executor is None:
                    self._executor = ThreadPoolExecutor(
                        max_workers=1, thread_name_prefix="einargate-location"
                    )
                self._lookup = self._executor.submit(self._run_lookup)
            lookup = self._lookup
        wait = attempt_timeout(timeout if timeout is not None else 1e9)
        if wait is None:
            return _waited_too_long(timeout or 0)
        try:
            result = lookup.result(timeout=wait)
        except FutureTimeout:
            return _waited_too_long(wait)
        except FutureCancelled:
            # close() cancelled the lookup before its worker took it
            return closed_error()
        with self._lock:
            if isinstance(result, Ok):
                self._location = result
            if self._lookup is lookup:
                self._lookup = None
        return result

    def close(self) -> None:
        """Stops a lookup in progress at its next retry and its worker."""
        self.transport.close()
        with self._lock:
            self._closed = True
        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)


class AsyncClientContext:
    def __init__(
        self,
        transport: AsyncTransport,
        location_id: str | None,
        look_up_location: Callable[[], Awaitable[Result[str, Any]]],
    ) -> None:
        self.transport = transport
        self.send = transport.send
        self._fixed = location_id
        self._look_up = look_up_location
        self._location: Ok[str] | None = None
        self._lookup: asyncio.Task[Result[str, Any]] | None = None

    async def location_id(self, timeout: float | None) -> Result[str, Any]:
        if self._fixed is not None:
            return Ok(self._fixed, ResponseInfo(status=200))
        if self._location is not None:
            return self._location
        if self.transport.closed:
            return closed_error()
        if self._lookup is not None and _failed(self._lookup):
            self._lookup = None
        if self._lookup is None:
            # Without the caller's deadline: the lookup serves every caller
            context = contextvars.copy_context()
            context.run(clear_deadline)
            self._lookup = context.run(asyncio.ensure_future, self._look_up())
        lookup = self._lookup
        try:
            # Shielded: a caller that stops waiting does not stop the lookup
            result = await asyncio.wait_for(asyncio.shield(lookup), timeout)
        except asyncio.TimeoutError:
            return _waited_too_long(timeout or 0)
        except asyncio.CancelledError:
            # aclose() cancelled the lookup, and nothing cancelled this caller
            if lookup.cancelled() and not _cancelling():
                return closed_error()
            raise
        if isinstance(result, Ok):
            self._location = result
        if self._lookup is lookup:
            self._lookup = None
        return result

    async def aclose(self) -> None:
        """Cancels a lookup in progress."""
        self.transport.close()
        lookup, self._lookup = self._lookup, None
        if lookup is not None and not lookup.done():
            lookup.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await lookup
