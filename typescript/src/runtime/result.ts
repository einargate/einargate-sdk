import type { AnyError } from './errors.js'

/** What the API's response said besides its body */
export interface ResponseInfo {
  readonly status: number
  /** API Gateway's request id, for support */
  readonly requestId?: string
  /**
   * `true` when the API replayed the stored response of an earlier request
   * with the same idempotency key: the write had already happened
   */
  readonly replayed: boolean
}

export interface Success<T> {
  readonly success: true
  readonly data: T
  readonly response: ResponseInfo
  /** The data; a success never throws */
  unwrap(): T
}

export interface Failure<E extends AnyError> {
  readonly success: false
  readonly error: E
  /**
   * The `Idempotency-Key` a write was sent with. When the write may have
   * happened (a timeout, a network error after sending, a 5xx), check its
   * effect before sending it again, and send it with this key: the API
   * replays the first response if that write completed, but runs it again
   * if the API failed after running it, because it does not keep the key of
   * a failed write. After `unexpected-response` the write ran: check its
   * effect, but do not send it again.
   */
  readonly idempotencyKey?: string
  /** Throws an `EinarGateError` that carries the error */
  unwrap(): never
}

/**
 * What every call returns: check `success`, then use `data` or switch on
 * `error.type`. Nothing the API or the network does makes a call throw.
 */
export type Result<T, E extends AnyError> = Success<T> | Failure<E>

/**
 * Thrown by `unwrap()` on a failure, for code that wants to stop at the
 * first error. `error` is the same value the result carried.
 */
export class EinarGateError<E extends AnyError = AnyError> extends Error {
  readonly error: E

  constructor(error: E) {
    super(error.message)
    this.name = 'EinarGateError'
    this.error = error
  }
}

export function success<T>(data: T, response: ResponseInfo): Success<T> {
  return {
    success: true,
    data,
    response,
    unwrap: () => data,
  }
}

export function failure<E extends AnyError>(
  error: E,
  idempotencyKey?: string
): Failure<E> {
  return {
    success: false,
    error,
    ...(idempotencyKey !== undefined && { idempotencyKey }),
    unwrap: () => {
      throw new EinarGateError(error)
    },
  }
}
