from __future__ import annotations

import os
import platform
import random
import uuid
from dataclasses import dataclass
from types import TracebackType
from typing import Any

import httpx

from ._generated import operations as o
from ._generated.resources import (
    AsyncCamerasResource,
    AsyncGatesResource,
    AsyncLocationResource,
    AsyncMembersResource,
    AsyncRootResource,
    CamerasResource,
    GatesResource,
    LocationResource,
    MembersResource,
    RootResource,
)
from ._helpers import (
    AsyncEventsResource,
    AsyncPermissionsResource,
    EventsResource,
    PermissionsResource,
)
from ._runtime.api_key import api_key_problem
from ._runtime.context import AsyncClientContext, ClientContext
from ._runtime.result import Ok, Result
from ._runtime.transport import AsyncTransport, Transport, TransportConfig
from ._version import __version__

DEFAULT_BASE_URL = "https://api.einargate.com/v1"
_PROBLEM_TYPE_BASE_URI = "https://developers.einargate.com/errors/"


@dataclass(frozen=True, slots=True)
class AppInfo:
    """Your integration, added to the ``User-Agent``."""

    name: str
    version: str | None = None


def _base_url(value: str) -> str:
    """The base URL without a trailing slash; a malformed one is refused here
    rather than at the first call"""
    try:
        url = httpx.URL(value)
    except httpx.InvalidURL as error:
        raise ValueError(f"base_url {value!r} is not a valid URL: {error}") from None
    if url.scheme not in ("http", "https") or not url.host:
        raise ValueError(
            f"base_url {value!r} must be an http or https URL with a host, "
            f"such as {DEFAULT_BASE_URL!r}"
        )
    return value.rstrip("/")


def _config(
    api_key: str | None,
    base_url: str | None,
    timeout: float,
    max_retries: int,
    app_info: AppInfo | None,
) -> TransportConfig:
    key = api_key if api_key is not None else os.environ.get("EINARGATE_API_KEY")
    if not key:
        raise ValueError(
            "EinarGate needs an API key: pass api_key or set the "
            "EINARGATE_API_KEY environment variable. API keys are created in "
            "the Einar Gate app, under the location's API keys."
        )
    problem = api_key_problem(key)
    if problem is not None:
        raise ValueError(
            f"The Einar Gate API key is not valid: {problem}. An API key value "
            "looks like egk_ followed by 36 letters and digits."
        )
    url = _base_url(base_url or DEFAULT_BASE_URL)
    app = ""
    if app_info is not None:
        app = f" {app_info.name}" + (f"/{app_info.version}" if app_info.version else "")
    return TransportConfig(
        api_key=key,
        base_url=url,
        timeout=timeout,
        max_retries=max_retries,
        user_agent=(
            f"einargate-python/{__version__} python/{platform.python_version()}{app}"
        ),
        problem_type_base_uri=_PROBLEM_TYPE_BASE_URI,
        random=random.random,
        new_idempotency_key=lambda: str(uuid.uuid4()),
    )


class EinarGate(RootResource):
    """The Einar Gate API client.

    Every call returns a ``Result``: match ``Ok(data)`` or ``Err(error)``, or
    check ``isinstance(result, Err)``. Calls never raise for anything the API or the
    network does. Use it as a context manager, or call ``close()``::

        with EinarGate() as eg:
            gates = eg.gates.list_all().unwrap()
    """

    location: LocationResource
    """The API key's location"""
    members: MembersResource
    """Members and invitees of the location, who own permissions"""
    gates: GatesResource
    cameras: CamerasResource
    permissions: PermissionsResource
    """License plate permissions, one per camera"""
    events: EventsResource
    """Gate openings"""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        location_id: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.Client | None = None,
        app_info: AppInfo | None = None,
    ) -> None:
        """Creates a client.

        ``api_key`` defaults to the ``EINARGATE_API_KEY`` environment variable;
        keep it on the server. ``location_id`` is read from ``GET /me`` on
        first use when left out. ``timeout`` is per attempt, in seconds;
        ``max_retries`` counts the retries of what is safe to retry.
        ``http_client`` replaces the client's own ``httpx.Client``, e.g. for a
        proxy; the caller then closes it.
        """
        config = _config(api_key, base_url, timeout, max_retries, app_info)
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client()
        transport = Transport(config, self._http_client)

        def look_up() -> Result[str, Any]:
            # Shared by the calls that wait for it: the client's own timeout
            me = transport.send(o.GET_ME)
            return Ok(me.data.location_id, me.response) if isinstance(me, Ok) else me

        context = ClientContext(transport, location_id, look_up)
        self._context_ref = context
        super().__init__(context)
        self.location = LocationResource(context)
        self.members = MembersResource(context)
        self.gates = GatesResource(context)
        self.cameras = CamerasResource(context)
        self.permissions = PermissionsResource(context)
        self.events = EventsResource(context)

    def close(self) -> None:
        """Closes the client's HTTP connections, unless they are the caller's."""
        self._context_ref.close()
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self) -> EinarGate:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncEinarGate(AsyncRootResource):
    """The async Einar Gate API client; ``EinarGate`` with ``await``.

    Use it as an async context manager, or call ``aclose()``::

        async with AsyncEinarGate() as eg:
            gates = (await eg.gates.list_all()).unwrap()
    """

    location: AsyncLocationResource
    members: AsyncMembersResource
    gates: AsyncGatesResource
    cameras: AsyncCamerasResource
    permissions: AsyncPermissionsResource
    events: AsyncEventsResource

    def __init__(
        self,
        api_key: str | None = None,
        *,
        location_id: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.AsyncClient | None = None,
        app_info: AppInfo | None = None,
    ) -> None:
        """Creates a client; the options are ``EinarGate``'s."""
        config = _config(api_key, base_url, timeout, max_retries, app_info)
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient()
        transport = AsyncTransport(config, self._http_client)

        async def look_up() -> Result[str, Any]:
            # Shared by the calls that wait for it: the client's own timeout
            me = await transport.send(o.GET_ME)
            return Ok(me.data.location_id, me.response) if isinstance(me, Ok) else me

        context = AsyncClientContext(transport, location_id, look_up)
        self._context_ref = context
        super().__init__(context)
        self.location = AsyncLocationResource(context)
        self.members = AsyncMembersResource(context)
        self.gates = AsyncGatesResource(context)
        self.cameras = AsyncCamerasResource(context)
        self.permissions = AsyncPermissionsResource(context)
        self.events = AsyncEventsResource(context)

    async def aclose(self) -> None:
        """Closes the client's HTTP connections, unless they are the caller's."""
        await self._context_ref.aclose()
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> AsyncEinarGate:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()


__all__ = ["DEFAULT_BASE_URL", "AppInfo", "AsyncEinarGate", "EinarGate"]
