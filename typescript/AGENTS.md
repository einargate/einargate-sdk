# Einar Gate API, TypeScript client: guide for coding agents

> **Very early alpha.** The Einar Gate public API is not generally
> available yet, and this client may change in breaking ways before 1.0:
> pin an exact version.

This is everything you need to write correct code against the Einar Gate
API with `@einargate/sdk`. The types are the contract: if your code
compiles, it handles every case the API can produce. Read the rules below
once; the operations table at the end lists what each call needs and returns.

## Setup

```ts
import { EinarGate } from '@einargate/sdk'

// Reads the EINARGATE_API_KEY environment variable; or pass { apiKey }.
// An API key value looks like egk_ + 36 letters and digits. It is created
// in the Einar Gate app by a location Owner or Admin, who also picks its
// roles. Keep it on the server: the API has no CORS on purpose.
const eg = new EinarGate({ appInfo: { name: 'acme-sync', version: '1.0.0' } })

const me = await eg.me()
if (me.success) {
  console.log(me.data.name, me.data.roles, me.data.rateLimit)
}
```

Node.js 22.12 or later, Bun or Deno. No runtime dependencies.

## Rules

1. **Every call returns a `Result` and never throws** for anything the API
   or the network does. Check `result.success`, then use `result.data`, or
   switch on `result.error.type`. Only the constructor throws, for a
   missing or malformed API key. `result.unwrap()` returns the data or
   throws an `EinarGateError`; use it in scripts that should stop at the
   first failure.
2. **`error.type` is one flat discriminator.** It is a problem type of the
   call (`not-found`, `limit-exceeded`, …), `unknown-problem` (an error the
   API added after this version, or a body that is not a problem: handle it
   by `status`), `network`, `timeout`, `aborted`, or `unexpected-response`
   (a body that breaks the contract: a bug on the API's side). Each call's
   error union, e.g. `CreatePermissionError`, lists exactly its types.
   Every problem has `message` (one line for logs), `hint` (what to do),
   `detail`, `requestId` and `docsUrl`.
3. **Never pass a location id.** The client is bound to the API key's
   location: it reads it from `GET /me` on first use, or takes
   `locationId` in its options.
4. **Do not write your own retry loop.** The client retries a read after a
   network error, a timeout, a 5xx or `rate-limited` with
   `window: 'second'`, with backoff and `Retry-After`, up to `maxRetries`
   (2). It retries a write only when the write cannot have run:
   `rate-limited` per second, `provisioning`, `idempotency-key-in-flight`,
   or no connection at all. `rate-limited` with `window: 'day'` means the
   daily quota is used up.
5. **A write that may have run comes back to you, with its key.** Every
   `POST`, `PUT` and `DELETE` sends an `Idempotency-Key`. After a timeout, a
   network error once the request was sent, or a 5xx, the write may have
   happened, and opening a gate twice is not a retry's call to make: the
   failure carries `result.idempotencyKey`, and its message says so. Check
   the effect first (for a gate opening, `events.list`; for a permission,
   `permissions.listAll({ licensePlate })`). If you send it again, pass
   `{ idempotencyKey: result.idempotencyKey }`: the API replays the first
   response if that write completed, but runs it again if the API failed
   after running it, since it does not keep the key of a failed write. To
   stay safe across restarts of your process, pass your own key derived
   from your data: `{ idempotencyKey: 'open-g1-42' }`.
   `result.response.replayed` is `true` when the write had already happened.
   After `unexpected-response` the write ran, but its answer broke the
   contract: check its effect, and do not send it again.
6. **Values the API adds later are `UnknownValue`.** Every enum and union in
   a response includes it (e.g. `camera.status: CameraStatus | UnknownValue`),
   so an exhaustive `switch` needs a `default` branch. `String(value)` gives
   the raw value; `isUnknown(value)` tests for it.
7. **Ids are opaque.** Use them exactly as returned; never build or parse
   one. The client URL-encodes them. Pass an entity where a reference is
   asked for: `eg.permissions.delete(permission)`, `eg.gates.open(gate)`,
   or the ids as an object: `eg.gates.open({ gateId })`.
8. **Permissions are per camera.** A plate permitted at a gate with two
   cameras is two permissions. Create at a scope with `at`: `'location'`
   (every camera), `{ gateId }` (every camera of a gate) or
   `{ gateId, cameraId }`. A create succeeds when at least one camera got
   the plate: `data.created` is never empty, and `data.failed` lists the
   cameras that did not, each with a `conflict` or `limit-exceeded` problem.
   Find a plate's permissions with `listAll({ licensePlate })`.
9. **`replace` is a full replacement; prefer `update`.** `replace` removes
   every field you leave out, so it requires `supplementalInfo` (`null`
   removes it). `eg.permissions.update(permission, { active: false })`
   keeps the other fields. Changing the plate or country changes the
   `permissionId`: use the returned permission from then on.
10. **`licensePlateCountry: null` means no country.** On create, leaving it
    out applies the location's `defaultLicensePlateCountry`.
11. **`forbidden` means a missing role.** Each method's doc comment and the
    table below name the roles that allow it; `eg.me()` shows the key's.
12. **Timestamps are `Date`s.** Filters such as `events.list({ from })`
    take `Date`s too.

## Recipes

### Sync permissions from your system

```ts
import { EinarGate, type Permission } from '@einargate/sdk'

const eg = new EinarGate()

/** The plates your system says may enter, with their owner's user id */
const wanted = new Map([
  ['ABC123', 'user-1'],
  ['XYZ789', 'user-2'],
])

const existing = await eg.permissions.listAll()
if (!existing.success) {
  throw new Error(existing.error.message)
}

const byPlate = new Map<string, Permission[]>()
for (const permission of existing.data) {
  byPlate.set(permission.licensePlate, [
    ...(byPlate.get(permission.licensePlate) ?? []),
    permission,
  ])
}

for (const [plate, ownerUserId] of wanted) {
  if (byPlate.has(plate)) {
    continue
  }
  const created = await eg.permissions.create({
    at: 'location',
    licensePlate: plate,
    ownerUserId,
    active: true,
  })
  if (!created.success) {
    console.error(`${plate}: ${created.error.message}`)
  } else {
    for (const failed of created.data.failed) {
      console.warn(
        `${plate} at camera ${failed.cameraId}: ${failed.error.message}`
      )
    }
  }
}

for (const [plate, permissions] of byPlate) {
  if (wanted.has(plate)) {
    continue
  }
  for (const permission of permissions) {
    const deleted = await eg.permissions.delete(permission)
    if (!deleted.success && deleted.error.type !== 'not-found') {
      console.error(`${plate}: ${deleted.error.message}`)
    }
  }
}
```

### Open a gate and get its snapshots

```ts
import { EinarGate } from '@einargate/sdk'

const eg = new EinarGate()

const opened = await eg.gates.open({ gateId: 'gate-id' })
if (!opened.success) {
  switch (opened.error.type) {
    case 'gate-not-operable':
      console.error('The gate cannot be opened now:', opened.error.detail)
      break
    case 'forbidden':
      console.error('The API key needs the IntegrationGateOperator role')
      break
    default:
      console.error(opened.error.message)
  }
} else {
  const event = await eg.events.waitForAttachments(opened.data)
  if (event.success) {
    for (const attachment of event.data.attachments) {
      console.log(attachment.role, attachment.url) // valid for 15 minutes
    }
  }
}
```

### Follow new gate openings

```ts
import { EinarGate } from '@einargate/sdk'

const eg = new EinarGate()
const controller = new AbortController()

for await (const result of eg.events.follow(
  { type: 'AutomaticGateOpening' },
  { signal: controller.signal }
)) {
  if (!result.success) {
    console.error(result.error.message)
    break
  }
  console.log(result.data.eventTime, result.data.plate?.text)
}
```

### Test without a real location

There is no sandbox, so test against the typed mock. It runs the real
client against answers you register per operation:

```ts
import { MockEinarGate } from '@einargate/sdk/testing'

const mock = new MockEinarGate()
mock.on('openGate', () => ({
  problem: 'gate-not-operable',
  detail: 'The control camera is offline',
}))

const eg = mock.client()
const result = await eg.gates.open({ gateId: 'g1' })
console.assert(!result.success && result.error.type === 'gate-not-operable')
console.assert(mock.callsOf('openGate').length === 1)
```

## Operations

`Errors` lists each call's own problem types; every authenticated call can
also return `unauthorized`, `forbidden`, `rate-limited`, `provisioning`,
`internal`, `service-unavailable` and the `CallError` types.

<!-- generated:operations:start -->

| Call                                 | HTTP                                                                                                                                                                                                                                           | Roles                                                                                                             | Errors                                                                                                                              |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `eg.me()`                            | `GET /me`                                                                                                                                                                                                                                      | any                                                                                                               | –                                                                                                                                   |
| `eg.openApiDocument()`               | `GET /openapi.json`                                                                                                                                                                                                                            | none (no API key)                                                                                                 | `internal`, `rate-limited`, `service-unavailable`                                                                                   |
| `eg.location.get()`                  | `GET /locations/{locationId}`                                                                                                                                                                                                                  | `IntegrationSetupReader`, `IntegrationEventReader`                                                                | `invalid-request`, `not-found`                                                                                                      |
| `eg.members.list()`, `listAll()`     | `GET /locations/{locationId}/members`                                                                                                                                                                                                          | `IntegrationPermissionReader`, `IntegrationPermissionManager`                                                     | `invalid-request`, `not-found`                                                                                                      |
| `eg.gates.list()`, `listAll()`       | `GET /locations/{locationId}/gates`                                                                                                                                                                                                            | any                                                                                                               | `invalid-request`                                                                                                                   |
| `eg.gates.get()`                     | `GET /locations/{locationId}/gates/{gateId}`                                                                                                                                                                                                   | any                                                                                                               | `invalid-request`, `not-found`                                                                                                      |
| `eg.gates.open()`                    | `POST /locations/{locationId}/gates/{gateId}/open`                                                                                                                                                                                             | `IntegrationGateOperator`                                                                                         | `gate-not-operable`, `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-request`, `not-found`                           |
| `eg.cameras.list()`, `listAll()`     | `GET /locations/{locationId}/cameras` (`'location'`)<br>`GET /locations/{locationId}/gates/{gateId}/cameras` (`{ gateId }`)                                                                                                                    | `IntegrationSetupReader`, `IntegrationPermissionReader`, `IntegrationEventReader`, `IntegrationPermissionManager` | `invalid-request`, `not-found`                                                                                                      |
| `eg.cameras.get()`                   | `GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}`                                                                                                                                                                                | `IntegrationSetupReader`, `IntegrationPermissionReader`, `IntegrationEventReader`, `IntegrationPermissionManager` | `invalid-request`, `not-found`                                                                                                      |
| `eg.permissions.list()`, `listAll()` | `GET /locations/{locationId}/permissions`                                                                                                                                                                                                      | `IntegrationPermissionReader`, `IntegrationPermissionManager`                                                     | `invalid-request`                                                                                                                   |
| `eg.permissions.create()`            | `POST /locations/{locationId}/permissions` (`'location'`)<br>`POST /locations/{locationId}/gates/{gateId}/permissions` (`{ gateId }`)<br>`POST /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions` (`{ gateId, cameraId }`) | `IntegrationPermissionManager`                                                                                    | `conflict`, `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-owner`, `invalid-request`, `limit-exceeded`, `not-found` |
| `eg.permissions.get()`               | `GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`                                                                                                                                                     | `IntegrationPermissionReader`, `IntegrationPermissionManager`                                                     | `invalid-request`, `not-found`                                                                                                      |
| `eg.permissions.replace()`           | `PUT /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`                                                                                                                                                     | `IntegrationPermissionManager`                                                                                    | `conflict`, `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-request`, `not-found`                                    |
| `eg.permissions.delete()`            | `DELETE /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`                                                                                                                                                  | `IntegrationPermissionManager`                                                                                    | `idempotency-key-in-flight`, `idempotency-key-reuse`, `invalid-request`, `not-found`                                                |
| `eg.events.list()`, `listAll()`      | `GET /locations/{locationId}/events`                                                                                                                                                                                                           | `IntegrationEventReader`                                                                                          | `invalid-request`, `not-found`                                                                                                      |
| `eg.events.get()`                    | `GET /locations/{locationId}/events/{eventId}`                                                                                                                                                                                                 | `IntegrationEventReader`                                                                                          | `invalid-request`, `not-found`                                                                                                      |

<!-- generated:operations:end -->
