import { describe, expect, it } from 'vitest'
import type { Event } from '../src/index.js'
import { MockEinarGate } from '../src/testing.js'
import { event } from './fixtures.js'

describe('events.follow', () => {
  it('yields each event once, carrying the cursor, until aborted', async () => {
    const polls: Event[][] = [
      [
        event('e1', '2026-10-01T10:00:00Z'),
        event('e2', '2026-10-01T10:00:05Z'),
      ],
      [
        event('e2', '2026-10-01T10:00:05Z'),
        event('e3', '2026-10-01T10:00:05Z'),
      ],
      [
        event('e2', '2026-10-01T10:00:05Z'),
        event('e3', '2026-10-01T10:00:05Z'),
        event('e4', '2026-10-01T10:01:00Z'),
      ],
    ]
    let poll = 0
    const mock = new MockEinarGate().on('listEvents', () => ({
      data: { items: polls[Math.min(poll++, polls.length - 1)] },
    }))
    const controller = new AbortController()
    const seen: string[] = []

    for await (const result of mock
      .client()
      .events.follow(
        { from: new Date('2026-10-01T09:00:00Z') },
        { pollIntervalMs: 1, signal: controller.signal }
      )) {
      seen.push(result.unwrap().eventId)
      if (seen.length === 4) {
        controller.abort()
      }
    }

    expect(seen).toEqual(['e1', 'e2', 'e3', 'e4'])
    expect(mock.calls.map((call) => call.query.from)).toEqual([
      '2026-10-01T09:00:00.000Z',
      '2026-10-01T10:00:05.000Z',
      '2026-10-01T10:00:05.000Z',
    ])
  })

  it('skips an event older than the cursor', async () => {
    const controller = new AbortController()
    let polls = 0
    const mock = new MockEinarGate().on('listEvents', () => {
      if (++polls === 3) {
        controller.abort()
      }
      return {
        data: {
          items: [
            event('e0', '2026-10-01T10:00:05.200Z'),
            event('e1', '2026-10-01T10:00:06Z'),
          ],
        },
      }
    })
    const seen: string[] = []

    for await (const result of mock
      .client()
      .events.follow(
        { from: new Date('2026-10-01T10:00:05.500Z') },
        { pollIntervalMs: 1, signal: controller.signal }
      )) {
      seen.push(result.unwrap().eventId)
    }

    expect(seen).toEqual(['e1'])
  })

  it('yields a failure and stops', async () => {
    const mock = new MockEinarGate().on('listEvents', () => ({
      problem: 'forbidden',
    }))
    const results = []
    for await (const result of mock
      .client()
      .events.follow({}, { pollIntervalMs: 1 })) {
      results.push(result)
    }
    expect(results).toHaveLength(1)
    expect(!results[0].success && results[0].error.type).toBe('forbidden')
  })
})

describe('events.waitForAttachments', () => {
  const pending = {
    ...event('e1', '2026-10-01T10:00:00Z'),
    type: 'ManualGateOpening' as const,
    status: 'pending' as const,
    attachments: [
      {
        fileName: 'a.jpg',
        role: 'Overview',
        mediaType: 'image/jpeg',
        status: 'requested' as const,
      },
    ],
  }

  it('gets the event until its snapshots arrive', async () => {
    let calls = 0
    const mock = new MockEinarGate().on('getEvent', () =>
      ++calls < 3
        ? { data: pending }
        : {
            data: {
              ...pending,
              status: 'finalized',
              attachments: [
                {
                  ...pending.attachments[0],
                  status: 'uploaded',
                  url: 'https://example.test/a.jpg',
                },
              ],
            },
          }
    )
    const result = await mock
      .client()
      .events.waitForAttachments(pending, { pollIntervalMs: 1 })
    expect(result.unwrap().attachments[0].url).toBe(
      'https://example.test/a.jpg'
    )
    expect(calls).toBe(3)
  })

  it('gives up after waitMs with the event as last seen', async () => {
    const mock = new MockEinarGate().on('getEvent', () => ({ data: pending }))
    const result = await mock
      .client()
      .events.waitForAttachments(pending, { waitMs: 5, pollIntervalMs: 2 })
    if (result.success || result.error.type !== 'wait-timeout') {
      expect.fail('expected wait-timeout')
    }
    expect(result.error.event?.eventId).toBe('e1')
  })

  it('stops a poll that outlasts waitMs', async () => {
    const mock = new MockEinarGate().on(
      'getEvent',
      () => new Promise(() => undefined)
    )
    const started = Date.now()
    const result = await mock
      .client({ timeoutMs: 10_000 })
      .events.waitForAttachments(pending, { waitMs: 50 })
    expect(!result.success && result.error.type).toBe('wait-timeout')
    expect(Date.now() - started).toBeLessThan(1_000)
  })
})
