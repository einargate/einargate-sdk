import {
  CamerasResource,
  GatesResource,
  LocationResource,
  MembersResource,
  RootResource,
} from './generated/resources.js'
import { getMeSpec } from './generated/operations.js'
import { EventsResource } from './helpers/events.js'
import { PermissionsResource } from './helpers/permissions.js'
import { apiKeyProblem } from './runtime/api-key.js'
import { ClientContext } from './runtime/context.js'
import { success } from './runtime/result.js'
import { sleep } from './runtime/transport.js'
import { VERSION } from './version.js'

export interface EinarGateOptions {
  /**
   * An API key value, `egk_…`, created in the Einar Gate app. Defaults to
   * the `EINARGATE_API_KEY` environment variable. Keep it on the server:
   * the API has no CORS on purpose.
   */
  readonly apiKey?: string
  /**
   * The API key's location. When left out, the first call that needs it
   * reads it from `GET /me`.
   */
  readonly locationId?: string
  /** Defaults to `https://api.einargate.com/v1` */
  readonly baseUrl?: string
  /** Per attempt, in milliseconds; defaults to 30 000 */
  readonly timeoutMs?: number
  /**
   * Retries of a call that failed in a way that is safe to retry: network
   * errors, timeouts, `rate-limited` per second, `provisioning`,
   * `service-unavailable` and an in-flight idempotency key. Defaults to 2.
   */
  readonly maxRetries?: number
  /** A `fetch` to use instead of the global one, e.g. for a proxy */
  readonly fetch?: typeof globalThis.fetch
  /** Your integration, added to the `User-Agent`: `{ name: 'acme-sync', version: '1.2.0' }` */
  readonly appInfo?: { readonly name: string; readonly version?: string }
}

export const DEFAULT_BASE_URL = 'https://api.einargate.com/v1'

const PROBLEM_TYPE_BASE_URI = 'https://developers.einargate.com/errors/'

/**
 * The Einar Gate API client. Every call returns a `Result`: check
 * `success`, then use `data` or switch on `error.type`. Calls never throw
 * for anything the API or the network does.
 *
 * ```ts
 * const eg = new EinarGate()
 * const gates = await eg.gates.listAll()
 * if (!gates.success) throw new Error(gates.error.message)
 * ```
 */
export class EinarGate extends RootResource {
  /** The API key's location */
  readonly location: LocationResource
  /** Members and invitees of the location, who own permissions */
  readonly members: MembersResource
  readonly gates: GatesResource
  readonly cameras: CamerasResource
  /** License plate permissions, one per camera */
  readonly permissions: PermissionsResource
  /** Gate openings */
  readonly events: EventsResource

  constructor(options: EinarGateOptions = {}) {
    const context = createContext(options)
    super(context)
    this.location = new LocationResource(context)
    this.members = new MembersResource(context)
    this.gates = new GatesResource(context)
    this.cameras = new CamerasResource(context)
    this.permissions = new PermissionsResource(context)
    this.events = new EventsResource(context)
  }
}

function createContext(options: EinarGateOptions): ClientContext {
  const apiKey = options.apiKey ?? environment('EINARGATE_API_KEY')
  if (apiKey === undefined || apiKey === '') {
    throw new TypeError(
      'EinarGate needs an API key: pass `apiKey` or set the ' +
        'EINARGATE_API_KEY environment variable. API keys are created in ' +
        'the Einar Gate app, under the location’s API keys.'
    )
  }
  const problem = apiKeyProblem(apiKey)
  if (problem !== undefined) {
    throw new TypeError(
      `The Einar Gate API key is not valid: ${problem}. An API key value ` +
        'looks like egk_ followed by 36 letters and digits.'
    )
  }

  const fetchFunction = options.fetch ?? globalThis.fetch
  if (typeof fetchFunction !== 'function') {
    throw new TypeError(
      'EinarGate needs fetch: use Node.js 22 or later, or pass `fetch`'
    )
  }

  const context: ClientContext = new ClientContext(
    {
      apiKey,
      baseUrl: (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, ''),
      fetch: fetchFunction,
      timeoutMs: options.timeoutMs ?? 30_000,
      maxRetries: options.maxRetries ?? 2,
      userAgent: userAgent(options.appInfo),
      problemTypeBaseUri: PROBLEM_TYPE_BASE_URI,
      sleep,
      random: Math.random,
      newIdempotencyKey: () => globalThis.crypto.randomUUID(),
    },
    options.locationId,
    async (callOptions) => {
      const me = await context.send(getMeSpec, callOptions)
      return me.success ? success(me.data.locationId, me.response) : me
    }
  )
  return context
}

function userAgent(appInfo: EinarGateOptions['appInfo']): string {
  const runtime =
    typeof process !== 'undefined' && process.versions?.node
      ? `node/${process.versions.node}`
      : 'javascript'
  const app = appInfo
    ? ` ${appInfo.name}${appInfo.version ? `/${appInfo.version}` : ''}`
    : ''
  return `einargate-typescript/${VERSION} ${runtime}${app}`
}

function environment(name: string): string | undefined {
  return typeof process !== 'undefined' ? process.env?.[name] : undefined
}
