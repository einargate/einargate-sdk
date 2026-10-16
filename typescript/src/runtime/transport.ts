import { DecodeError, type Decoder, type JsonObject } from './decode.js'
import type {
  AnyError,
  CallError,
  NetworkError,
  RequestAborted,
  UnknownProblem,
} from './errors.js'
import { failure, type Result, success } from './result.js'

/**
 * Sends one call: builds the request, retries what is safe to retry, and
 * turns the response into a result. Nothing here throws for anything the
 * API or the network does (ADR-0022).
 */

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'

export interface ProblemInfo {
  /** The response's HTTP status, which must be the problem type's */
  readonly status?: number
  readonly retryAfterSeconds?: number
}

/** Decodes the body of a problem of one declared type */
export type ProblemDecoder = (body: JsonObject, info: ProblemInfo) => AnyError

/** One operation of the API, as the generated code describes it */
export interface OperationSpec<T> {
  readonly id: string
  readonly method: HttpMethod
  /** Relative to the base URL, e.g. `/locations/{locationId}/gates` */
  readonly path: string
  /** The success status the contract declares */
  readonly status: number
  readonly authenticated: boolean
  /** A write that accepts an `Idempotency-Key` */
  readonly idempotent: boolean
  /** Decodes the success body; not set when the success has none */
  readonly decode?: Decoder<T>
  /** Writes success data as the API sends it, for the mock */
  encode?(value: T): unknown
  /** The problem types the operation declares, by slug */
  readonly problems: Readonly<Record<string, ProblemDecoder>>
}

export interface CallOptions {
  /** Aborts the call, retries included */
  readonly signal?: AbortSignal
  /** Per attempt; defaults to the client's `timeoutMs` */
  readonly timeoutMs?: number
}

export interface WriteOptions extends CallOptions {
  /**
   * Makes the write idempotent for 24 hours. A random key is used when not
   * given, so the library's own retries are always safe; pass one derived
   * from your own data to stay safe across restarts of your process.
   */
  readonly idempotencyKey?: string
}

export interface CallInput extends WriteOptions {
  readonly path?: Readonly<Record<string, string>>
  readonly query?: Readonly<Record<string, string | undefined>>
  readonly body?: unknown
}

export interface TransportConfig {
  readonly apiKey: string
  readonly baseUrl: string
  readonly fetch: typeof globalThis.fetch
  readonly timeoutMs: number
  readonly maxRetries: number
  readonly userAgent: string
  readonly problemTypeBaseUri: string
  readonly sleep: (ms: number, signal?: AbortSignal) => Promise<void>
  readonly random: () => number
  readonly newIdempotencyKey: () => string
}

const IDEMPOTENCY_KEY_HEADER = 'Idempotency-Key'
const REPLAYED_HEADER = 'Idempotent-Replayed'
const REQUEST_ID_HEADER = 'x-amzn-requestid'
/** A longer `Retry-After` is returned to the caller rather than waited for */
const MAX_RETRY_AFTER_SECONDS = 60
const BASE_BACKOFF_MS = 500
const MAX_BACKOFF_MS = 8_000

export async function send<T, E extends AnyError>(
  config: TransportConfig,
  spec: OperationSpec<T>,
  input: CallInput
): Promise<Result<T, E | CallError>> {
  const idempotencyKey = spec.idempotent
    ? (input.idempotencyKey ?? config.newIdempotencyKey())
    : undefined
  const request = buildRequest(config, spec, input, idempotencyKey)
  // Aborted before anything was sent: nothing to check before sending it
  if (input.signal?.aborted) {
    return failure(aborted(input.signal.reason), idempotencyKey)
  }

  for (let attempt = 0; ; attempt++) {
    const result = await attemptOnce<T>(config, spec, request, input)
    if (result.success) {
      return result as Result<T, E | CallError>
    }

    const delay =
      attempt < config.maxRetries
        ? retryDelay(config, spec, result.error, attempt)
        : undefined
    if (delay === undefined) {
      return failure(
        idempotencyKey !== undefined
          ? withWriteHint(result.error, idempotencyKey)
          : result.error,
        idempotencyKey
      ) as Result<T, E | CallError>
    }

    await config.sleep(delay, input.signal)
    if (input.signal?.aborted) {
      return failure(aborted(input.signal.reason), idempotencyKey)
    }
  }
}

/**
 * Whether a failed write happened: `ran` when the API answered success in a
 * form the contract does not allow, `maybe` when the API may have run it and
 * then failed or its answer was lost
 */
function writeOutcome(error: AnyError): 'ran' | 'maybe' | 'no' {
  switch (error.type) {
    case 'unexpected-response':
      return 'ran'
    case 'network':
      return (error as NetworkError).requestSent ? 'maybe' : 'no'
    case 'timeout':
    case 'aborted':
    case 'internal':
    case 'service-unavailable':
      return 'maybe'
    case 'unknown-problem':
      return (error as UnknownProblem).status >= 500 ? 'maybe' : 'no'
    default:
      return 'no'
  }
}

/** A failed write's message, with what to do before sending it again */
function withWriteHint<E extends AnyError>(error: E, key: string): E {
  switch (writeOutcome(error)) {
    case 'ran':
      return {
        ...error,
        message:
          `${error.message} The write ran: do not send it again, but check ` +
          `its effect (for a gate opening, the events).`,
      }
    case 'maybe':
      return {
        ...error,
        message:
          `${error.message} The write may have happened: check its effect ` +
          `(for a gate opening, the events) before sending it again. If ` +
          `you do, send it with idempotencyKey '${key}': the API replays ` +
          `the first response if that write completed, but runs it again ` +
          `if the API failed after running it.`,
      }
    case 'no':
      return error
  }
}

interface BuiltRequest {
  readonly url: string
  readonly init: RequestInit
}

function buildRequest(
  config: TransportConfig,
  spec: OperationSpec<unknown>,
  input: CallInput,
  idempotencyKey: string | undefined
): BuiltRequest {
  const path = spec.path.replace(/\{([^{}]+)\}/g, (_, name: string) => {
    const value = input.path?.[name]
    if (value === undefined) {
      throw new TypeError(`${spec.id}: the path parameter ${name} is missing`)
    }
    return encodeURIComponent(value)
  })

  const query = new URLSearchParams()
  for (const [name, value] of Object.entries(input.query ?? {})) {
    if (value !== undefined) {
      query.set(name, value)
    }
  }
  const search = query.size > 0 ? `?${query}` : ''

  const headers: Record<string, string> = {
    Accept: 'application/json, application/problem+json',
    'User-Agent': config.userAgent,
  }
  if (spec.authenticated) {
    headers.Authorization = `Bearer ${config.apiKey}`
  }
  if (idempotencyKey !== undefined) {
    headers[IDEMPOTENCY_KEY_HEADER] = idempotencyKey
  }
  if (input.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  return {
    url: `${config.baseUrl}${path}${search}`,
    init: {
      method: spec.method,
      headers,
      ...(input.body !== undefined && { body: JSON.stringify(input.body) }),
    },
  }
}

const TIMED_OUT = Symbol('timed out')

async function attemptOnce<T>(
  config: TransportConfig,
  spec: OperationSpec<T>,
  request: BuiltRequest,
  input: CallInput
): Promise<Result<T, AnyError>> {
  const signal = input.signal
  if (signal?.aborted) {
    return failure(aborted(signal.reason))
  }

  const timeoutMs = input.timeoutMs ?? config.timeoutMs
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(TIMED_OUT), timeoutMs)
  const onAbort = () => controller.abort(signal?.reason)
  signal?.addEventListener('abort', onAbort, { once: true })

  let response: Response
  let text: string
  try {
    response = await config.fetch(request.url, {
      ...request.init,
      signal: controller.signal,
    })
    text = await response.text()
  } catch (error) {
    if (signal?.aborted) {
      return failure(aborted(signal.reason))
    }
    if (controller.signal.reason === TIMED_OUT) {
      return failure({
        type: 'timeout',
        message: `No response from the Einar Gate API within ${timeoutMs} ms`,
        timeoutMs,
      })
    }
    const requestSent = !isConnectionFailure(error)
    return failure({
      type: 'network',
      message: `The Einar Gate API could not be reached: ${describe(error)}`,
      requestSent,
      cause: error,
    })
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', onAbort)
  }

  const requestId = response.headers.get(REQUEST_ID_HEADER) ?? undefined
  if (response.status === spec.status) {
    return decodeSuccess(spec, response, text, requestId)
  }
  if (response.ok) {
    return failure({
      type: 'unexpected-response',
      message:
        `The Einar Gate API answered ${spec.id} with ${response.status}, ` +
        `where its contract says ${spec.status}. This is a bug on the ` +
        `API's side${requestId ? `; request id ${requestId}` : ''}.`,
      status: response.status,
      ...(requestId !== undefined && { requestId }),
      path: '',
      body: text,
    })
  }
  return failure(decodeError(config, spec, response, text, requestId))
}

function decodeSuccess<T>(
  spec: OperationSpec<T>,
  response: Response,
  text: string,
  requestId: string | undefined
): Result<T, AnyError> {
  const info = {
    status: response.status,
    ...(requestId !== undefined && { requestId }),
    replayed: response.headers.get(REPLAYED_HEADER) === 'true',
  }
  if (!spec.decode) {
    return success(undefined as T, info)
  }

  const body = parseJson(text)
  try {
    if (body === NOT_JSON) {
      throw new DecodeError('', 'a JSON body')
    }
    return success(spec.decode(body, ''), info)
  } catch (error) {
    if (!(error instanceof DecodeError)) {
      throw error
    }
    return failure({
      type: 'unexpected-response',
      message:
        `The Einar Gate API answered ${spec.id} with a body that does not ` +
        `match its contract (${error.message}). This is a bug on the API's ` +
        `side${requestId ? `; request id ${requestId}` : ''}.`,
      status: response.status,
      ...(requestId !== undefined && { requestId }),
      path: error.path,
      body: body === NOT_JSON ? text : body,
    })
  }
}

function decodeError(
  config: TransportConfig,
  spec: OperationSpec<unknown>,
  response: Response,
  text: string,
  requestId: string | undefined
): AnyError {
  const parsed = parseJson(text)
  const body = parsed === NOT_JSON ? text : parsed
  const retryAfterSeconds = parseRetryAfter(response.headers.get('Retry-After'))
  const info = {
    status: response.status,
    ...(retryAfterSeconds !== undefined && { retryAfterSeconds }),
  }

  if (typeof body === 'object' && body !== null && !Array.isArray(body)) {
    const problem = body as JsonObject
    const type = problem.type
    if (
      typeof type === 'string' &&
      type.startsWith(config.problemTypeBaseUri)
    ) {
      const slug = type.slice(config.problemTypeBaseUri.length)
      // Own properties only: `constructor` is not a problem type
      const decoder = Object.hasOwn(spec.problems, slug)
        ? spec.problems[slug]
        : undefined
      if (decoder) {
        try {
          return decoder(problem, info)
        } catch (error) {
          if (!(error instanceof DecodeError)) {
            throw error
          }
        }
      }
    }
  }

  return unknownProblem(response.status, body, requestId, retryAfterSeconds)
}

/** An error body that is not a problem of a declared type */
export function unknownProblem(
  status: number,
  body: unknown,
  requestId?: string,
  retryAfterSeconds?: number
): UnknownProblem {
  const problem =
    typeof body === 'object' && body !== null
      ? (body as Record<string, unknown>)
      : {}
  const text = (key: string) =>
    typeof problem[key] === 'string' ? (problem[key] as string) : undefined
  const problemType = text('type')
  const title = text('title')
  const detail = text('detail')
  const id = text('requestId') ?? requestId

  return {
    type: 'unknown-problem',
    status,
    ...(problemType !== undefined && { problemType }),
    ...(title !== undefined && { title }),
    ...(detail !== undefined && { detail }),
    ...(id !== undefined && { requestId: id }),
    ...(retryAfterSeconds !== undefined && { retryAfterSeconds }),
    message:
      `The Einar Gate API answered ${status}` +
      (problemType
        ? ` with a problem this version does not know (${problemType})`
        : '') +
      (detail ? `: ${detail}` : title ? `: ${title}` : '') +
      `. Handle it by its status.` +
      (id ? ` Request id ${id}.` : ''),
    body,
  }
}

/**
 * How long to wait before retrying, or `undefined` when the error must not
 * be retried.
 *
 * A read is retried after any transient failure. A write is retried only
 * when it cannot have run: the usage plan refused it (`rate-limited` per
 * second, `provisioning`), an earlier attempt with the same idempotency key
 * is still running, or no connection could be made. After a timeout, a
 * network error once the request was sent, or a 5xx, a write may have run
 * (the API releases the idempotency key of a write that fails, so a retry
 * would run it again), and opening a gate twice is not a retry's call to
 * make: the failure goes back to the caller with its idempotency key.
 */
function retryDelay(
  config: TransportConfig,
  spec: OperationSpec<unknown>,
  error: AnyError,
  attempt: number
): number | undefined {
  const read = spec.method === 'GET'
  const backoff = () => {
    const ceiling = Math.min(MAX_BACKOFF_MS, BASE_BACKOFF_MS * 2 ** attempt)
    return Math.round(ceiling / 2 + (ceiling / 2) * config.random())
  }
  const after = (seconds: number | undefined) => {
    if (seconds === undefined) {
      return backoff()
    }
    return seconds <= MAX_RETRY_AFTER_SECONDS ? seconds * 1000 : undefined
  }
  const retryAfter = (error as { retryAfterSeconds?: number }).retryAfterSeconds

  switch (error.type) {
    case 'network':
      return read || !(error as NetworkError).requestSent
        ? backoff()
        : undefined
    case 'timeout':
    case 'internal':
      return read ? backoff() : undefined
    case 'service-unavailable':
      return read ? after(retryAfter) : undefined
    case 'rate-limited':
      return (error as { window?: unknown }).window === 'second'
        ? after(retryAfter)
        : undefined
    case 'provisioning':
    case 'idempotency-key-in-flight':
      return after(retryAfter)
    case 'unknown-problem': {
      const status = (error as UnknownProblem).status
      if (status === 429 || (read && [502, 503, 504].includes(status))) {
        return after(retryAfter)
      }
      return undefined
    }
    default:
      return undefined
  }
}

/** Error codes that mean no connection was made, so nothing was sent */
const CONNECTION_FAILURE_CODES = new Set([
  'ECONNREFUSED',
  'ENOTFOUND',
  'EAI_AGAIN',
  'EHOSTUNREACH',
  'ENETUNREACH',
  'UND_ERR_CONNECT_TIMEOUT',
  // Bun
  'ConnectionRefused',
  'FailedToOpenSocket',
])

function isConnectionFailure(error: unknown): boolean {
  for (let current = error, depth = 0; current && depth < 5; depth++) {
    const code = (current as { code?: unknown }).code
    if (typeof code === 'string' && CONNECTION_FAILURE_CODES.has(code)) {
      return true
    }
    current = (current as { cause?: unknown }).cause
  }
  return false
}

function aborted(reason: unknown): RequestAborted {
  return { type: 'aborted', message: 'The call was aborted', reason }
}

const NOT_JSON = Symbol('not JSON')

function parseJson(text: string): unknown {
  if (text === '') {
    return NOT_JSON
  }
  try {
    return JSON.parse(text) as unknown
  } catch {
    return NOT_JSON
  }
}

function parseRetryAfter(value: string | null): number | undefined {
  if (value === null) {
    return undefined
  }
  if (/^\d+$/.test(value.trim())) {
    return Number(value.trim())
  }
  const date = Date.parse(value)
  return Number.isNaN(date)
    ? undefined
    : Math.max(0, Math.ceil((date - Date.now()) / 1000))
}

function describe(error: unknown): string {
  if (error instanceof Error) {
    const cause = (error as { cause?: unknown }).cause
    return cause instanceof Error
      ? `${error.message} (${cause.message})`
      : error.message
  }
  return String(error)
}

export function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    if (signal?.aborted) {
      resolve()
      return
    }
    const timer = setTimeout(done, ms)
    signal?.addEventListener('abort', done, { once: true })
    function done() {
      clearTimeout(timer)
      signal?.removeEventListener('abort', done)
      resolve()
    }
  })
}
