from __future__ import annotations

import re
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypeVar

import httpx
import pytest

from einargate import (
    AppInfo,
    CameraScope,
    CreatePermissionResult,
    EinarGate,
    EinarGateError,
    Err,
    EventRef,
    Gate,
    GateRef,
    GateScope,
    InvalidRequestIssue,
    Me,
    NotFoundProblem,
    Ok,
    Page,
    ReplacePermission,
    UnknownValue,
    __version__,
    is_unknown,
)
from einargate._helpers import CARRIED_FIELDS
from einargate.testing import MOCK_API_KEY, MockCall, MockEinarGate, MockReply

from .fixtures import GATE, PERMISSION, WHEN, permission_body

PROBLEMS = "https://developers.einargate.com/errors/"
T = TypeVar("T")


def test_turns_a_body_into_the_librarys_types() -> None:
    mock = MockEinarGate().on(
        "get_permission",
        lambda call: MockReply.raw(
            200, permission_body(licensePlateCountry="", unknownMember=1)
        ),
    )
    with mock.client() as eg:
        result = eg.permissions.get(PERMISSION)

    assert isinstance(result, Ok)
    assert result.data.created_at == WHEN
    assert result.data.license_plate_country is None
    assert result.data.supplemental_info is None
    assert result.response.request_id == "mock-request"


def test_keeps_values_and_variants_it_does_not_know() -> None:
    body = {
        "eventId": "e1",
        "type": "ScheduledGateOpening",
        "status": "finalized",
        "locationId": "mock-location",
        "gateId": "g1",
        "eventTime": "2026-09-12T10:41:07.000Z",
        "initiator": {"type": "schedule", "scheduleId": "s1"},
        "attachments": [],
        "createdAt": "2026-09-12T10:41:07.000Z",
        "updatedAt": "2026-09-12T10:41:07.000Z",
    }
    mock = MockEinarGate().on("get_event", lambda call: MockReply.raw(200, body))
    with mock.client() as eg:
        event = eg.events.get(EventRef(event_id="e1")).unwrap()

    assert is_unknown(event.type)
    assert event.type == UnknownValue("ScheduledGateOpening")
    assert str(event.type) == "ScheduledGateOpening"
    assert event.type != "ScheduledGateOpening"
    assert event.initiator is not None
    assert isinstance(event.initiator.type, UnknownValue)


def test_reports_a_body_that_breaks_the_contract() -> None:
    mock = MockEinarGate().on(
        "get_gate", lambda call: MockReply.raw(200, {"gateId": "g1", "name": "Main"})
    )
    with mock.client() as eg:
        result = eg.gates.get(GATE)

    match result:
        case Err(error) if error.type == "unexpected-response":
            assert error.path == "locationId"
            assert error.request_id == "mock-request"
        case _:
            pytest.fail(f"expected unexpected-response, got {result}")


def test_returns_a_declared_problem_with_its_hint() -> None:
    mock = MockEinarGate().on(
        "open_gate",
        lambda call: MockReply.problem(
            "gate-not-operable", detail="The control camera is offline"
        ),
    )
    with mock.client() as eg:
        result = eg.gates.open(GATE)

    assert isinstance(result, Err)
    error = result.error
    assert error.type == "gate-not-operable"
    assert error.status == 422
    assert error.docs_url == f"{PROBLEMS}gate-not-operable"
    assert "control camera" in error.hint
    assert re.match(
        r"Gate not operable \(422 gate-not-operable\): The control camera is "
        r"offline\. .*Request id mock-request",
        str(error),
    )


def test_treats_undeclared_and_unknown_types_as_unknown_problem() -> None:
    undeclared = {
        "type": f"{PROBLEMS}invalid-owner",
        "title": "Invalid owner",
        "status": 422,
        "requestId": "r1",
    }
    mock = (
        MockEinarGate()
        .on("get_gate", lambda call: MockReply.raw(422, undeclared))
        .on("list_gates", lambda call: MockReply.raw(418, "<html>teapot</html>"))
    )
    with mock.client() as eg:
        first = eg.gates.get(GATE)
        second = eg.gates.list()

    assert isinstance(first, Err) and first.error.type == "unknown-problem"
    assert first.error.problem_type == f"{PROBLEMS}invalid-owner"
    assert first.error.request_id == "r1"
    assert isinstance(second, Err) and second.error.type == "unknown-problem"
    assert second.error.status == 418


def test_returns_network_failures_and_timeouts() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    def hang(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    for handler, expected in ((refuse, "network"), (hang, "timeout")):
        client = httpx.Client(transport=httpx.MockTransport(handler))
        eg = EinarGate(
            MOCK_API_KEY, location_id="l1", max_retries=0, http_client=client
        )
        result = eg.gates.list()
        assert isinstance(result, Err) and result.error.type == expected


def test_unwrap_raises_an_einargate_error() -> None:
    mock = MockEinarGate().on("get_gate", lambda call: MockReply.problem("not-found"))
    with mock.client() as eg:
        result = eg.gates.get(GATE)
    with pytest.raises(EinarGateError) as raised:
        result.unwrap()
    assert isinstance(raised.value.error, NotFoundProblem)


def test_retries_a_per_second_limit_but_not_a_daily_one() -> None:
    answers: list[MockReply[Page[Gate], Literal["rate-limited"]]] = [
        MockReply.problem(
            "rate-limited",
            window="second",
            headers={"Retry-After": "0"},
        ),
        MockReply.ok(_page([GATE])),
    ]
    replies = iter(answers)
    mock = MockEinarGate().on("list_gates", lambda call: next(replies))
    with mock.client(max_retries=2) as eg:
        assert isinstance(eg.gates.list(), Ok)
    assert len(mock.calls) == 2

    daily = MockEinarGate().on(
        "list_gates",
        lambda call: MockReply.problem("rate-limited", window="day"),
    )
    with daily.client(max_retries=2) as eg:
        result = eg.gates.list()
    assert isinstance(result, Err) and result.error.type == "rate-limited"
    assert len(daily.calls) == 1


def test_sends_one_idempotency_key_for_a_write_and_its_retries() -> None:
    count = 0

    def handler(call: object) -> MockReply:
        nonlocal count
        count += 1
        if count == 1:
            return MockReply.problem(
                "idempotency-key-in-flight", headers={"Retry-After": "0"}
            )
        if count == 2:
            return MockReply.problem(
                "rate-limited",
                window="second",
                headers={"Retry-After": "0"},
            )
        return MockReply.raw(
            202,
            {
                "eventId": "e1",
                "type": "ManualGateOpening",
                "status": "pending",
                "locationId": "mock-location",
                "gateId": "g1",
                "eventTime": "2026-09-12T10:41:07.000Z",
                "createdAt": "2026-09-12T10:41:07.000Z",
                "updatedAt": "2026-09-12T10:41:07.000Z",
            },
        )

    mock = MockEinarGate().on("open_gate", handler)
    with mock.client(max_retries=2) as eg:
        assert isinstance(eg.gates.open(GATE), Ok)
        keys = [call.headers["idempotency-key"] for call in mock.calls]
        assert len(keys) == 3 and len(set(keys)) == 1
        assert re.fullmatch(r"[0-9a-f-]{36}", keys[0])

        eg.gates.open(GateRef(gate_id="g1"), idempotency_key="open-g1-42")
        assert mock.calls[-1].headers["idempotency-key"] == "open-g1-42"


def test_does_not_retry_a_write_that_may_have_run_and_says_how_to() -> None:
    mock = MockEinarGate().on(
        "open_gate", lambda call: MockReply.problem("service-unavailable")
    )
    with mock.client(max_retries=2) as eg:
        result = eg.gates.open(GATE, idempotency_key="open-1")
    assert len(mock.calls) == 1
    assert isinstance(result, Err)
    assert result.idempotency_key == "open-1"
    assert "check its effect" in str(result.error)
    assert "idempotency_key='open-1'" in str(result.error)

    def hang(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    eg = EinarGate(
        MOCK_API_KEY,
        location_id="l1",
        max_retries=2,
        http_client=httpx.Client(transport=httpx.MockTransport(hang)),
    )
    timed_out = eg.gates.open(GATE)
    assert isinstance(timed_out, Err) and timed_out.error.type == "timeout"
    assert timed_out.idempotency_key and re.fullmatch(
        r"[0-9a-f-]{36}", timed_out.idempotency_key
    )


def test_says_a_write_ran_after_unexpected_response_and_nothing_unsent() -> None:
    from einargate._runtime.transport import deadline

    mock = MockEinarGate().on("open_gate", lambda call: MockReply.raw(200, {}))
    with mock.client(max_retries=2) as eg:
        ran = eg.gates.open(GATE, idempotency_key="open-1")
        with deadline(0):
            unsent = eg.gates.open(GATE, idempotency_key="open-2")
    assert len(mock.calls) == 1
    assert isinstance(ran, Err) and ran.error.type == "unexpected-response"
    assert ran.idempotency_key == "open-1"
    assert "The write ran: do not send it again" in str(ran.error)
    assert isinstance(unsent, Err) and unsent.error.type == "timeout"
    assert unsent.idempotency_key == "open-2"
    assert str(unsent.error) == "The time given to the call ran out before it was sent."


def test_a_pool_timeout_is_a_write_that_was_not_sent() -> None:
    attempts = 0

    def no_connection(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.PoolTimeout("no connection free")

    eg = EinarGate(
        MOCK_API_KEY,
        location_id="l1",
        max_retries=1,
        http_client=httpx.Client(transport=httpx.MockTransport(no_connection)),
    )
    eg._context.transport._sleep = lambda seconds: None  # pyright: ignore[reportAttributeAccessIssue]
    result = eg.gates.open(GATE)
    assert attempts == 2
    assert isinstance(result, Err) and result.error.type == "network"
    assert result.error.request_sent is False
    assert "may have happened" not in str(result.error)


def test_retries_a_write_that_could_not_connect() -> None:
    attempts = 0

    def refuse(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("connection refused")

    eg = EinarGate(
        MOCK_API_KEY,
        location_id="l1",
        max_retries=1,
        http_client=httpx.Client(transport=httpx.MockTransport(refuse)),
    )
    eg._context.transport._sleep = lambda seconds: None  # pyright: ignore[reportAttributeAccessIssue]
    result = eg.gates.open(GATE)
    assert attempts == 2
    assert isinstance(result, Err) and result.error.type == "network"
    assert result.error.request_sent is False


def test_checks_the_status_against_the_contract() -> None:
    mismatch = {
        "type": f"{PROBLEMS}service-unavailable",
        "title": "Service unavailable",
        "status": 503,
        "requestId": "r1",
    }
    mock = (
        MockEinarGate()
        .on("delete_permission", lambda call: MockReply.raw(202, {"pending": True}))
        .on("replace_permission", lambda call: MockReply.raw(500, mismatch))
    )
    with mock.client(max_retries=2) as eg:
        deleted = eg.permissions.delete(PERMISSION)
        replaced = eg.permissions.update(PERMISSION, active=False)
    assert isinstance(deleted, Err) and deleted.error.type == "unexpected-response"
    assert isinstance(replaced, Err) and replaced.error.type == "unknown-problem"
    assert replaced.error.status == 500
    assert len(mock.calls_of("replace_permission")) == 1


def test_does_not_retry_a_500_on_a_write_but_does_on_a_read() -> None:
    mock = (
        MockEinarGate()
        .on("delete_permission", lambda call: MockReply.problem("internal"))
        .on("get_permission", lambda call: MockReply.problem("internal"))
    )
    eg = mock.client(max_retries=1)
    eg.permissions.delete(PERMISSION)
    assert len(mock.calls_of("delete_permission")) == 1
    eg._context.transport._sleep = lambda seconds: None  # pyright: ignore[reportAttributeAccessIssue]
    eg.permissions.get(PERMISSION)
    assert len(mock.calls_of("get_permission")) == 2


def test_reads_the_location_from_me_once_and_again_after_a_failure() -> None:
    me = {
        "apiKeyId": "k1",
        "name": "Sync",
        "locationId": "loc-from-me",
        "roles": ["IntegrationSetupReader"],
        "subscriptionActive": True,
        "rateLimit": {"requestsPerSecond": 17, "burst": 200, "requestsPerDay": 100000},
    }
    me_answers: list[MockReply[Me, Literal["service-unavailable"]]] = [
        MockReply.problem("service-unavailable"),
        MockReply.raw(200, me),
    ]
    replies = iter(me_answers)
    mock = (
        MockEinarGate()
        .on("get_me", lambda call: next(replies))
        .on("list_gates", lambda call: MockReply.ok(_page([])))
    )
    with mock.client(location_id=None) as eg:
        first = eg.gates.list()
        assert isinstance(first, Err) and first.error.type == "service-unavailable"
        eg.gates.list()
        eg.gates.list()

    assert len(mock.calls_of("get_me")) == 2
    assert [call.path for call in mock.calls_of("list_gates")] == [
        "/locations/loc-from-me/gates",
        "/locations/loc-from-me/gates",
    ]


def test_looks_the_location_up_again_after_a_failure_nobody_waited_for() -> None:
    import time

    me = {
        "apiKeyId": "k1",
        "name": "Sync",
        "locationId": "loc-from-me",
        "roles": [],
        "subscriptionActive": True,
        "rateLimit": {"requestsPerSecond": 17, "burst": 200, "requestsPerDay": 100000},
    }

    def slow_failure_then_me(
        call: MockCall,
    ) -> MockReply[Me, Literal["service-unavailable"]]:
        if len(mock.calls_of("get_me")) == 1:
            time.sleep(0.2)
            return MockReply.problem("service-unavailable")
        return MockReply.raw(200, me)

    mock = (
        MockEinarGate()
        .on("get_me", slow_failure_then_me)
        .on("list_gates", lambda call: MockReply.ok(_page([])))
    )
    with mock.client(location_id=None) as eg:
        first = eg.gates.list(timeout=0.05)
        assert isinstance(first, Err) and first.error.type == "timeout"
        time.sleep(0.3)
        second = eg.gates.list()
    assert isinstance(second, Ok)
    assert len(mock.calls_of("get_me")) == 2


def test_a_closed_client_returns_the_closed_error() -> None:
    import time

    def slow(call: MockCall) -> MockReply[Me, Literal["service-unavailable"]]:
        time.sleep(0.1)
        return MockReply.problem("service-unavailable")

    mock = (
        MockEinarGate()
        .on("get_me", slow)
        .on("list_gates", lambda call: MockReply.ok(_page([])))
    )
    eg = mock.client(location_id=None)
    waited = eg.gates.list(timeout=0.01)
    assert isinstance(waited, Err) and waited.error.type == "timeout"
    eg.close()
    result = eg.gates.list()
    assert isinstance(result, Err) and result.error.type == "network"
    assert str(result.error) == "The Einar Gate client was closed"
    assert mock.calls_of("list_gates") == []


def test_a_lookup_cancelled_before_it_ran_returns_the_closed_error() -> None:
    from collections.abc import Callable
    from concurrent.futures import Future, ThreadPoolExecutor
    from typing import Any

    class CancelsAtOnce(ThreadPoolExecutor):
        """As close() does when it cancels a lookup its worker has not taken"""

        def submit(
            self, fn: Callable[..., T], /, *args: Any, **kwargs: Any
        ) -> Future[T]:
            future: Future[T] = Future()
            future.cancel()
            return future

    mock = MockEinarGate().on("list_gates", lambda call: MockReply.ok(_page([])))
    eg = mock.client(location_id=None)
    eg._context._executor = CancelsAtOnce(max_workers=1)  # pyright: ignore[reportPrivateUsage]
    result = eg.gates.list()
    assert isinstance(result, Err) and result.error.type == "network"
    assert str(result.error) == "The Einar Gate client was closed"


def test_refuses_a_malformed_base_url() -> None:
    for base_url in ("not a url", "ftp://api.einargate.com/v1", "https://"):
        with pytest.raises(ValueError, match="base_url"):
            EinarGate(MOCK_API_KEY, base_url=base_url)


def test_creates_a_permission_at_the_scope_at_names() -> None:
    created = MockReply.ok(CreatePermissionResult(created=(PERMISSION,), failed=()))
    mock = (
        MockEinarGate()
        .on("create_location_permission", lambda call: created)
        .on("create_gate_permission", lambda call: created)
        .on("create_camera_permission", lambda call: created)
    )
    body = {"licensePlate": "abc-123", "ownerUserId": "u1", "active": True}
    with mock.client() as eg:
        eg.permissions.create(
            at="location", license_plate="abc-123", owner_user_id="u1", active=True
        )
        eg.permissions.create(
            at=GateScope(gate_id="g1"),
            license_plate="abc-123",
            owner_user_id="u1",
            active=True,
            license_plate_country=None,
        )
        eg.permissions.create(
            at=CameraScope(gate_id="g1", camera_id="c1"),
            license_plate="abc-123",
            owner_user_id="u1",
            active=True,
            license_plate_country="HU",
        )

    assert [call.operation for call in mock.calls] == [
        "create_location_permission",
        "create_gate_permission",
        "create_camera_permission",
    ]
    assert [call.body for call in mock.calls] == [
        body,
        {**body, "licensePlateCountry": ""},
        {**body, "licensePlateCountry": "HU"},
    ]
    assert mock.calls[2].params == {
        "locationId": "mock-location",
        "gateId": "g1",
        "cameraId": "c1",
    }


def test_url_encodes_ids_and_sends_a_listing_scope_as_filters() -> None:
    mock = (
        MockEinarGate()
        .on("delete_permission", lambda call: MockReply.ok())
        .on("list_permissions", lambda call: MockReply.ok(_page([])))
    )
    with mock.client() as eg:
        assert isinstance(eg.permissions.delete(PERMISSION), Ok)
        eg.permissions.list(at=CameraScope(gate_id="g1", camera_id="c1"), active=False)
        eg.permissions.list(at=GATE)

    assert mock.calls[0].path == (
        "/locations/mock-location/gates/g1/cameras/c1/permissions/ABC123%7CHU"
    )
    assert mock.calls[1].query == {"gateId": "g1", "cameraId": "c1", "active": "false"}
    assert mock.calls[2].query == {"gateId": "g1"}


def test_replaces_with_none_as_removal_and_updates_from_the_permission() -> None:
    mock = MockEinarGate().on(
        "replace_permission", lambda call: MockReply.ok(PERMISSION)
    )
    with mock.client() as eg:
        eg.permissions.replace(
            PERMISSION,
            license_plate="ABC123",
            license_plate_country=None,
            active=True,
            supplemental_info=None,
        )
        eg.permissions.update(PERMISSION, active=False)

    assert mock.calls[0].body == {
        "licensePlate": "ABC123",
        "licensePlateCountry": "",
        "active": True,
    }
    assert mock.calls[1].body == {
        "licensePlate": "ABC123",
        "licensePlateCountry": "HU",
        "active": False,
        "supplementalInfo": "Visitor",
    }


def test_update_carries_every_field_of_a_replacement() -> None:
    assert {field.name for field in fields(ReplacePermission)} == set(CARRIED_FIELDS)


def test_collects_every_page_with_list_all() -> None:
    def handler(call: MockCall) -> MockReply:
        query = call.query
        if "continuationToken" not in query:
            return MockReply.raw(
                200, {"items": [_gate_body("g1")], "continuationToken": "next"}
            )
        return MockReply.raw(200, {"items": [_gate_body("g2")]})

    mock = MockEinarGate().on("list_gates", handler)
    with mock.client() as eg:
        gates = eg.gates.list_all().unwrap()

    assert [gate.gate_id for gate in gates] == ["g1", "g2"]
    assert [call.query for call in mock.calls] == [
        {"limit": "200"},
        {"limit": "200", "continuationToken": "next"},
    ]


def test_sends_timestamps_in_utc_and_refuses_naive_ones() -> None:
    mock = MockEinarGate().on("list_events", lambda call: MockReply.ok(_page([])))
    with mock.client() as eg:
        eg.events.list(from_=datetime(2026, 10, 1, 12, tzinfo=timezone.utc))
        assert mock.calls[0].query == {"from": "2026-10-01T12:00:00.000Z"}
        with pytest.raises(ValueError, match="timezone-aware"):
            eg.events.list(from_=datetime(2026, 10, 1, 12))


def test_names_invalid_members_as_this_library_does() -> None:
    mock = MockEinarGate().on(
        "list_events",
        lambda call: MockReply.problem(
            "invalid-request",
            errors=[
                InvalidRequestIssue(
                    path="query.minFraudRiskPercentage", message="Too small"
                )
            ],
        ),
    )
    with mock.client() as eg:
        result = eg.events.list(min_fraud_risk_percentage=0)
    assert isinstance(result, Err) and result.error.type == "invalid-request"
    assert result.error.errors[0].python_name == "min_fraud_risk_percentage"


def test_sends_a_user_agent_with_the_version_and_the_app() -> None:
    mock = MockEinarGate().on("list_gates", lambda call: MockReply.ok(_page([])))
    with mock.client(app_info=AppInfo("acme-sync", "1.2.0")) as eg:
        eg.gates.list()
    headers = mock.calls[0].headers
    assert re.fullmatch(
        rf"einargate-python/{re.escape(__version__)} python/\S+ acme-sync/1\.2\.0",
        headers["user-agent"],
    )
    assert headers["authorization"] == f"Bearer {MOCK_API_KEY}"


def test_keeps_the_version_equal_to_pyprojects() -> None:
    pyproject = (Path(__file__).parent.parent / "pyproject.toml").read_text()
    match = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
    assert match is not None and __version__ == match.group(1)


def _page(items: list[T]) -> Page[T]:
    return Page(items=tuple(items))


def _gate_body(gate_id: str) -> dict[str, object]:
    return {
        "gateId": gate_id,
        "locationId": "mock-location",
        "name": gate_id,
        "manualOperation": False,
        "createdAt": "2026-09-12T10:41:07.000Z",
        "updatedAt": "2026-09-12T10:41:07.000Z",
    }


def test_applies_a_callers_timeout_to_its_wait_for_the_location() -> None:
    import time

    def slow(call: MockCall) -> MockReply[Me, Literal["service-unavailable"]]:
        time.sleep(0.5)
        return MockReply.problem("service-unavailable")

    mock = (
        MockEinarGate()
        .on("get_me", slow)
        .on("list_gates", lambda call: MockReply.ok(_page([])))
    )
    started = time.monotonic()
    with mock.client(location_id=None) as eg:
        result = eg.gates.list(timeout=0.05)
    assert isinstance(result, Err) and result.error.type == "timeout"
    assert time.monotonic() - started < 0.4


def test_close_stops_a_location_lookup_waiting_to_retry() -> None:
    import threading
    import time

    mock = MockEinarGate().on(
        "get_me",
        lambda call: MockReply.problem("provisioning", headers={"Retry-After": "60"}),
    )
    eg = mock.client(location_id=None, max_retries=2)
    result = eg.gates.list(timeout=0.05)
    assert isinstance(result, Err) and result.error.type == "timeout"
    eg.close()
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline and any(
        thread.name.startswith("einargate-location") for thread in threading.enumerate()
    ):
        time.sleep(0.01)
    assert not any(
        thread.name.startswith("einargate-location") for thread in threading.enumerate()
    )
