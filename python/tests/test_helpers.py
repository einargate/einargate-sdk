from __future__ import annotations

import itertools
from collections.abc import Callable
from datetime import datetime, timezone

import pytest

from einargate import (
    EinarGate,
    Err,
    Event,
    EventAttachment,
    EventWithAttachments,
    Ok,
    Page,
    WaitTimeout,
)
from einargate.testing import MockCall, MockEinarGate, MockReply

from .fixtures import event


def test_follow_yields_each_event_once_and_carries_the_cursor() -> None:
    polls = [
        [event("e1", "2026-10-01T10:00:00Z"), event("e2", "2026-10-01T10:00:05Z")],
        [event("e2", "2026-10-01T10:00:05Z"), event("e3", "2026-10-01T10:00:05Z")],
        [
            event("e2", "2026-10-01T10:00:05Z"),
            event("e3", "2026-10-01T10:00:05Z"),
            event("e4", "2026-10-01T10:01:00Z"),
        ],
    ]
    counter = itertools.count()

    def handler(call: MockCall) -> MockReply:
        return MockReply.ok(Page(items=tuple(polls[min(next(counter), 2)])))

    mock = MockEinarGate().on("list_events", handler)
    seen: list[str] = []
    with mock.client() as eg:
        for result in eg.events.follow(
            from_=datetime(2026, 10, 1, 9, tzinfo=timezone.utc), poll_interval=0
        ):
            seen.append(result.unwrap().event_id)
            if len(seen) == 4:
                break

    assert seen == ["e1", "e2", "e3", "e4"]
    assert [call.query["from"] for call in mock.calls] == [
        "2026-10-01T09:00:00.000Z",
        "2026-10-01T10:00:05.000Z",
        "2026-10-01T10:00:05.000Z",
    ]


def _polls(*items: Event) -> Callable[[MockCall], MockReply]:
    """The same events on two polls, then a failure that ends ``follow``"""
    polls = itertools.count()

    def handler(call: MockCall) -> MockReply:
        if next(polls) == 2:
            return MockReply.problem("service-unavailable")
        return MockReply.ok(Page(items=items))

    return handler


def test_follow_yields_an_event_at_a_start_finer_than_milliseconds_once() -> None:
    mock = MockEinarGate().on(
        "list_events", _polls(event("e1", "2026-10-01T10:00:00.123Z"))
    )
    with mock.client() as eg:
        seen = [
            result.data.event_id
            for result in eg.events.follow(
                from_=datetime(2026, 10, 1, 10, 0, 0, 123456, tzinfo=timezone.utc),
                poll_interval=0,
            )
            if isinstance(result, Ok)
        ]
    assert seen == ["e1"]
    assert mock.calls[0].query["from"] == "2026-10-01T10:00:00.123Z"


def test_follow_skips_an_event_older_than_the_cursor() -> None:
    mock = MockEinarGate().on(
        "list_events",
        _polls(
            event("e0", "2026-10-01T10:00:05.200Z"),
            event("e1", "2026-10-01T10:00:06Z"),
        ),
    )
    with mock.client() as eg:
        seen = [
            result.data.event_id
            for result in eg.events.follow(
                from_=datetime(2026, 10, 1, 10, 0, 5, 500000, tzinfo=timezone.utc),
                poll_interval=0,
            )
            if isinstance(result, Ok)
        ]
    assert seen == ["e1"]


def test_follow_yields_a_failure_and_stops() -> None:
    mock = MockEinarGate().on(
        "list_events", lambda call: MockReply.problem("forbidden")
    )
    with mock.client() as eg:
        results = list(eg.events.follow(poll_interval=0))
    assert len(results) == 1
    assert isinstance(results[0], Err) and results[0].error.type == "forbidden"


PENDING = EventWithAttachments(
    **{
        name: getattr(event("e1", "2026-10-01T10:00:00Z"), name)
        for name in (
            "event_id",
            "location_id",
            "gate_id",
            "event_time",
            "created_at",
            "updated_at",
        )
    },
    type="ManualGateOpening",
    status="pending",
    attachments=(
        EventAttachment(
            file_name="a.jpg",
            role="Overview",
            media_type="image/jpeg",
            status="requested",
        ),
    ),
)


def test_wait_for_attachments_gets_the_event_until_its_snapshots_arrive() -> None:
    done = EventWithAttachments(
        **{
            **{
                name: getattr(PENDING, name)
                for name in (
                    "event_id",
                    "type",
                    "location_id",
                    "gate_id",
                    "event_time",
                    "created_at",
                    "updated_at",
                )
            },
            "status": "finalized",
            "attachments": (
                EventAttachment(
                    file_name="a.jpg",
                    role="Overview",
                    media_type="image/jpeg",
                    status="uploaded",
                    url="https://example.test/a.jpg",
                ),
            ),
        }
    )
    replies = iter([PENDING, PENDING, done])
    mock = MockEinarGate().on("get_event", lambda call: MockReply.ok(next(replies)))
    with mock.client() as eg:
        result = eg.events.wait_for_attachments(PENDING, poll_interval=0)
    assert isinstance(result, Ok)
    assert result.data.attachments[0].url == "https://example.test/a.jpg"
    assert len(mock.calls) == 3


def test_wait_for_attachments_gives_up_with_the_event_as_last_seen() -> None:
    mock = MockEinarGate().on("get_event", lambda call: MockReply.ok(PENDING))
    with mock.client() as eg:
        result = eg.events.wait_for_attachments(PENDING, wait=0.01, poll_interval=0.005)
    match result:
        case Err(WaitTimeout() as error):
            assert error.event is not None and error.event.event_id == "e1"
        case _:
            pytest.fail(f"expected wait-timeout, got {result}")


@pytest.mark.anyio
async def test_wait_for_attachments_stops_a_poll_that_outlasts_the_wait() -> None:
    import asyncio
    import time

    import httpx

    from einargate import AsyncEinarGate
    from einargate.testing import MOCK_API_KEY

    async def hang(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(10)
        raise AssertionError("not reached")

    eg = AsyncEinarGate(
        MOCK_API_KEY,
        location_id="l1",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(hang)),
    )
    started = time.monotonic()
    result = await eg.events.wait_for_attachments(PENDING, wait=0.05)
    assert isinstance(result, Err) and result.error.type == "wait-timeout"
    assert time.monotonic() - started < 1


def test_wait_for_attachments_bounds_retries_by_the_wait() -> None:
    import time

    mock = MockEinarGate().on(
        "get_event",
        lambda call: MockReply.problem(
            "service-unavailable", headers={"Retry-After": "1"}
        ),
    )
    started = time.monotonic()
    with mock.client(max_retries=1) as eg:
        result = eg.events.wait_for_attachments(PENDING, wait=0.05)
    assert isinstance(result, Err) and result.error.type == "wait-timeout"
    assert time.monotonic() - started < 0.5
    assert len(mock.calls) == 1


def test_wait_for_attachments_ends_on_time_while_a_response_trickles_in() -> None:
    import time

    eg = _trickle_client(stop_on_close=True)
    started = time.monotonic()
    result = eg.events.wait_for_attachments(PENDING, wait=0.05)
    assert isinstance(result, Err) and result.error.type == "wait-timeout"
    assert time.monotonic() - started < 0.5


def _trickle_client(stop_on_close: bool) -> EinarGate:
    import json
    import time
    from collections.abc import Iterator

    import httpx

    from einargate._generated.models import encode_event_with_attachments
    from einargate.testing import MOCK_API_KEY

    body = json.dumps(encode_event_with_attachments(PENDING)).encode()

    class Trickle(httpx.SyncByteStream):
        def __init__(self) -> None:
            self.closed = False

        def __iter__(self) -> Iterator[bytes]:
            for byte in body:
                if self.closed:
                    return
                time.sleep(0.01)
                yield bytes([byte])

        def close(self) -> None:
            self.closed = stop_on_close

    return EinarGate(
        MOCK_API_KEY,
        location_id="l1",
        http_client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, stream=Trickle())
            )
        ),
    )


def test_a_timed_out_poll_closes_its_read_and_its_worker_ends() -> None:
    import threading
    import time

    before = set(threading.enumerate())
    eg = _trickle_client(stop_on_close=True)
    for _ in range(3):
        result = eg.events.wait_for_attachments(PENDING, wait=0.03)
        assert isinstance(result, Err) and result.error.type == "wait-timeout"
    eg.close()
    deadline = time.monotonic() + 1

    def workers() -> list[threading.Thread]:
        return [
            thread
            for thread in threading.enumerate()
            if thread.name == "einargate-wait" and thread not in before
        ]

    while time.monotonic() < deadline and workers():
        time.sleep(0.01)
    assert not workers()


def test_a_poll_that_cannot_be_stopped_does_not_keep_the_process_alive() -> None:
    import subprocess
    import sys
    import textwrap
    from pathlib import Path

    script = textwrap.dedent(
        """
        from tests.test_helpers import PENDING, _trickle_client

        eg = _trickle_client(stop_on_close=False)
        result = eg.events.wait_for_attachments(PENDING, wait=0.03)
        print(result.error.type)
        """
    )
    finished = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert finished.stdout.strip() == "wait-timeout", finished.stderr
