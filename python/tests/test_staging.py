"""The Python client against a deployed API (ADR-0022).

Skipped unless ``EINARGATE_TEST_API_KEY`` and ``EINARGATE_TEST_BASE_URL``
are set: the monorepo's integration suite runs it with the API key it
creates for its own location. Read-only.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from einargate import AsyncEinarGate, EinarGate, Err, GateRef, Ok

API_KEY = os.environ.get("EINARGATE_TEST_API_KEY")
BASE_URL = os.environ.get("EINARGATE_TEST_BASE_URL")

pytestmark = pytest.mark.skipif(
    not API_KEY or not BASE_URL, reason="no deployed API to test against"
)


def test_reads_the_location_through_the_python_client() -> None:
    with EinarGate(API_KEY, base_url=BASE_URL) as eg:
        me = eg.me().unwrap()
        assert me.location_id
        assert eg.location.get().unwrap().location_id == me.location_id

        gates = eg.gates.list_all().unwrap()
        assert gates
        cameras = eg.cameras.list_all(at=gates[0]).unwrap()
        assert all(camera.gate_id == gates[0].gate_id for camera in cameras)
        assert eg.members.list_all().unwrap()
        eg.permissions.list_all().unwrap()
        since = datetime.now(timezone.utc) - timedelta(days=1)
        assert isinstance(eg.events.list(from_=since), Ok)

        missing = eg.gates.get(GateRef(gate_id="gate_unknown"))
        assert isinstance(missing, Err) and missing.error.type == "not-found"


@pytest.mark.anyio
async def test_reads_the_location_through_the_async_client() -> None:
    async with AsyncEinarGate(API_KEY, base_url=BASE_URL) as eg:
        me = (await eg.me()).unwrap()
        location = (await eg.location.get()).unwrap()
        assert location.location_id == me.location_id
