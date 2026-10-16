import { describe, expect, it } from 'vitest'
import {
  EinarGate,
  EinarGateError,
  isUnknown,
  UnknownValue,
  VERSION,
} from '../src/index.js'
import { MOCK_API_KEY, MockEinarGate } from '../src/testing.js'
import { gate, permission } from './fixtures.js'
import packageJson from '../package.json' with { type: 'json' }

const PROBLEMS = 'https://developers.einargate.com/errors/'

function permissionBody(overrides: Record<string, unknown> = {}) {
  return {
    permissionId: 'ABC123|HU',
    locationId: 'mock-location',
    gateId: 'g1',
    cameraId: 'c1',
    licensePlate: 'ABC123',
    licensePlateCountry: 'HU',
    ownerUserId: 'u1',
    active: true,
    numberOfOpenings: 0,
    createdAt: '2026-09-12T10:41:07.000Z',
    updatedAt: '2026-09-12T10:41:07.000Z',
    ...overrides,
  }
}

describe('decoding', () => {
  it('turns a body into the library’s types', async () => {
    const mock = new MockEinarGate().on('getPermission', () => ({
      status: 200,
      body: permissionBody({ licensePlateCountry: '', unknownMember: 1 }),
    }))
    const result = await mock.client().permissions.get(permission)

    expect(result.success).toBe(true)
    const data = result.unwrap()
    expect(data.createdAt).toEqual(new Date('2026-09-12T10:41:07.000Z'))
    expect(data.licensePlateCountry).toBeNull()
    expect(data).not.toHaveProperty('unknownMember')
    expect(data).not.toHaveProperty('supplementalInfo')
    expect(result.success && result.response.requestId).toBe('mock-request')
  })

  it('keeps enum values and union variants it does not know', async () => {
    const mock = new MockEinarGate().on('getEvent', () => ({
      status: 200,
      body: {
        eventId: 'e1',
        type: 'ScheduledGateOpening',
        status: 'finalized',
        locationId: 'mock-location',
        gateId: 'g1',
        eventTime: '2026-09-12T10:41:07.000Z',
        initiator: { type: 'schedule', scheduleId: 's1' },
        attachments: [],
        createdAt: '2026-09-12T10:41:07.000Z',
        updatedAt: '2026-09-12T10:41:07.000Z',
      },
    }))
    const event = (await mock.client().events.get({ eventId: 'e1' })).unwrap()

    expect(isUnknown(event.type)).toBe(true)
    expect(String(event.type)).toBe('ScheduledGateOpening')
    expect(event.initiator?.type).toBeInstanceOf(UnknownValue)
    expect(JSON.parse(JSON.stringify(event)).type).toBe('ScheduledGateOpening')
  })

  it('reports a body that breaks the contract as unexpected-response', async () => {
    const mock = new MockEinarGate().on('getGate', () => ({
      status: 200,
      body: { gateId: 'g1', name: 'Main gate' },
    }))
    const result = await mock.client().gates.get(gate)

    expect(result.success).toBe(false)
    if (!result.success && result.error.type === 'unexpected-response') {
      expect(result.error.path).toBe('locationId')
      expect(result.error.requestId).toBe('mock-request')
    } else {
      expect.fail('expected unexpected-response')
    }
  })
})

describe('errors', () => {
  it('returns a declared problem with its hint and docs URL', async () => {
    const mock = new MockEinarGate().on('openGate', () => ({
      problem: 'gate-not-operable',
      detail: 'The control camera is offline',
    }))
    const result = await mock.client().gates.open(gate)

    if (result.success || result.error.type !== 'gate-not-operable') {
      expect.fail('expected gate-not-operable')
    }
    expect(result.error.status).toBe(422)
    expect(result.error.docsUrl).toBe(`${PROBLEMS}gate-not-operable`)
    expect(result.error.hint).toMatch(/control camera/)
    expect(result.error.message).toMatch(
      /Gate not operable \(422 gate-not-operable\): The control camera is offline\. .*Request id mock-request/
    )
  })

  it('treats an undeclared or unknown type and a non-problem body as unknown-problem', async () => {
    const mock = new MockEinarGate()
      .on('getGate', () => ({
        status: 422,
        body: {
          type: `${PROBLEMS}invalid-owner`,
          title: 'Invalid owner',
          status: 422,
          requestId: 'r1',
        },
      }))
      .on('listGates', () => ({ status: 418, body: '<html>teapot</html>' }))
    const eg = mock.client()

    const undeclared = await eg.gates.get(gate)
    expect(!undeclared.success && undeclared.error.type).toBe('unknown-problem')
    if (!undeclared.success && undeclared.error.type === 'unknown-problem') {
      expect(undeclared.error.problemType).toBe(`${PROBLEMS}invalid-owner`)
      expect(undeclared.error.requestId).toBe('r1')
    }

    const notProblem = await eg.gates.list()
    expect(!notProblem.success && notProblem.error.type).toBe('unknown-problem')
  })

  it('returns network failures, timeouts and aborts instead of throwing', async () => {
    const failing = new EinarGate({
      apiKey: MOCK_API_KEY,
      locationId: 'l1',
      maxRetries: 0,
      fetch: async () => {
        throw new TypeError('fetch failed', { cause: new Error('ECONNRESET') })
      },
    })
    const network = await failing.gates.list()
    expect(!network.success && network.error.type).toBe('network')
    expect(!network.success && network.error.message).toMatch(/ECONNRESET/)

    const hanging = new EinarGate({
      apiKey: MOCK_API_KEY,
      locationId: 'l1',
      maxRetries: 0,
      timeoutMs: 20,
      fetch: (_input, init) =>
        new Promise((_resolve, reject) =>
          init?.signal?.addEventListener('abort', () =>
            reject(init.signal?.reason)
          )
        ),
    })
    const timeout = await hanging.gates.list()
    expect(!timeout.success && timeout.error.type).toBe('timeout')

    const controller = new AbortController()
    const pending = hanging.gates.list(
      {},
      { signal: controller.signal, timeoutMs: 5_000 }
    )
    controller.abort()
    const aborted = await pending
    expect(!aborted.success && aborted.error.type).toBe('aborted')
  })

  it('checks the status against the contract', async () => {
    const mock = new MockEinarGate()
      .on('deletePermission', () => ({ status: 202, body: { pending: true } }))
      .on('replacePermission', () => ({
        status: 500,
        body: {
          type: `${PROBLEMS}service-unavailable`,
          title: 'Service unavailable',
          status: 503,
          requestId: 'r1',
        },
      }))
    const eg = mock.client({ maxRetries: 2 })

    const deleted = await eg.permissions.delete(permission)
    expect(!deleted.success && deleted.error.type).toBe('unexpected-response')

    const replaced = await eg.permissions.update(permission, { active: false })
    if (replaced.success || replaced.error.type !== 'unknown-problem') {
      expect.fail('expected unknown-problem')
    }
    expect(replaced.error.status).toBe(500)
    expect(mock.callsOf('replacePermission')).toHaveLength(1)
  })

  it('treats a type named after an object property as unknown', async () => {
    for (const slug of ['__proto__', 'constructor', 'toString']) {
      const mock = new MockEinarGate().on('getGate', () => ({
        status: 404,
        body: {
          type: `${PROBLEMS}${slug}`,
          title: 'x',
          status: 404,
          requestId: 'r',
        },
      }))
      const result = await mock.client().gates.get(gate)
      expect(!result.success && result.error.type).toBe('unknown-problem')
    }
  })

  it('throws an EinarGateError from unwrap', async () => {
    const mock = new MockEinarGate().on('getGate', () => ({
      problem: 'not-found',
    }))
    const result = await mock.client().gates.get(gate)
    expect(() => result.unwrap()).toThrow(EinarGateError)
    try {
      result.unwrap()
    } catch (error) {
      expect((error as EinarGateError).error.type).toBe('not-found')
    }
  })
})

describe('retries', () => {
  it('retries a per-second rate limit after Retry-After, but not a daily one', async () => {
    let calls = 0
    const mock = new MockEinarGate().on('listGates', () =>
      ++calls === 1
        ? {
            problem: 'rate-limited',
            extensions: { window: 'second' as const },
            headers: { 'Retry-After': '0' },
          }
        : { data: { items: [gate] } }
    )
    const result = await mock.client({ maxRetries: 2 }).gates.list()
    expect(result.success).toBe(true)
    expect(calls).toBe(2)

    const daily = new MockEinarGate().on('listGates', () => ({
      problem: 'rate-limited',
      extensions: { window: 'day' as const },
    }))
    const exhausted = await daily.client({ maxRetries: 2 }).gates.list()
    expect(!exhausted.success && exhausted.error.type).toBe('rate-limited')
    expect(daily.calls).toHaveLength(1)
  })

  it('sends one idempotency key for a write and all its retries', async () => {
    let calls = 0
    const mock = new MockEinarGate().on('openGate', () =>
      ++calls < 3
        ? calls === 1
          ? {
              problem: 'idempotency-key-in-flight',
              headers: { 'Retry-After': '0' },
            }
          : {
              problem: 'rate-limited',
              extensions: { window: 'second' as const },
              headers: { 'Retry-After': '0' },
            }
        : {
            data: {
              eventId: 'e1',
              type: 'ManualGateOpening',
              status: 'pending',
              locationId: 'mock-location',
              gateId: 'g1',
              eventTime: new Date(),
              createdAt: new Date(),
              updatedAt: new Date(),
            },
          }
    )
    const result = await mock.client({ maxRetries: 2 }).gates.open(gate)

    expect(result.success).toBe(true)
    const keys = mock.calls.map((call) => call.headers['idempotency-key'])
    expect(keys).toHaveLength(3)
    expect(new Set(keys).size).toBe(1)
    expect(keys[0]).toMatch(/^[0-9a-f-]{36}$/)

    await mock.client().gates.open(gate, { idempotencyKey: 'open-g1-42' })
    expect(mock.calls.at(-1)?.headers['idempotency-key']).toBe('open-g1-42')
  })

  it('does not retry a write that may have run, and says how to retry it', async () => {
    const mock = new MockEinarGate()
      .on('openGate', () => ({ problem: 'service-unavailable' }))
      .on('listGates', () => ({ problem: 'service-unavailable' }))
    const eg = mock.client({ maxRetries: 2 })

    const opened = await eg.gates.open(gate, { idempotencyKey: 'open-1' })
    expect(mock.callsOf('openGate')).toHaveLength(1)
    expect(!opened.success && opened.idempotencyKey).toBe('open-1')
    expect(!opened.success && opened.error.message).toMatch(
      /may have happened: check its effect .* idempotencyKey 'open-1'/
    )

    const timedOut = await new EinarGate({
      apiKey: MOCK_API_KEY,
      locationId: 'l1',
      maxRetries: 2,
      timeoutMs: 10,
      fetch: (_input, init) =>
        new Promise((_resolve, reject) =>
          init?.signal?.addEventListener('abort', () =>
            reject(init.signal?.reason)
          )
        ),
    }).gates.open(gate)
    expect(!timedOut.success && timedOut.error.type).toBe('timeout')
    expect(!timedOut.success && timedOut.idempotencyKey).toMatch(
      /^[0-9a-f-]{36}$/
    )
  })

  it('says a write ran after unexpected-response, and nothing before sending', async () => {
    const mock = new MockEinarGate().on('openGate', () => ({
      status: 200,
      body: {},
    }))
    const eg = mock.client({ maxRetries: 2 })

    const opened = await eg.gates.open(gate, { idempotencyKey: 'open-1' })
    expect(mock.callsOf('openGate')).toHaveLength(1)
    expect(!opened.success && opened.error.type).toBe('unexpected-response')
    expect(!opened.success && opened.idempotencyKey).toBe('open-1')
    expect(!opened.success && opened.error.message).toMatch(
      /The write ran: do not send it again/
    )

    const notSent = await eg.gates.open(gate, {
      idempotencyKey: 'open-2',
      signal: AbortSignal.abort(),
    })
    expect(mock.callsOf('openGate')).toHaveLength(1)
    expect(!notSent.success && notSent.error.type).toBe('aborted')
    expect(!notSent.success && notSent.idempotencyKey).toBe('open-2')
    expect(!notSent.success && notSent.error.message).not.toMatch(/write/)
  })

  it('retries a write that could not connect', async () => {
    let attempts = 0
    const refused = new EinarGate({
      apiKey: MOCK_API_KEY,
      locationId: 'l1',
      maxRetries: 1,
      fetch: async () => {
        attempts++
        throw new TypeError('fetch failed', {
          cause: Object.assign(new Error('connect ECONNREFUSED'), {
            code: 'ECONNREFUSED',
          }),
        })
      },
    })
    const result = await refused.gates.open(gate)
    expect(attempts).toBe(2)
    expect(
      !result.success &&
        result.error.type === 'network' &&
        result.error.requestSent
    ).toBe(false)
  })

  it('does not retry a 500 on a write, but does on a read', async () => {
    const mock = new MockEinarGate()
      .on('deletePermission', () => ({ problem: 'internal' }))
      .on('getPermission', () => ({ problem: 'internal' }))
    const eg = mock.client({ maxRetries: 1 })

    await eg.permissions.delete(permission)
    expect(mock.callsOf('deletePermission')).toHaveLength(1)

    await eg.permissions.get(permission)
    expect(mock.callsOf('getPermission')).toHaveLength(2)
  })
})

describe('requests', () => {
  it('reads the location from GET /me once, and again after a failure', async () => {
    let meCalls = 0
    const mock = new MockEinarGate()
      .on('getMe', () =>
        ++meCalls === 1
          ? { problem: 'service-unavailable' }
          : {
              data: {
                apiKeyId: 'k1',
                name: 'Sync',
                locationId: 'loc-from-me',
                roles: ['IntegrationSetupReader'],
                subscriptionActive: true,
                rateLimit: {
                  requestsPerSecond: 17,
                  burst: 200,
                  requestsPerDay: 100000,
                },
              },
            }
      )
      .on('listGates', () => ({ data: { items: [] } }))
    const eg = mock.client({ locationId: undefined })

    const first = await eg.gates.list()
    expect(!first.success && first.error.type).toBe('service-unavailable')
    await eg.gates.list()
    await eg.gates.list()

    expect(meCalls).toBe(2)
    expect(mock.callsOf('listGates').map((call) => call.path)).toEqual([
      '/locations/loc-from-me/gates',
      '/locations/loc-from-me/gates',
    ])
  })

  it('lets one caller abort its wait for the location without the others', async () => {
    let answer: (() => void) | undefined
    const mock = new MockEinarGate()
      .on(
        'getMe',
        () =>
          new Promise((resolve) => {
            answer = () =>
              resolve({
                data: {
                  apiKeyId: 'k1',
                  name: 'Sync',
                  locationId: 'loc-from-me',
                  roles: [],
                  subscriptionActive: true,
                  rateLimit: {
                    requestsPerSecond: 17,
                    burst: 200,
                    requestsPerDay: 100000,
                  },
                },
              })
          })
      )
      .on('listGates', () => ({ data: { items: [] } }))
    const eg = mock.client({ locationId: undefined })
    const controller = new AbortController()

    const first = eg.gates.list({}, { signal: controller.signal })
    const second = eg.gates.list()
    await new Promise((resolve) => setTimeout(resolve, 5))
    controller.abort()
    expect((await first).success).toBe(false)
    answer?.()
    expect((await second).success).toBe(true)
    expect(mock.callsOf('getMe')).toHaveLength(1)
  })

  it('applies a caller\u2019s timeout to its wait for the location', async () => {
    const mock = new MockEinarGate()
      .on('getMe', () => new Promise(() => undefined))
      .on('listGates', () => ({ data: { items: [] } }))
    const started = Date.now()
    const result = await mock
      .client({ locationId: undefined })
      .gates.list({}, { timeoutMs: 20 })
    expect(!result.success && result.error.type).toBe('timeout')
    expect(Date.now() - started).toBeLessThan(1_000)
  })

  it('creates a permission at the scope `at` names', async () => {
    const created = { data: { created: [permission] as const, failed: [] } }
    const mock = new MockEinarGate()
      .on('createLocationPermission', () => created)
      .on('createGatePermission', () => created)
      .on('createCameraPermission', () => created)
    const eg = mock.client()
    const body = { licensePlate: 'abc-123', ownerUserId: 'u1', active: true }

    await eg.permissions.create({ ...body, at: 'location' })
    await eg.permissions.create({
      ...body,
      at: { gateId: 'g1' },
      licensePlateCountry: null,
    })
    await eg.permissions.create({
      ...body,
      at: { gateId: 'g1', cameraId: 'c1' },
      licensePlateCountry: 'HU',
    })

    expect(mock.calls.map((call) => call.operationId)).toEqual([
      'createLocationPermission',
      'createGatePermission',
      'createCameraPermission',
    ])
    expect(mock.calls.map((call) => call.body)).toEqual([
      body,
      { ...body, licensePlateCountry: '' },
      { ...body, licensePlateCountry: 'HU' },
    ])
    expect(mock.calls[2].params).toEqual({
      locationId: 'mock-location',
      gateId: 'g1',
      cameraId: 'c1',
    })
  })

  it('URL-encodes ids and sends the scope of a listing as filters', async () => {
    const mock = new MockEinarGate()
      .on('deletePermission', () => ({ data: undefined }))
      .on('listPermissions', () => ({ data: { items: [] } }))
    const eg = mock.client()

    await eg.permissions.delete(permission)
    expect(mock.calls[0].path).toBe(
      '/locations/mock-location/gates/g1/cameras/c1/permissions/ABC123%7CHU'
    )

    await eg.permissions.list({
      at: { gateId: 'g1', cameraId: 'c1' },
      active: false,
    })
    expect(mock.calls[1].query).toEqual({
      gateId: 'g1',
      cameraId: 'c1',
      active: 'false',
    })
  })

  it('replaces with supplementalInfo null as a removal, and updates from the permission', async () => {
    const mock = new MockEinarGate().on('replacePermission', () => ({
      data: permission,
    }))
    const eg = mock.client()

    await eg.permissions.replace(permission, {
      licensePlate: 'ABC123',
      licensePlateCountry: null,
      active: true,
      supplementalInfo: null,
    })
    expect(mock.calls[0].body).toEqual({
      licensePlate: 'ABC123',
      licensePlateCountry: '',
      active: true,
    })

    await eg.permissions.update(permission, { active: false })
    expect(mock.calls[1].body).toEqual({
      licensePlate: 'ABC123',
      licensePlateCountry: 'HU',
      active: false,
      supplementalInfo: 'Visitor',
    })
  })

  it('collects every page with listAll', async () => {
    const mock = new MockEinarGate().on('listGates', (call) =>
      call.query.continuationToken === undefined
        ? { data: { items: [gate], continuationToken: 'next' } }
        : { data: { items: [{ ...gate, gateId: 'g2' }] } }
    )
    const gates = (await mock.client().gates.listAll()).unwrap()

    expect(gates.map((g) => g.gateId)).toEqual(['g1', 'g2'])
    expect(mock.calls.map((call) => call.query)).toEqual([
      { limit: '200' },
      { limit: '200', continuationToken: 'next' },
    ])
  })

  it('sends a User-Agent with the version and the app', async () => {
    const mock = new MockEinarGate().on('listGates', () => ({
      data: { items: [] },
    }))
    await mock
      .client({ appInfo: { name: 'acme-sync', version: '1.2.0' } })
      .gates.list()
    expect(mock.calls[0].headers['user-agent']).toMatch(
      new RegExp(`^einargate-typescript/${VERSION} .* acme-sync/1\\.2\\.0$`)
    )
    expect(mock.calls[0].headers.authorization).toBe(`Bearer ${MOCK_API_KEY}`)
  })

  it('keeps VERSION equal to package.json’s', () => {
    expect(VERSION).toBe(packageJson.version)
  })
})
