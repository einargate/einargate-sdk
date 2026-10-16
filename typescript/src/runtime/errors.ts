/**
 * The failures a call can return (ADR-0019, ADR-0022). Every call returns a
 * result whose error is one of its route's problem types or one of the
 * errors below; `error.type` tells them apart.
 */

/** The members of every problem (RFC 9457 problem details) */
export interface ProblemFields<T extends string, S extends number> {
  /** The problem type, e.g. `not-found`: switch on it */
  readonly type: T
  readonly status: S
  readonly title: string
  /** What happened in this case */
  readonly detail?: string
  /** The request path */
  readonly instance?: string
  /** Send it to support */
  readonly requestId: string
  /** What to do about a problem of this type */
  readonly hint: string
  /** The error catalogue's page of the type */
  readonly docsUrl: string
  /** Seconds to wait, from `Retry-After`, when the response had one */
  readonly retryAfterSeconds?: number
  /** One line for logs: the type, status, detail, hint and request id */
  readonly message: string
  /** The body as sent, including members this version does not know */
  readonly body: Readonly<Record<string, unknown>>
}

/**
 * An error response that is not a problem of a type the route declares: a
 * type added after this version was released, or a body that is not a
 * problem at all (a proxy's error page). Handle it by its status.
 */
export interface UnknownProblem {
  readonly type: 'unknown-problem'
  readonly status: number
  /** The body's `type`, when it had one */
  readonly problemType?: string
  readonly title?: string
  readonly detail?: string
  readonly requestId?: string
  readonly retryAfterSeconds?: number
  readonly message: string
  readonly body: unknown
}

/** The request did not reach the API, or its response did not arrive */
export interface NetworkError {
  readonly type: 'network'
  readonly message: string
  /**
   * `false` when no connection could be made, so the request was not sent;
   * `true` when it may have reached the API, so a write may have happened
   */
  readonly requestSent: boolean
  readonly cause: unknown
}

/** No response within the timeout, for the last attempt */
export interface RequestTimeout {
  readonly type: 'timeout'
  readonly message: string
  readonly timeoutMs: number
}

/** The caller's `signal` aborted the call */
export interface RequestAborted {
  readonly type: 'aborted'
  readonly message: string
  readonly reason: unknown
}

/**
 * A success response that does not match the API's contract. It is a bug on
 * the API's side: send the request id to support.
 */
export interface UnexpectedResponse {
  readonly type: 'unexpected-response'
  readonly status: number
  readonly requestId?: string
  /** Where the body differs from the contract, e.g. `items.0.gateId` */
  readonly path: string
  readonly message: string
  readonly body: unknown
}

/** The errors every call can return besides its problem types */
export type CallError =
  | UnknownProblem
  | NetworkError
  | RequestTimeout
  | RequestAborted
  | UnexpectedResponse

/** Any error a call can return */
export interface AnyError {
  readonly type: string
  readonly message: string
}
