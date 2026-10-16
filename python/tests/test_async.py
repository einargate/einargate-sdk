from __future__ import annotations

import pytest

from einargate import Err, GateRef, Ok, Page
from einargate.testing import MockEinarGate, MockReply

from .fixtures import GATE, PERMISSION

pytestmark = pytest.mark.anyio


async def test_the_async_client_returns_the_same_results() -> None:
    mock = (
        MockEinarGate()
        .on("list_gates", lambda call: MockReply.ok(Page(items=(GATE,))))
        .on("open_gate", lambda call: MockReply.problem("gate-not-operable"))
        .on("replace_permission", lambda call: MockReply.ok(PERMISSION))
    )
    async with mock.async_client() as eg:
        gates = await eg.gates.list_all()
        opened = await eg.gates.open(GateRef(gate_id="g1"))
        updated = await eg.permissions.update(PERMISSION, active=False)

    assert isinstance(gates, Ok) and [gate.gate_id for gate in gates.data] == ["g1"]
    assert isinstance(opened, Err) and opened.error.type == "gate-not-operable"
    assert isinstance(updated, Ok)
    assert mock.calls[-1].body == {
        "licensePlate": "ABC123",
        "licensePlateCountry": "HU",
        "active": False,
        "supplementalInfo": "Visitor",
    }


async def test_the_async_client_reads_the_location_from_me() -> None:
    me = {
        "apiKeyId": "k1",
        "name": "Sync",
        "locationId": "loc-from-me",
        "roles": [],
        "subscriptionActive": True,
        "rateLimit": {"requestsPerSecond": 17, "burst": 200, "requestsPerDay": 100000},
    }
    mock = (
        MockEinarGate()
        .on("get_me", lambda call: MockReply.raw(200, me))
        .on("list_gates", lambda call: MockReply.ok(Page(items=())))
    )
    async with mock.async_client(location_id=None) as eg:
        await eg.gates.list()
        await eg.gates.list()
    assert len(mock.calls_of("get_me")) == 1
    assert mock.calls[-1].path == "/locations/loc-from-me/gates"


async def test_the_async_client_applies_a_callers_timeout_to_the_lookup() -> None:
    import asyncio

    import httpx

    from einargate import AsyncEinarGate
    from einargate.testing import MOCK_API_KEY

    async def hang(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(10)
        raise AssertionError("not reached")

    eg = AsyncEinarGate(
        MOCK_API_KEY, http_client=httpx.AsyncClient(transport=httpx.MockTransport(hang))
    )
    result = await asyncio.wait_for(eg.gates.list(timeout=0.05), 2)
    assert isinstance(result, Err) and result.error.type == "timeout"


async def test_a_short_wait_does_not_shorten_the_shared_location_lookup() -> None:
    import asyncio

    import httpx

    from einargate import AsyncEinarGate, EventRef
    from einargate.testing import MOCK_API_KEY

    me = {
        "apiKeyId": "k1",
        "name": "Sync",
        "locationId": "loc-from-me",
        "roles": [],
        "subscriptionActive": True,
        "rateLimit": {"requestsPerSecond": 17, "burst": 200, "requestsPerDay": 100000},
    }

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/me"):
            await asyncio.sleep(0.1)
            return httpx.Response(200, json=me)
        return httpx.Response(200, json={"items": []})

    eg = AsyncEinarGate(
        MOCK_API_KEY,
        timeout=1.0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    waited, listed = await asyncio.gather(
        eg.events.wait_for_attachments(EventRef(event_id="e1"), wait=0.03),
        eg.gates.list(),
    )
    assert isinstance(waited, Err) and waited.error.type == "wait-timeout"
    assert isinstance(listed, Ok)
    await eg.aclose()


async def test_aclose_gives_a_caller_waiting_for_the_lookup_the_closed_error() -> None:
    import asyncio

    import httpx

    from einargate import AsyncEinarGate
    from einargate.testing import MOCK_API_KEY

    async def hang(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(10)
        raise AssertionError("not reached")

    eg = AsyncEinarGate(
        MOCK_API_KEY, http_client=httpx.AsyncClient(transport=httpx.MockTransport(hang))
    )
    waiting = asyncio.ensure_future(eg.gates.list())
    await asyncio.sleep(0.02)
    await eg.aclose()
    result = await waiting
    assert isinstance(result, Err) and result.error.type == "network"
    assert str(result.error) == "The Einar Gate client was closed"


async def test_aclose_ends_a_retry_waiting_for_retry_after() -> None:
    import asyncio
    import time

    mock = MockEinarGate().on(
        "list_gates",
        lambda call: MockReply.problem("provisioning", headers={"Retry-After": "30"}),
    )
    eg = mock.async_client(max_retries=2)
    started = time.monotonic()
    waiting = asyncio.ensure_future(eg.gates.list())
    await asyncio.sleep(0.05)
    await eg.aclose()
    result = await waiting
    assert isinstance(result, Err) and result.error.type == "network"
    assert time.monotonic() - started < 1
    assert len(mock.calls) == 1


async def test_aclose_cancels_a_location_lookup_in_progress() -> None:
    import asyncio

    import httpx

    from einargate import AsyncEinarGate
    from einargate.testing import MOCK_API_KEY

    async def hang(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(10)
        raise AssertionError("not reached")

    eg = AsyncEinarGate(
        MOCK_API_KEY, http_client=httpx.AsyncClient(transport=httpx.MockTransport(hang))
    )
    result = await eg.gates.list(timeout=0.02)
    assert isinstance(result, Err) and result.error.type == "timeout"
    lookup = eg._context_ref._lookup  # pyright: ignore[reportPrivateUsage]
    await eg.aclose()
    assert lookup is not None and lookup.cancelled()
