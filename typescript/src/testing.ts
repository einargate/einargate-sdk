/**
 * A typed stand-in for the Einar Gate API, for testing code that uses the
 * client without a real location (the API has no sandbox). Register what
 * each operation answers; the client then runs exactly as against the API:
 * it encodes requests, decodes responses and maps problems the same way.
 *
 * ```ts
 * import { MockEinarGate } from '@einargate/sdk/testing'
 *
 * const mock = new MockEinarGate()
 * mock.on('openGate', () => ({ problem: 'gate-not-operable' }))
 * const eg = mock.client()
 * const result = await eg.gates.open({ gateId: 'g1' })
 * // result.success === false, result.error.type === 'gate-not-operable'
 * ```
 *
 * A call to an operation with no `on(...)` comes back as a `network` error
 * whose message names the operation to register.
 */

import { EinarGate, type EinarGateOptions } from './client.js'
import {
  OPERATIONS,
  type OperationId,
  type OperationTypes,
} from './generated/operations.js'
import { type Problem, PROBLEM_TYPES } from './generated/types.js'
import { checksum } from './runtime/api-key.js'
import type { ProblemFields } from './runtime/errors.js'

/** A well-formed API key value that no real API key has */
export const MOCK_API_KEY = mockApiKey()

/** The location the mock client is bound to unless told otherwise */
export const MOCK_LOCATION_ID = 'mock-location'

/** A request the client sent */
export interface MockCall {
  readonly operationId: OperationId
  readonly method: string
  /** E.g. `/locations/mock-location/gates/g1/open` */
  readonly path: string
  /** The path parameters, decoded */
  readonly params: Readonly<Record<string, string>>
  readonly query: Readonly<Record<string, string>>
  /** The parsed JSON body, if any */
  readonly body: unknown
  readonly headers: Readonly<Record<string, string>>
}

type ProblemsOf<Op extends OperationId> = OperationTypes[Op]['problems']
type ProblemBySlug = { [P in Problem as P['type']]: P }
type ProblemExtensions<S extends keyof ProblemBySlug> = Omit<
  ProblemBySlug[S],
  keyof ProblemFields<string, number>
>

/** What a mocked operation answers */
export type MockReply<Op extends OperationId> =
  /** Success, with the operation's data as the client returns it */
  | {
      readonly data: OperationTypes[Op]['data']
      readonly headers?: Readonly<Record<string, string>>
    }
  /** A problem of a type the operation declares */
  | {
      [S in ProblemsOf<Op>]: {
        readonly problem: S
        readonly detail?: string
        readonly headers?: Readonly<Record<string, string>>
      } & ({} extends ProblemExtensions<S>
        ? { readonly extensions?: ProblemExtensions<S> }
        : { readonly extensions: ProblemExtensions<S> })
    }[ProblemsOf<Op>]
  /** Any response at all, e.g. a body the contract does not allow */
  | {
      readonly status: number
      readonly body?: unknown
      readonly headers?: Readonly<Record<string, string>>
    }

export type MockHandler<Op extends OperationId> = (
  call: MockCall
) => MockReply<Op> | Promise<MockReply<Op>>

const BASE_URL = 'https://api.einargate.test/v1'

export class MockEinarGate {
  /** Every request the client sent, in order */
  readonly calls: MockCall[] = []
  private readonly handlers = new Map<OperationId, MockHandler<OperationId>>()

  /** Sets what an operation answers; the last handler set wins */
  on<Op extends OperationId>(operationId: Op, handler: MockHandler<Op>): this {
    this.handlers.set(operationId, handler as MockHandler<OperationId>)
    return this
  }

  /**
   * A client that sends its requests to this mock. It is bound to
   * `MOCK_LOCATION_ID` and does not retry unless told otherwise.
   */
  client(options: Omit<EinarGateOptions, 'apiKey' | 'fetch'> = {}): EinarGate {
    return new EinarGate({
      locationId: MOCK_LOCATION_ID,
      maxRetries: 0,
      ...options,
      apiKey: MOCK_API_KEY,
      baseUrl: BASE_URL,
      fetch: this.fetch,
    })
  }

  /** The calls of one operation */
  callsOf(operationId: OperationId): MockCall[] {
    return this.calls.filter((call) => call.operationId === operationId)
  }

  readonly fetch: typeof globalThis.fetch = async (input, init) => {
    const url = new URL(
      typeof input === 'string' || input instanceof URL ? input : input.url
    )
    const method = (init?.method ?? 'GET').toUpperCase()
    const path = url.pathname.replace(/^\/v1/, '')
    const match = matchOperation(method, path)
    if (!match) {
      throw new TypeError(`MockEinarGate: no operation is ${method} ${path}`)
    }

    const headers = Object.fromEntries(
      new Headers(init?.headers).entries()
    ) as Record<string, string>
    const text = typeof init?.body === 'string' ? init.body : undefined
    const call: MockCall = {
      operationId: match.id,
      method,
      path,
      params: match.params,
      query: Object.fromEntries(url.searchParams.entries()),
      body: text === undefined ? undefined : (JSON.parse(text) as unknown),
      headers,
    }
    this.calls.push(call)

    const handler = this.handlers.get(match.id)
    if (!handler) {
      throw new TypeError(
        `MockEinarGate: nothing answers ${match.id} (${method} ${path}); ` +
          `call mock.on('${match.id}', …) first`
      )
    }
    // As fetch does, give up when the request's signal aborts
    const signal = init?.signal
    if (signal?.aborted) {
      throw signal.reason
    }
    const reply = await new Promise<MockReply<OperationId>>(
      (resolve, reject) => {
        const onAbort = () => reject(signal?.reason)
        signal?.addEventListener('abort', onAbort, { once: true })
        Promise.resolve(handler(call)).then(
          (value) => {
            signal?.removeEventListener('abort', onAbort)
            resolve(value)
          },
          (error: unknown) => {
            signal?.removeEventListener('abort', onAbort)
            reject(error)
          }
        )
      }
    )
    return toResponse(match.id, reply)
  }
}

function matchOperation(
  method: string,
  path: string
): { id: OperationId; params: Record<string, string> } | undefined {
  for (const [id, spec] of Object.entries(OPERATIONS)) {
    if (spec.method !== method) {
      continue
    }
    const names: string[] = []
    const pattern = spec.path.replace(/\{([^{}]+)\}/g, (_, name: string) => {
      names.push(name)
      return '([^/]+)'
    })
    const found = new RegExp(`^${pattern}$`).exec(path)
    if (found) {
      return {
        id: id as OperationId,
        params: Object.fromEntries(
          names.map((name, index) => [
            name,
            decodeURIComponent(found[index + 1]),
          ])
        ),
      }
    }
  }
  return undefined
}

function toResponse(
  operationId: OperationId,
  reply: MockReply<OperationId>
): Response {
  const spec = OPERATIONS[operationId]
  const headers = { ...reply.headers }

  if ('data' in reply) {
    const encode = spec.encode as ((value: unknown) => unknown) | undefined
    return json(
      spec.status,
      encode ? encode(reply.data) : undefined,
      'application/json',
      headers
    )
  }
  if ('problem' in reply) {
    const type = PROBLEM_TYPES[reply.problem as keyof typeof PROBLEM_TYPES]
    const { extensions, detail } = reply as {
      extensions?: Record<string, unknown>
      detail?: string
    }
    return json(
      type.status,
      {
        type: type.docsUrl,
        title: type.title,
        status: type.status,
        ...(detail !== undefined && { detail }),
        requestId: 'mock-request',
        ...extensions,
      },
      'application/problem+json',
      headers
    )
  }
  return json(reply.status, reply.body, 'application/json', headers)
}

function json(
  status: number,
  body: unknown,
  contentType: string,
  headers: Record<string, string>
): Response {
  const text = body === undefined ? null : JSON.stringify(body)
  return new Response(status === 204 ? null : text, {
    status,
    headers: {
      ...(text !== null && { 'Content-Type': contentType }),
      'x-amzn-RequestId': 'mock-request',
      ...headers,
    },
  })
}

function mockApiKey(): string {
  const body = 'egk_' + 'mock'.padEnd(30, '0')
  return body + checksum(body)
}
