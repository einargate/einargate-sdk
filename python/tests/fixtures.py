from __future__ import annotations

from datetime import datetime, timezone

from einargate import Event, Gate, Permission

WHEN = datetime(2026, 9, 12, 10, 41, 7, tzinfo=timezone.utc)

GATE = Gate(
    gate_id="g1",
    location_id="mock-location",
    name="Main gate",
    manual_operation=True,
    gate_control_camera_id="c1",
    created_at=WHEN,
    updated_at=WHEN,
)

PERMISSION = Permission(
    permission_id="ABC123|HU",
    location_id="mock-location",
    gate_id="g1",
    camera_id="c1",
    license_plate="ABC123",
    license_plate_country="HU",
    owner_user_id="u1",
    active=True,
    supplemental_info="Visitor",
    number_of_openings=3,
    created_at=WHEN,
    updated_at=WHEN,
)


def permission_body(**overrides: object) -> dict[str, object]:
    return {
        "permissionId": "ABC123|HU",
        "locationId": "mock-location",
        "gateId": "g1",
        "cameraId": "c1",
        "licensePlate": "ABC123",
        "licensePlateCountry": "HU",
        "ownerUserId": "u1",
        "active": True,
        "numberOfOpenings": 0,
        "createdAt": "2026-09-12T10:41:07.000Z",
        "updatedAt": "2026-09-12T10:41:07.000Z",
        **overrides,
    }


def event(event_id: str, event_time: str) -> Event:
    when = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
    return Event(
        event_id=event_id,
        type="AutomaticGateOpening",
        status="finalized",
        location_id="mock-location",
        gate_id="g1",
        camera_id="c1",
        event_time=when,
        created_at=when,
        updated_at=when,
    )
