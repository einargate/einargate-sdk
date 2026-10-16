import { describe, expectTypeOf, it } from 'vitest'
import type {
  CreatePermissionError,
  CreatePermissionResult,
  EinarGate,
  OpenGateError,
  Permission,
  Result,
} from '../src/index.js'

/** Checked by `tsc` (npm run typecheck); vitest only runs the shells */
describe('types', () => {
  it('lists exactly the errors a call can return', () => {
    expectTypeOf<OpenGateError['type']>().toEqualTypeOf<
      | 'gate-not-operable'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'invalid-request'
      | 'not-found'
      | 'forbidden'
      | 'internal'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
      | 'unknown-problem'
      | 'network'
      | 'timeout'
      | 'aborted'
      | 'unexpected-response'
    >()
    expectTypeOf<'invalid-owner'>().toMatchTypeOf<
      CreatePermissionError['type']
    >()
  })

  it('never returns an empty created list', () => {
    expectTypeOf<CreatePermissionResult['created']>().toEqualTypeOf<
      readonly [Permission, ...Permission[]]
    >()
  })

  it('makes invalid calls unrepresentable', () => {
    const check = (eg: EinarGate) => {
      // @ts-expect-error: a camera scope needs its gate
      void eg.permissions.list({ at: { cameraId: 'c1' } })
      // @ts-expect-error: a create must say where
      void eg.permissions.create({
        licensePlate: 'A1',
        ownerUserId: 'u1',
        active: true,
      })
      void eg.permissions.replace(
        { gateId: 'g', cameraId: 'c', permissionId: 'p' },
        // @ts-expect-error: a replacement must say what happens to supplementalInfo
        { licensePlate: 'A1', licensePlateCountry: 'HU', active: true }
      )
    }
    void check
  })

  it('narrows on success and on the error type', () => {
    const handle = (result: Result<Permission, CreatePermissionError>) => {
      if (result.success) {
        expectTypeOf(result.data).toEqualTypeOf<Permission>()
        return
      }
      if (result.error.type === 'limit-exceeded') {
        expectTypeOf(result.error.status).toEqualTypeOf<422>()
      }
      if (result.error.type === 'rate-limited') {
        // @ts-expect-error: the window may be one this version does not know
        const window: 'second' | 'day' = result.error.window
        void window
      }
    }
    void handle
  })
})
