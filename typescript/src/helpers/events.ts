import type {
  GetEventError,
  ListEventsError,
  ListEventsParams,
} from '../generated/operations.js'
import { EventsResource as GeneratedEventsResource } from '../generated/resources.js'
import type {
  Event,
  EventRef,
  EventWithAttachments,
} from '../generated/types.js'
import type { RequestAborted } from '../runtime/errors.js'
import { failure, type Result, success } from '../runtime/result.js'
import { type CallOptions, sleep } from '../runtime/transport.js'

/** The filters of `events.follow`: those of `list`, without `to` */
export type FollowEventsParams = Omit<
  ListEventsParams,
  'to' | 'limit' | 'continuationToken'
>

export interface FollowOptions extends CallOptions {
  /** How long to wait between polls; defaults to 5 000 ms */
  readonly pollIntervalMs?: number
}

export interface WaitOptions extends CallOptions {
  /** How long to wait in all; defaults to 60 000 ms */
  readonly waitMs?: number
  /** How long to wait between polls; defaults to 2 000 ms */
  readonly pollIntervalMs?: number
}

/**
 * `waitForAttachments` gave up after `waitMs`; `event` is the event as last
 * seen, if a poll answered in time
 */
export interface WaitTimeout {
  readonly type: 'wait-timeout'
  readonly message: string
  readonly event?: EventWithAttachments
}

export class EventsResource extends GeneratedEventsResource {
  /**
   * Yields every event from `from` on (now when left out), oldest first,
   * and then each new one as it appears, polling `list`. Each event is
   * yielded once, as first seen: get it again for a later status. A
   * failure is yielded and ends the iteration; so does aborting `signal`.
   *
   * ```ts
   * for await (const result of eg.events.follow({ gateId })) {
   *   if (!result.success) break
   *   console.log(result.data.eventTime, result.data.plate?.text)
   * }
   * ```
   *
   * Events arrive in event time order; an event that reaches the API late
   * with an earlier time than the last one seen is not yielded.
   */
  async *follow(
    params: FollowEventsParams = {},
    options: FollowOptions = {}
  ): AsyncGenerator<Result<Event, ListEventsError>, void, undefined> {
    const { pollIntervalMs = 5_000, ...callOptions } = options
    let from = params.from ?? new Date()
    // The events at exactly `from`, which the next poll lists again
    let seen = new Set<string>()

    while (!options.signal?.aborted) {
      const events = await this.listAll({ ...params, from }, callOptions)
      if (!events.success) {
        if (events.error.type !== 'aborted') {
          yield events
        }
        return
      }
      for (const event of events.data) {
        const time = event.eventTime.getTime()
        if (
          time < from.getTime() ||
          (time === from.getTime() && seen.has(event.eventId))
        ) {
          continue
        }
        if (event.eventTime.getTime() > from.getTime()) {
          from = event.eventTime
          seen = new Set()
        }
        seen.add(event.eventId)
        yield success(event, events.response)
      }
      await sleep(pollIntervalMs, options.signal)
    }
  }

  /**
   * Gets an event again until it is no longer `pending` and none of its
   * attachments is still `requested`: after `gates.open`, the snapshots of
   * the opening. The attachments' URLs are valid for 15 minutes.
   */
  async waitForAttachments(
    event: EventRef,
    options: WaitOptions = {}
  ): Promise<
    Result<EventWithAttachments, GetEventError | WaitTimeout | RequestAborted>
  > {
    const { waitMs = 60_000, pollIntervalMs = 2_000, ...callOptions } = options
    // Bounds the polls, their retries and the sleeps between them
    const deadline = AbortSignal.timeout(waitMs)
    const signal = options.signal
      ? AbortSignal.any([options.signal, deadline])
      : deadline
    let last: EventWithAttachments | undefined
    const timedOut = () =>
      failure({
        type: 'wait-timeout',
        message:
          `Event ${event.eventId} still had pending attachments after ` +
          `${waitMs} ms`,
        ...(last && { event: last }),
      } satisfies WaitTimeout)

    for (;;) {
      const result = await this.get(event, { ...callOptions, signal })
      if (!result.success) {
        return result.error.type === 'aborted' && !options.signal?.aborted
          ? timedOut()
          : result
      }
      if (isSettled(result.data)) {
        return result
      }
      last = result.data
      await sleep(pollIntervalMs, signal)
      if (options.signal?.aborted) {
        return failure({
          type: 'aborted',
          message: 'The call was aborted',
          reason: options.signal.reason,
        })
      }
      if (deadline.aborted) {
        return timedOut()
      }
    }
  }
}

function isSettled(event: EventWithAttachments): boolean {
  return (
    event.status !== 'pending' &&
    event.attachments.every((attachment) => attachment.status !== 'requested')
  )
}
