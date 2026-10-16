# Einar Gate API, Python client: guide for coding agents

> **Very early alpha.** The Einar Gate public API is not generally
> available yet, and this client may change in breaking ways before 1.0:
> pin an exact version.

This is everything you need to write correct code against the Einar Gate
API with the `einargate` package. The types are the contract: if pyright or
mypy accepts your code, it handles every case the API can produce. Read the
rules below once; the operations table at the end lists what each call
needs and returns.

## Setup

```python
from einargate import AppInfo, EinarGate, Ok

# Reads the EINARGATE_API_KEY environment variable; or pass the key first.
# An API key value looks like egk_ + 36 letters and digits. It is created in
# the Einar Gate app by a location Owner or Admin, who also picks its roles.
with EinarGate(app_info=AppInfo("acme-sync", "1.0.0")) as eg:
    me = eg.me()
    if isinstance(me, Ok):
        print(me.data.name, me.data.roles, me.data.rate_limit)
```

Python 3.10 or later. The only dependency is `httpx`. `AsyncEinarGate` has
the same calls with `await`, and `async with` instead of `with`. This guide
is also installed with the package, as `einargate/AGENTS.md`.

## Rules

1. **Every call returns `Ok` or `Err` and never raises** for anything the
   API or the network does. Use `match result:` with `case Ok(data):` and
   `case Err(error):`, or `isinstance(result, Ok)`. Only the constructor
   raises (`ValueError`), for a missing or malformed API key, and so does
   passing a naive `datetime`. `result.unwrap()` returns the data or raises
   an `EinarGateError` whose `error` is the result's; use it in scripts that
   should stop at the first failure.
2. **`error.type` is one flat discriminator.** It is a problem type of the
   call (`"not-found"`, `"limit-exceeded"`, …), `"unknown-problem"` (an
   error the API added after this version, or a body that is not a problem:
   handle it by `status`), `"network"`, `"timeout"`, or
   `"unexpected-response"` (a body that breaks the contract: a bug on the
   API's side). Each problem is a class (`NotFoundProblem`, …) and each
   call's error union, e.g. `CreatePermissionError`, lists exactly its
   types. Every problem has `message` (`str(error)` gives it), `hint` (what
   to do), `detail`, `request_id` and `docs_url`.
3. **Never pass a location id.** The client is bound to the API key's
   location: it reads it from `GET /me` on first use, or takes
   `location_id=` in its constructor.
4. **Do not write your own retry loop.** The client retries a read after a
   network error, a timeout, a 5xx or `rate-limited` with
   `window == "second"`, with backoff and `Retry-After`, up to `max_retries`
   (2). It retries a write only when the write cannot have run:
   `rate-limited` per second, `provisioning`, `idempotency-key-in-flight`,
   or no connection at all. `rate-limited` with `window == "day"` means the
   daily quota is used up.
5. **A write that may have run comes back to you, with its key.** Every
   `POST`, `PUT` and `DELETE` sends an `Idempotency-Key`. After a timeout, a
   network error once the request was sent, or a 5xx, the write may have
   happened, and opening a gate twice is not a retry's call to make: the
   `Err` carries `idempotency_key`, and its message says so. Check the
   effect first (for a gate opening, `events.list`; for a permission,
   `permissions.list_all(license_plate=...)`). If you send it again, pass
   `idempotency_key=result.idempotency_key`: the API replays the first
   response if that write completed, but runs it again if the API failed
   after running it, since it does not keep the key of a failed write. To
   stay safe across restarts of your process, pass your own key derived
   from your data: `idempotency_key="open-g1-42"`.
   `result.response.replayed` is `True` when the write had already happened.
   After `unexpected-response` the write ran, but its answer broke the
   contract: check its effect, and do not send it again.
6. **Values the API adds later are `UnknownValue`.** Every enum and union in
   a response includes it (e.g. `camera.status: CameraStatus | UnknownValue`),
   so an exhaustive `match` needs a `case UnknownValue():`. `str(value)`
   gives the raw value. It never equals a string, so a comparison with a
   known value is never true by accident.
7. **Ids are opaque.** Use them exactly as returned; never build or parse
   one. The client URL-encodes them. Pass an entity where a reference is
   asked for, `eg.permissions.delete(permission)`, `eg.gates.open(gate)`,
   or a reference: `eg.gates.open(GateRef(gate_id="…"))`.
8. **Permissions are per camera.** A plate permitted at a gate with two
   cameras is two permissions. Create at a scope with `at=`: `"location"`
   (every camera), a `Gate` or `GateScope(gate_id=…)` (every camera of a
   gate), or a `Camera` or `CameraScope(gate_id=…, camera_id=…)`. A create
   succeeds when at least one camera got the plate: `data.created` is never
   empty, and `data.failed` lists the cameras that did not, each with a
   `ConflictProblem` or `LimitExceededProblem`. Find a plate's permissions
   with `list_all(license_plate=…)`.
9. **`replace` is a full replacement; prefer `update`.** `replace` removes
   every field you leave out, so it requires `supplemental_info` (`None`
   removes it). `eg.permissions.update(permission, active=False)` keeps the
   other fields. Changing the plate or country changes the `permission_id`:
   use the returned permission from then on.
10. **`license_plate_country=None` means no country.** On create, leaving it
    out (`NOT_GIVEN`) applies the location's `default_license_plate_country`.
11. **`forbidden` means a missing role.** Each method's docstring and the
    table below name the roles that allow it; `eg.me()` shows the key's.
12. **Timestamps are timezone-aware `datetime`s**, in UTC. A naive
    `datetime` is refused rather than guessed. Field names are in
    `snake_case`, and `from` is `from_`. The `errors` of an
    `invalid-request` problem name members as the API does
    (`query.licensePlate`); `issue.python_name` gives this library's name
    (`license_plate`).

## Recipes

### Sync permissions from your system

```python
from einargate import EinarGate, Err, Permission

# The plates your system says may enter, with their owner's user id
wanted = {"ABC123": "user-1", "XYZ789": "user-2"}

with EinarGate() as eg:
    existing = eg.permissions.list_all().unwrap()

    by_plate: dict[str, list[Permission]] = {}
    for permission in existing:
        by_plate.setdefault(permission.license_plate, []).append(permission)

    for plate, owner_user_id in wanted.items():
        if plate in by_plate:
            continue
        created = eg.permissions.create(
            at="location",
            license_plate=plate,
            owner_user_id=owner_user_id,
            active=True,
        )
        if isinstance(created, Err):
            print(f"{plate}: {created.error}")
            continue
        for failed in created.data.failed:
            print(f"{plate} at camera {failed.camera_id}: {failed.error.message}")

    for plate, permissions in by_plate.items():
        if plate in wanted:
            continue
        for permission in permissions:
            deleted = eg.permissions.delete(permission)
            if isinstance(deleted, Err) and deleted.error.type != "not-found":
                print(f"{plate}: {deleted.error}")
```

### Open a gate and get its snapshots

```python
from einargate import EinarGate, Err, GateRef, Ok

with EinarGate() as eg:
    opened = eg.gates.open(GateRef(gate_id="gate-id"))
    match opened:
        case Err(error) if error.type == "gate-not-operable":
            print("The gate cannot be opened now:", error.detail)
        case Err(error) if error.type == "forbidden":
            print("The API key needs the IntegrationGateOperator role")
        case Err(error):
            print(error)
        case Ok(event):
            snapshots = eg.events.wait_for_attachments(event)
            if isinstance(snapshots, Ok):
                for attachment in snapshots.data.attachments:
                    print(attachment.role, attachment.url)  # valid for 15 minutes
```

### Follow new gate openings

```python
from einargate import EinarGate, Err

with EinarGate() as eg:
    for result in eg.events.follow(type="AutomaticGateOpening"):
        if isinstance(result, Err):
            print(result.error)
            break
        plate = result.data.plate
        print(result.data.event_time, plate.text if plate else None)
```

### Test without a real location

There is no sandbox, so test against the mock. It runs the real client
against answers you register per operation (snake_case operation ids).
`on` is typed per operation: pyright rejects data of another type, or a
problem type the operation does not declare.

```python
from einargate import Err, GateRef
from einargate.testing import MockEinarGate, MockReply

mock = MockEinarGate()
mock.on(
    "open_gate",
    lambda call: MockReply.problem(
        "gate-not-operable", detail="The control camera is offline"
    ),
)

with mock.client() as eg:
    result = eg.gates.open(GateRef(gate_id="g1"))

assert isinstance(result, Err) and result.error.type == "gate-not-operable"
assert len(mock.calls_of("open_gate")) == 1
```

## Operations

`Errors` lists each call's own problem types; every authenticated call can
also return `unauthorized`, `forbidden`, `rate-limited`, `provisioning`,
`internal`, `service-unavailable` and the `CallError` types.

<!-- generated:operations:start -->

| Call                                  | HTTP                                                                                                                                                                                                                                                           | Roles                                                                                                             | Errors                                                                                                                              |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `eg.me()`                             | `GET /me`                                                                                                                                                                                                                                                      | any                                                                                                               | –                                                                                                                                   |
| `eg.open_api_document()`              | `GET /openapi.json`                                                                                                                                                                                                                                            | none (no API key)                                                                                                 | `internal`, `rate-limited`, `service-unavailable`                                                                                   |
| `eg.location.get()`                   | `GET /locations/{locationId}`                                                                                                                                                                                                                                  | `IntegrationSetupReader`, `IntegrationEventReader`                                                                | `invalid-request`, `not-found`                                                                                                      |
| `eg.members.list()`, `list_all()`     | `GET /locations/{locationId}/members`                                                                                                                                                                                                                          | `IntegrationPermissionReader`, `IntegrationPermissionManager`                                                     | `invalid-request`, `not-found`                                                                                                      |
| `eg.gates.list()`, `list_all()`       | `GET /locations/{locationId}/gates`                                                                                                                                                                                                                            | any                                                                                                               | `invalid-request`                                                                                                                   |
| `eg.gates.get()`                      | `GET /locations/{locationId}/gates/{gateId}`                                                                                                                                                                                                                   | any                                                                                                               | `invalid-request`, `not-found`                                                                                                      |
| `eg.gates.open()`                     | `POST /locations/{locationId}/gates/{gateId}/open`                                                                                                                                                                                                             | `IntegrationGateOperator`                                                                                         | `gate-not-operable`, `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-request`, `not-found`                           |
| `eg.cameras.list()`, `list_all()`     | `GET /locations/{locationId}/cameras` (`"location"`)<br>`GET /locations/{locationId}/gates/{gateId}/cameras` (a `Gate` or `GateScope`)                                                                                                                         | `IntegrationSetupReader`, `IntegrationPermissionReader`, `IntegrationEventReader`, `IntegrationPermissionManager` | `invalid-request`, `not-found`                                                                                                      |
| `eg.cameras.get()`                    | `GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}`                                                                                                                                                                                                | `IntegrationSetupReader`, `IntegrationPermissionReader`, `IntegrationEventReader`, `IntegrationPermissionManager` | `invalid-request`, `not-found`                                                                                                      |
| `eg.permissions.list()`, `list_all()` | `GET /locations/{locationId}/permissions`                                                                                                                                                                                                                      | `IntegrationPermissionReader`, `IntegrationPermissionManager`                                                     | `invalid-request`                                                                                                                   |
| `eg.permissions.create()`             | `POST /locations/{locationId}/permissions` (`"location"`)<br>`POST /locations/{locationId}/gates/{gateId}/permissions` (a `Gate` or `GateScope`)<br>`POST /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions` (a `Camera` or `CameraScope`) | `IntegrationPermissionManager`                                                                                    | `conflict`, `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-owner`, `invalid-request`, `limit-exceeded`, `not-found` |
| `eg.permissions.get()`                | `GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`                                                                                                                                                                     | `IntegrationPermissionReader`, `IntegrationPermissionManager`                                                     | `invalid-request`, `not-found`                                                                                                      |
| `eg.permissions.replace()`            | `PUT /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`                                                                                                                                                                     | `IntegrationPermissionManager`                                                                                    | `conflict`, `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-request`, `not-found`                                    |
| `eg.permissions.delete()`             | `DELETE /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`                                                                                                                                                                  | `IntegrationPermissionManager`                                                                                    | `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-request`, `not-found`                                                |
| `eg.events.list()`, `list_all()`      | `GET /locations/{locationId}/events`                                                                                                                                                                                                                           | `IntegrationEventReader`                                                                                          | `invalid-request`, `not-found`                                                                                                      |
| `eg.events.get()`                     | `GET /locations/{locationId}/events/{eventId}`                                                                                                                                                                                                                 | `IntegrationEventReader`                                                                                          | `invalid-request`, `not-found`                                                                                                      |

<!-- generated:operations:end -->
