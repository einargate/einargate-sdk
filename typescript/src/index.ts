/**
 * The official TypeScript client of the Einar Gate API. Start with
 * `new EinarGate()`, and read AGENTS.md in this package for the model.
 */

export { DEFAULT_BASE_URL, EinarGate, type EinarGateOptions } from './client.js'
export type {
  FollowEventsParams,
  FollowOptions,
  WaitOptions,
  WaitTimeout,
} from './helpers/events.js'
export type { PermissionChanges } from './helpers/permissions.js'
export * from './generated/types.js'
export type * from './generated/operations.js'
export type {
  AnyError,
  CallError,
  NetworkError,
  ProblemFields,
  RequestAborted,
  RequestTimeout,
  UnexpectedResponse,
  UnknownProblem,
} from './runtime/errors.js'
export type { Page } from './runtime/page.js'
export {
  EinarGateError,
  type Failure,
  type ResponseInfo,
  type Result,
  type Success,
} from './runtime/result.js'
export type { CallOptions, WriteOptions } from './runtime/transport.js'
export { isUnknown, UnknownValue } from './runtime/unknown-value.js'
export { VERSION } from './version.js'
