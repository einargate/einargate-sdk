import type { AnyError, RequestAborted, RequestTimeout } from './errors.js'
import { failure, type Result, success } from './result.js'
import {
  type CallInput,
  type CallOptions,
  type OperationSpec,
  send,
  type TransportConfig,
} from './transport.js'

/**
 * What the resources share: the transport configuration, and the API key's
 * location, which every location path needs. The location comes from the
 * client's options or, on first use, from `GET /me`; a failed lookup is not
 * cached, so the next call tries again.
 */
export class ClientContext {
  private location: Promise<Result<string, AnyError>> | undefined

  constructor(
    readonly config: TransportConfig,
    private readonly fixedLocationId: string | undefined,
    private readonly lookUpLocation: (
      options: CallOptions
    ) => Promise<Result<string, AnyError>>
  ) {}

  send<T, E extends AnyError>(
    spec: OperationSpec<T>,
    input: CallInput
  ): Promise<Result<T, E>> {
    return send<T, E>(this.config, spec, input) as Promise<Result<T, E>>
  }

  /**
   * The lookup is shared by the calls that wait for it, so it runs without
   * any one caller's signal; each caller still stops waiting when its own
   * signal aborts.
   */
  locationId<E extends AnyError>(
    options: CallOptions
  ): Promise<Result<string, E>> {
    if (this.fixedLocationId !== undefined) {
      return Promise.resolve(
        success(this.fixedLocationId, { status: 200, replayed: false })
      )
    }
    if (!this.location) {
      const lookup = this.lookUpLocation({})
      this.location = lookup
      void lookup.then((result) => {
        if (!result.success && this.location === lookup) {
          this.location = undefined
        }
      })
    }
    return waitFor(this.location, options) as Promise<Result<string, E>>
  }
}

/**
 * The shared lookup's result, or the caller's own `aborted` or `timeout` as
 * soon as its signal aborts or its `timeoutMs` passes
 */
function waitFor<T>(
  promise: Promise<Result<T, AnyError>>,
  { signal, timeoutMs }: CallOptions
): Promise<Result<T, AnyError>> {
  if (!signal && timeoutMs === undefined) {
    return promise
  }
  const aborted = () =>
    failure({
      type: 'aborted',
      message: 'The call was aborted',
      reason: signal?.reason,
    } satisfies RequestAborted)
  if (signal?.aborted) {
    return Promise.resolve(aborted())
  }
  return new Promise((resolve) => {
    const finish = (result: Result<T, AnyError>) => {
      clearTimeout(timer)
      signal?.removeEventListener('abort', onAbort)
      resolve(result)
    }
    const onAbort = () => finish(aborted())
    const timer =
      timeoutMs === undefined
        ? undefined
        : setTimeout(
            () =>
              finish(
                failure({
                  type: 'timeout',
                  message:
                    'No answer from the Einar Gate API about the API ' +
                    `key’s location within ${timeoutMs} ms`,
                  timeoutMs,
                } satisfies RequestTimeout)
              ),
            timeoutMs
          )
    signal?.addEventListener('abort', onAbort, { once: true })
    void promise.then(finish)
  })
}
