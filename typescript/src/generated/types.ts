// Generated from the Einar Gate OpenAPI document by
// packages/aws/scripts/sdk in the Einar Gate monorepo. Do not edit:
// change the route registry or the generator and run
// `npm run public-api:lock --workspace @einargate/aws`.

import * as d from '../runtime/decode.js'
import * as e from '../runtime/encode.js'
import type { ProblemFields, UnknownProblem } from '../runtime/errors.js'
import type { Page } from '../runtime/page.js'
import { problemFields, type ProblemType } from '../runtime/problem.js'
import type { ProblemInfo } from '../runtime/transport.js'
import { unknownProblem } from '../runtime/transport.js'
import { UnknownValue } from '../runtime/unknown-value.js'

// #region Enums

/**
 * A response field of this type is `ApiKeyRole | UnknownValue`: the API may
 * add values within v1.
 */
export type ApiKeyRole =
  | 'IntegrationSetupReader'
  | 'IntegrationPermissionReader'
  | 'IntegrationEventReader'
  | 'IntegrationPermissionManager'
  | 'IntegrationGateOperator'

export const API_KEY_ROLE_VALUES = [
  'IntegrationSetupReader',
  'IntegrationPermissionReader',
  'IntegrationEventReader',
  'IntegrationPermissionManager',
  'IntegrationGateOperator',
] as const satisfies readonly ApiKeyRole[]

/**
 * A response field of this type is `CameraConnectionStatus | UnknownValue`:
 * the API may add values within v1.
 */
export type CameraConnectionStatus = 'online' | 'offline'

export const CAMERA_CONNECTION_STATUS_VALUES = [
  'online',
  'offline',
] as const satisfies readonly CameraConnectionStatus[]

/**
 * The camera’s registration at the gate
 *
 * A response field of this type is `CameraStatus | UnknownValue`: the API
 * may add values within v1.
 */
export type CameraStatus = 'initializing' | 'active' | 'deleting'

export const CAMERA_STATUS_VALUES = [
  'initializing',
  'active',
  'deleting',
] as const satisfies readonly CameraStatus[]

/**
 * A manual opening’s snapshot: requested from the camera, uploaded, or
 * failed
 *
 * A response field of this type is `EventAttachmentStatus | UnknownValue`:
 * the API may add values within v1.
 */
export type EventAttachmentStatus = 'requested' | 'uploaded' | 'error'

export const EVENT_ATTACHMENT_STATUS_VALUES = [
  'requested',
  'uploaded',
  'error',
] as const satisfies readonly EventAttachmentStatus[]

/**
 * A gate opening is `pending` until its data and images arrive
 *
 * A response field of this type is `EventStatus | UnknownValue`: the API may
 * add values within v1.
 */
export type EventStatus = 'pending' | 'finalized' | 'canceled' | 'failed'

export const EVENT_STATUS_VALUES = [
  'pending',
  'finalized',
  'canceled',
  'failed',
] as const satisfies readonly EventStatus[]

/**
 * A response field of this type is `EventType | UnknownValue`: the API may
 * add values within v1.
 */
export type EventType = 'AutomaticGateOpening' | 'ManualGateOpening'

export const EVENT_TYPE_VALUES = [
  'AutomaticGateOpening',
  'ManualGateOpening',
] as const satisfies readonly EventType[]

/**
 * A response field of this type is `MemberRole | UnknownValue`: the API may
 * add values within v1.
 */
export type MemberRole = 'LocationOwner' | 'LocationAdmin' | 'LocationUser'

export const MEMBER_ROLE_VALUES = [
  'LocationOwner',
  'LocationAdmin',
  'LocationUser',
] as const satisfies readonly MemberRole[]

/**
 * Only a `member` can own permissions; the others are invitations in
 * progress or a membership being removed
 *
 * A response field of this type is `MemberStatus | UnknownValue`: the API
 * may add values within v1.
 */
export type MemberStatus =
  | 'invited'
  | 'invitation_declined'
  | 'acknowledged'
  | 'member'
  | 'deleting'

export const MEMBER_STATUS_VALUES = [
  'invited',
  'invitation_declined',
  'acknowledged',
  'member',
  'deleting',
] as const satisfies readonly MemberStatus[]

/**
 * A response field of this type is `RateLimitWindow | UnknownValue`: the API
 * may add values within v1.
 */
export type RateLimitWindow = 'second' | 'day'

export const RATE_LIMIT_WINDOW_VALUES = [
  'second',
  'day',
] as const satisfies readonly RateLimitWindow[]

// #endregion Enums
// #region Models

/** A camera registered at a gate */
export interface Camera {
  readonly cameraId: string
  readonly locationId: string
  readonly gateId: string
  readonly name: string
  /** The camera’s registration at the gate */
  readonly status: CameraStatus | UnknownValue
  readonly connection: CameraConnection
  readonly createdAt: Date
  readonly updatedAt: Date
}

export interface CameraConnection {
  readonly status: CameraConnectionStatus | UnknownValue
  /** When an offline camera was last connected, if known */
  readonly disconnectedAt?: Date
}

export interface CreatePermission {
  /** As typed; whitespace and dashes are removed */
  readonly licensePlate: string
  /**
   * `null` for a plate without a country; when left out, the location’s
   * `defaultLicensePlateCountry`
   */
  readonly licensePlateCountry?: string | null
  /**
   * A member of the location whose status is `member`; the plate counts
   * against their limit
   */
  readonly ownerUserId: string
  readonly active: boolean
  readonly supplementalInfo?: string
}

/**
 * The permission as added to each camera that got it, and the cameras that
 * did not
 */
export interface CreatePermissionResult {
  /** Never empty: when no camera got it, the answer is a problem */
  readonly created: readonly [Permission, ...Permission[]]
  readonly failed: readonly FailedCamera[]
}

/** A gate opening */
export interface Event {
  readonly eventId: string
  readonly type: EventType | UnknownValue
  /** A gate opening is `pending` until its data and images arrive */
  readonly status: EventStatus | UnknownValue
  readonly locationId: string
  readonly gateId: string
  /** The camera that recognized the plate; not set on manual openings */
  readonly cameraId?: string
  readonly eventTime: Date
  readonly initiator?: EventInitiator
  /** The recognized plate; automatic openings */
  readonly plate?: EventPlate
  /** The recognized vehicle; automatic openings */
  readonly vehicle?: EventVehicle
  readonly direction?: string
  readonly speed?: number
  readonly fraudRiskPercentage?: number
  /** The permission that let the vehicle in */
  readonly permission?: EventPermission
  readonly createdAt: Date
  readonly updatedAt: Date
}

export interface EventAttachment {
  readonly fileName: string
  /** E.g. `Overview` or `Plate` */
  readonly role: string
  readonly mediaType: string
  /**
   * A manual opening’s snapshot: requested from the camera, uploaded, or
   * failed
   */
  readonly status?: EventAttachmentStatus | UnknownValue
  /** A presigned URL, valid for 15 minutes; set once the file is uploaded */
  readonly url?: string
}

/** Manual openings only */
export type EventInitiator =
  | EventInitiatorUser
  | EventInitiatorApiKey
  | UnknownEventInitiator

/**
 * A variant of `EventInitiator` that this version does not know. `raw` is
 * the object as sent.
 */
export interface UnknownEventInitiator {
  readonly type: UnknownValue
  readonly raw: Readonly<Record<string, unknown>>
}

export interface EventInitiatorApiKey {
  readonly type: 'api-key'
  readonly apiKeyId: string
  readonly displayName: string
}

export interface EventInitiatorUser {
  readonly type: 'user'
  readonly userId: string
  readonly displayName: string
}

/** The permission that let the vehicle in */
export interface EventPermission {
  readonly permissionId: string
  readonly cameraId: string
  readonly ownerUserId: string
}

/** The recognized plate; automatic openings */
export interface EventPlate {
  readonly text: string
  readonly country: string
  readonly confidence: number
}

/** The recognized vehicle; automatic openings */
export interface EventVehicle {
  readonly category: string
  readonly make: string
  readonly model: string
  readonly color: string
}

/** A gate opening with its images */
export interface EventWithAttachments extends Event {
  readonly attachments: readonly EventAttachment[]
}

/**
 * A camera that did not get the permission: `conflict` when it already has
 * one for the plate and country, `limit-exceeded` when a plate limit of the
 * location or the owner would be exceeded
 */
export interface FailedCamera {
  readonly cameraId: string
  readonly error: ConflictProblem | LimitExceededProblem | UnknownProblem
}

export interface Gate {
  readonly gateId: string
  readonly locationId: string
  readonly name: string
  /** Whether any member of the location may open it in the app */
  readonly manualOperation: boolean
  /** The camera that opens the gate; a gate without one cannot be opened */
  readonly gateControlCameraId?: string
  readonly createdAt: Date
  readonly updatedAt: Date
}

export interface InvalidRequestIssue {
  readonly path: string
  readonly message: string
}

export interface Location {
  readonly locationId: string
  readonly name: string
  readonly address: string
  /** IANA time zone, e.g. `Europe/Budapest` */
  readonly timezone?: string
  /** The country a permission gets when it is created without one */
  readonly defaultLicensePlateCountry?: string
  readonly limits: LocationLimits
  /** Opening gates requires an active subscription */
  readonly subscriptionActive: boolean
  /** How many days events are kept; not set when they are kept indefinitely */
  readonly eventRetentionDays?: number
  readonly createdAt: Date
  readonly updatedAt: Date
}

/**
 * The location’s limits. A limit that is not set is the default of the
 * location’s plan.
 */
export interface LocationLimits {
  readonly maxUsers?: number
  readonly maxGates?: number
  readonly maxCamerasPerGate?: number
  readonly maxPlatesPerUser?: number
  readonly maxPlatesInPlan?: number
  readonly maxEventsWithAttachments?: number
}

/** The calling API key */
export interface Me {
  readonly apiKeyId: string
  readonly name: string
  readonly locationId: string
  /** The roles the API key holds at its location */
  readonly roles: readonly (ApiKeyRole | UnknownValue)[]
  /**
   * Whether the location's subscription is active. Opening gates requires an
   * active subscription.
   */
  readonly subscriptionActive: boolean
  readonly rateLimit: RateLimit
  readonly valueRetiresAt?: Date
}

/** A member or an invitee of the location */
export interface Member {
  /**
   * Set once the user has an account; a permission’s owner must be a member
   * whose status is `member`
   */
  readonly userId?: string
  readonly email: string
  readonly givenName?: string
  readonly familyName?: string
  readonly role: MemberRole | UnknownValue
  /**
   * Only a `member` can own permissions; the others are invitations in
   * progress or a membership being removed
   */
  readonly status: MemberStatus | UnknownValue
}

/**
 * A plate’s permission on one camera. The owner’s private name and comment
 * are never exposed.
 */
export interface Permission {
  /**
   * **Opaque: store it as it is and URL-encode it in paths.** Find a
   * permission by plate with the `licensePlate` filter instead of building an
   * id.
   */
  readonly permissionId: string
  readonly locationId: string
  readonly gateId: string
  readonly cameraId: string
  /** Normalized */
  readonly licensePlate: string
  /** Upper-case; `null` when the plate has no country */
  readonly licensePlateCountry: string | null
  readonly ownerUserId: string
  readonly active: boolean
  readonly supplementalInfo?: string
  readonly numberOfOpenings: number
  readonly createdAt: Date
  readonly updatedAt: Date
}

/**
 * The configured limits, shared by all API keys of the location. Live
 * counters are not available.
 */
export interface RateLimit {
  /** Sustained requests per second for the location */
  readonly requestsPerSecond: number
  /** Requests the location may send at once before throttling */
  readonly burst: number
  /** Daily quota of the location; it resets at the start of each day */
  readonly requestsPerDay: number
}

/**
 * The full representation of the permission’s fields an API key manages; a
 * field that is not given is removed. The owner cannot be changed, and the
 * owner’s private name and comment are kept.
 */
export interface ReplacePermission {
  /**
   * As typed; changing it changes the `permissionId`, which the response
   * returns
   */
  readonly licensePlate: string
  /** `null` for a plate without a country */
  readonly licensePlateCountry: string | null
  readonly active: boolean
  /** `null` removes it */
  readonly supplementalInfo: string | null
}

// #endregion Models
// #region References

/** A gate of the location: a `Gate`, or its id */
export interface GateRef {
  readonly gateId: string
}

/** A camera of a gate: a `Camera`, or its gate and camera ids */
export interface CameraRef {
  readonly gateId: string
  readonly cameraId: string
}

/**
 * A permission of a camera: a `Permission`, or its gate, camera and
 * permission ids. The permission id is opaque: use it as returned.
 */
export interface PermissionRef {
  readonly gateId: string
  readonly cameraId: string
  readonly permissionId: string
}

/** An event of the location: an `Event`, or its id */
export interface EventRef {
  readonly eventId: string
}

// #endregion References
// #region Problems

/**
 * Conflict: The entity already exists (for a permission: the camera already
 * has the plate and country) or was changed at the same time. Read it again
 * before deciding; a concurrent change is safe to retry.
 */
export interface ConflictProblem extends ProblemFields<'conflict', 409> {}

const CONFLICT_PROBLEM: ProblemType<'conflict', 409> = {
  slug: 'conflict',
  status: 409,
  title: 'Conflict',
  hint: 'The entity already exists (for a permission: the camera already has the plate and country) or was changed at the same time. Read it again before deciding; a concurrent change is safe to retry.',
  docsUrl: 'https://developers.einargate.com/errors/conflict',
}

export function decodeConflictProblem(
  body: d.JsonObject,
  info: ProblemInfo
): ConflictProblem {
  return problemFields(body, CONFLICT_PROBLEM, info)
}

/**
 * Forbidden: The API key lacks a role for this action, the path names
 * another location, or the action needs an active subscription. `GET /me`
 * shows the key’s roles, location and subscription state; a location Owner
 * or Admin changes its roles in the app.
 */
export interface ForbiddenProblem extends ProblemFields<'forbidden', 403> {}

const FORBIDDEN_PROBLEM: ProblemType<'forbidden', 403> = {
  slug: 'forbidden',
  status: 403,
  title: 'Forbidden',
  hint: 'The API key lacks a role for this action, the path names another location, or the action needs an active subscription. `GET /me` shows the key’s roles, location and subscription state; a location Owner or Admin changes its roles in the app.',
  docsUrl: 'https://developers.einargate.com/errors/forbidden',
}

export function decodeForbiddenProblem(
  body: d.JsonObject,
  info: ProblemInfo
): ForbiddenProblem {
  return problemFields(body, FORBIDDEN_PROBLEM, info)
}

/**
 * Gate not operable: The gate cannot be opened now: it has no control
 * camera, the camera is offline, or the gate is not set up for control.
 * Check its `gateControlCameraId` and that camera’s `connection.status`.
 */
export interface GateNotOperableProblem
  extends ProblemFields<'gate-not-operable', 422> {}

const GATE_NOT_OPERABLE_PROBLEM: ProblemType<'gate-not-operable', 422> = {
  slug: 'gate-not-operable',
  status: 422,
  title: 'Gate not operable',
  hint: 'The gate cannot be opened now: it has no control camera, the camera is offline, or the gate is not set up for control. Check its `gateControlCameraId` and that camera’s `connection.status`.',
  docsUrl: 'https://developers.einargate.com/errors/gate-not-operable',
}

export function decodeGateNotOperableProblem(
  body: d.JsonObject,
  info: ProblemInfo
): GateNotOperableProblem {
  return problemFields(body, GATE_NOT_OPERABLE_PROBLEM, info)
}

/**
 * Idempotency key in flight: A request with the same `Idempotency-Key` is
 * still running: wait a moment and retry with the same key.
 */
export interface IdempotencyKeyInFlightProblem
  extends ProblemFields<'idempotency-key-in-flight', 409> {}

const IDEMPOTENCY_KEY_IN_FLIGHT_PROBLEM: ProblemType<
  'idempotency-key-in-flight',
  409
> = {
  slug: 'idempotency-key-in-flight',
  status: 409,
  title: 'Idempotency key in flight',
  hint: 'A request with the same `Idempotency-Key` is still running: wait a moment and retry with the same key.',
  docsUrl: 'https://developers.einargate.com/errors/idempotency-key-in-flight',
}

export function decodeIdempotencyKeyInFlightProblem(
  body: d.JsonObject,
  info: ProblemInfo
): IdempotencyKeyInFlightProblem {
  return problemFields(body, IDEMPOTENCY_KEY_IN_FLIGHT_PROBLEM, info)
}

/**
 * Idempotency key reused: The `Idempotency-Key` was used for a different
 * request in the last 24 hours: send a new request with a new key.
 */
export interface IdempotencyKeyReuseProblem
  extends ProblemFields<'idempotency-key-reuse', 422> {}

const IDEMPOTENCY_KEY_REUSE_PROBLEM: ProblemType<'idempotency-key-reuse', 422> =
  {
    slug: 'idempotency-key-reuse',
    status: 422,
    title: 'Idempotency key reused',
    hint: 'The `Idempotency-Key` was used for a different request in the last 24 hours: send a new request with a new key.',
    docsUrl: 'https://developers.einargate.com/errors/idempotency-key-reuse',
  }

export function decodeIdempotencyKeyReuseProblem(
  body: d.JsonObject,
  info: ProblemInfo
): IdempotencyKeyReuseProblem {
  return problemFields(body, IDEMPOTENCY_KEY_REUSE_PROBLEM, info)
}

/**
 * Internal error: An unexpected error on our side. Retry later, and send the
 * `requestId` to support if it persists. Before retrying a gate opening,
 * check the events: the gate may have opened.
 */
export interface InternalProblem extends ProblemFields<'internal', 500> {}

const INTERNAL_PROBLEM: ProblemType<'internal', 500> = {
  slug: 'internal',
  status: 500,
  title: 'Internal error',
  hint: 'An unexpected error on our side. Retry later, and send the `requestId` to support if it persists. Before retrying a gate opening, check the events: the gate may have opened.',
  docsUrl: 'https://developers.einargate.com/errors/internal',
}

export function decodeInternalProblem(
  body: d.JsonObject,
  info: ProblemInfo
): InternalProblem {
  return problemFields(body, INTERNAL_PROBLEM, info)
}

/**
 * Invalid owner: Set `ownerUserId` to the `userId` of a member whose status
 * is `member` (`GET /locations/{locationId}/members`).
 */
export interface InvalidOwnerProblem
  extends ProblemFields<'invalid-owner', 422> {}

const INVALID_OWNER_PROBLEM: ProblemType<'invalid-owner', 422> = {
  slug: 'invalid-owner',
  status: 422,
  title: 'Invalid owner',
  hint: 'Set `ownerUserId` to the `userId` of a member whose status is `member` (`GET /locations/{locationId}/members`).',
  docsUrl: 'https://developers.einargate.com/errors/invalid-owner',
}

export function decodeInvalidOwnerProblem(
  body: d.JsonObject,
  info: ProblemInfo
): InvalidOwnerProblem {
  return problemFields(body, INVALID_OWNER_PROBLEM, info)
}

/**
 * Invalid request: Fix the members that `errors[]` lists and send the
 * request again. A body member’s path is bare (`licensePlate`); query and
 * path parameters are prefixed `query.` and `path.`.
 */
export interface InvalidRequestProblem
  extends ProblemFields<'invalid-request', 400> {
  readonly errors: readonly InvalidRequestIssue[]
}

const INVALID_REQUEST_PROBLEM: ProblemType<'invalid-request', 400> = {
  slug: 'invalid-request',
  status: 400,
  title: 'Invalid request',
  hint: 'Fix the members that `errors[]` lists and send the request again. A body member’s path is bare (`licensePlate`); query and path parameters are prefixed `query.` and `path.`.',
  docsUrl: 'https://developers.einargate.com/errors/invalid-request',
}

export function decodeInvalidRequestProblem(
  body: d.JsonObject,
  info: ProblemInfo
): InvalidRequestProblem {
  return {
    ...problemFields(body, INVALID_REQUEST_PROBLEM, info),
    errors: d.required(body, 'errors', '', (v: unknown, p: string) =>
      d.array(v, p, decodeInvalidRequestIssue)
    ),
  }
}

/**
 * Limit exceeded: A limit of the location’s plan or of the owner would be
 * exceeded; the location’s `limits` show them. Remove permissions first, or
 * ask the location Owner to change the plan.
 */
export interface LimitExceededProblem
  extends ProblemFields<'limit-exceeded', 422> {}

const LIMIT_EXCEEDED_PROBLEM: ProblemType<'limit-exceeded', 422> = {
  slug: 'limit-exceeded',
  status: 422,
  title: 'Limit exceeded',
  hint: 'A limit of the location’s plan or of the owner would be exceeded; the location’s `limits` show them. Remove permissions first, or ask the location Owner to change the plan.',
  docsUrl: 'https://developers.einargate.com/errors/limit-exceeded',
}

export function decodeLimitExceededProblem(
  body: d.JsonObject,
  info: ProblemInfo
): LimitExceededProblem {
  return problemFields(body, LIMIT_EXCEEDED_PROBLEM, info)
}

/**
 * Not found: Use ids exactly as the API returned them, under the API key’s
 * own location, and URL-encode permission ids. Never build an id.
 */
export interface NotFoundProblem extends ProblemFields<'not-found', 404> {}

const NOT_FOUND_PROBLEM: ProblemType<'not-found', 404> = {
  slug: 'not-found',
  status: 404,
  title: 'Not found',
  hint: 'Use ids exactly as the API returned them, under the API key’s own location, and URL-encode permission ids. Never build an id.',
  docsUrl: 'https://developers.einargate.com/errors/not-found',
}

export function decodeNotFoundProblem(
  body: d.JsonObject,
  info: ProblemInfo
): NotFoundProblem {
  return problemFields(body, NOT_FOUND_PROBLEM, info)
}

/**
 * Provisioning in progress: The location’s first API key was created moments
 * ago: retry after `Retry-After` seconds.
 */
export interface ProvisioningProblem
  extends ProblemFields<'provisioning', 503> {}

const PROVISIONING_PROBLEM: ProblemType<'provisioning', 503> = {
  slug: 'provisioning',
  status: 503,
  title: 'Provisioning in progress',
  hint: 'The location’s first API key was created moments ago: retry after `Retry-After` seconds.',
  docsUrl: 'https://developers.einargate.com/errors/provisioning',
}

export function decodeProvisioningProblem(
  body: d.JsonObject,
  info: ProblemInfo
): ProvisioningProblem {
  return problemFields(body, PROVISIONING_PROBLEM, info)
}

/**
 * Rate limit exceeded: Wait `Retry-After` seconds when `window` is `second`,
 * or until the next day when it is `day`. Every API key of the location
 * shares the limits that `GET /me` shows.
 */
export interface RateLimitedProblem extends ProblemFields<'rate-limited', 429> {
  readonly window: RateLimitWindow | UnknownValue
}

const RATE_LIMITED_PROBLEM: ProblemType<'rate-limited', 429> = {
  slug: 'rate-limited',
  status: 429,
  title: 'Rate limit exceeded',
  hint: 'Wait `Retry-After` seconds when `window` is `second`, or until the next day when it is `day`. Every API key of the location shares the limits that `GET /me` shows.',
  docsUrl: 'https://developers.einargate.com/errors/rate-limited',
}

export function decodeRateLimitedProblem(
  body: d.JsonObject,
  info: ProblemInfo
): RateLimitedProblem {
  return {
    ...problemFields(body, RATE_LIMITED_PROBLEM, info),
    window: d.required(body, 'window', '', (v: unknown, p: string) =>
      d.enumValue(v, p, RATE_LIMIT_WINDOW_VALUES)
    ),
  }
}

/**
 * Service unavailable: A dependency was briefly unavailable: send the same
 * request again after a short wait, with the same `Idempotency-Key` for a
 * write.
 */
export interface ServiceUnavailableProblem
  extends ProblemFields<'service-unavailable', 503> {}

const SERVICE_UNAVAILABLE_PROBLEM: ProblemType<'service-unavailable', 503> = {
  slug: 'service-unavailable',
  status: 503,
  title: 'Service unavailable',
  hint: 'A dependency was briefly unavailable: send the same request again after a short wait, with the same `Idempotency-Key` for a write.',
  docsUrl: 'https://developers.einargate.com/errors/service-unavailable',
}

export function decodeServiceUnavailableProblem(
  body: d.JsonObject,
  info: ProblemInfo
): ServiceUnavailableProblem {
  return problemFields(body, SERVICE_UNAVAILABLE_PROBLEM, info)
}

/**
 * Unauthorized: Send a working API key value as `Authorization: Bearer
 * egk_…`. A value stops working when it is revoked, or retired after a
 * rotation: get the current one from whoever manages the API key in the
 * Einar Gate app.
 */
export interface UnauthorizedProblem
  extends ProblemFields<'unauthorized', 401> {}

const UNAUTHORIZED_PROBLEM: ProblemType<'unauthorized', 401> = {
  slug: 'unauthorized',
  status: 401,
  title: 'Unauthorized',
  hint: 'Send a working API key value as `Authorization: Bearer egk_…`. A value stops working when it is revoked, or retired after a rotation: get the current one from whoever manages the API key in the Einar Gate app.',
  docsUrl: 'https://developers.einargate.com/errors/unauthorized',
}

export function decodeUnauthorizedProblem(
  body: d.JsonObject,
  info: ProblemInfo
): UnauthorizedProblem {
  return problemFields(body, UNAUTHORIZED_PROBLEM, info)
}

/** A problem of a type this version knows */
export type Problem =
  | ConflictProblem
  | ForbiddenProblem
  | GateNotOperableProblem
  | IdempotencyKeyInFlightProblem
  | IdempotencyKeyReuseProblem
  | InternalProblem
  | InvalidOwnerProblem
  | InvalidRequestProblem
  | LimitExceededProblem
  | NotFoundProblem
  | ProvisioningProblem
  | RateLimitedProblem
  | ServiceUnavailableProblem
  | UnauthorizedProblem

/** Every problem type: its status, title, hint and catalogue page */
export const PROBLEM_TYPES = {
  conflict: CONFLICT_PROBLEM,
  forbidden: FORBIDDEN_PROBLEM,
  'gate-not-operable': GATE_NOT_OPERABLE_PROBLEM,
  'idempotency-key-in-flight': IDEMPOTENCY_KEY_IN_FLIGHT_PROBLEM,
  'idempotency-key-reuse': IDEMPOTENCY_KEY_REUSE_PROBLEM,
  internal: INTERNAL_PROBLEM,
  'invalid-owner': INVALID_OWNER_PROBLEM,
  'invalid-request': INVALID_REQUEST_PROBLEM,
  'limit-exceeded': LIMIT_EXCEEDED_PROBLEM,
  'not-found': NOT_FOUND_PROBLEM,
  provisioning: PROVISIONING_PROBLEM,
  'rate-limited': RATE_LIMITED_PROBLEM,
  'service-unavailable': SERVICE_UNAVAILABLE_PROBLEM,
  unauthorized: UNAUTHORIZED_PROBLEM,
} as const

/**
 * Decodes a problem embedded in a body (a failed camera of a permission
 * create). A type not listed is an `UnknownProblem`.
 */
export function decodeEmbeddedProblem(
  value: unknown,
  path: string,
  slugs: readonly string[]
): Problem | UnknownProblem {
  const body = d.object(value, path)
  const type = body.type
  if (
    typeof type === 'string' &&
    type.startsWith('https://developers.einargate.com/errors/')
  ) {
    const slug = type.slice(40)
    if (slugs.includes(slug)) {
      try {
        switch (slug) {
          case 'conflict':
            return decodeConflictProblem(body, {})
          case 'forbidden':
            return decodeForbiddenProblem(body, {})
          case 'gate-not-operable':
            return decodeGateNotOperableProblem(body, {})
          case 'idempotency-key-in-flight':
            return decodeIdempotencyKeyInFlightProblem(body, {})
          case 'idempotency-key-reuse':
            return decodeIdempotencyKeyReuseProblem(body, {})
          case 'internal':
            return decodeInternalProblem(body, {})
          case 'invalid-owner':
            return decodeInvalidOwnerProblem(body, {})
          case 'invalid-request':
            return decodeInvalidRequestProblem(body, {})
          case 'limit-exceeded':
            return decodeLimitExceededProblem(body, {})
          case 'not-found':
            return decodeNotFoundProblem(body, {})
          case 'provisioning':
            return decodeProvisioningProblem(body, {})
          case 'rate-limited':
            return decodeRateLimitedProblem(body, {})
          case 'service-unavailable':
            return decodeServiceUnavailableProblem(body, {})
          case 'unauthorized':
            return decodeUnauthorizedProblem(body, {})
        }
      } catch (error) {
        if (!(error instanceof d.DecodeError)) throw error
      }
    }
  }
  const status = typeof body.status === 'number' ? body.status : 0
  return unknownProblem(status, body)
}

// #endregion Problems
// #region Decoders

export function decodeCamera(value: unknown, path: string): Camera {
  const o = d.object(value, path)
  return d.compact({
    cameraId: d.required(o, 'cameraId', path, d.string),
    locationId: d.required(o, 'locationId', path, d.string),
    gateId: d.required(o, 'gateId', path, d.string),
    name: d.required(o, 'name', path, d.string),
    status: d.required(o, 'status', path, (v: unknown, p: string) =>
      d.enumValue(v, p, CAMERA_STATUS_VALUES)
    ),
    connection: d.required(o, 'connection', path, decodeCameraConnection),
    createdAt: d.required(o, 'createdAt', path, d.timestamp),
    updatedAt: d.required(o, 'updatedAt', path, d.timestamp),
  })
}

export function decodeCameraConnection(
  value: unknown,
  path: string
): CameraConnection {
  const o = d.object(value, path)
  return d.compact({
    status: d.required(o, 'status', path, (v: unknown, p: string) =>
      d.enumValue(v, p, CAMERA_CONNECTION_STATUS_VALUES)
    ),
    disconnectedAt: d.optional(o, 'disconnectedAt', path, d.timestamp),
  })
}

export function decodeCreatePermissionResult(
  value: unknown,
  path: string
): CreatePermissionResult {
  const o = d.object(value, path)
  return d.compact({
    created: d.required(o, 'created', path, (v: unknown, p: string) =>
      d.nonEmptyArray(v, p, decodePermission)
    ),
    failed: d.required(o, 'failed', path, (v: unknown, p: string) =>
      d.array(v, p, decodeFailedCamera)
    ),
  })
}

export function decodeEvent(value: unknown, path: string): Event {
  const o = d.object(value, path)
  return d.compact({
    eventId: d.required(o, 'eventId', path, d.string),
    type: d.required(o, 'type', path, (v: unknown, p: string) =>
      d.enumValue(v, p, EVENT_TYPE_VALUES)
    ),
    status: d.required(o, 'status', path, (v: unknown, p: string) =>
      d.enumValue(v, p, EVENT_STATUS_VALUES)
    ),
    locationId: d.required(o, 'locationId', path, d.string),
    gateId: d.required(o, 'gateId', path, d.string),
    cameraId: d.optional(o, 'cameraId', path, d.string),
    eventTime: d.required(o, 'eventTime', path, d.timestamp),
    initiator: d.optional(o, 'initiator', path, decodeEventInitiator),
    plate: d.optional(o, 'plate', path, decodeEventPlate),
    vehicle: d.optional(o, 'vehicle', path, decodeEventVehicle),
    direction: d.optional(o, 'direction', path, d.string),
    speed: d.optional(o, 'speed', path, d.number),
    fraudRiskPercentage: d.optional(o, 'fraudRiskPercentage', path, d.number),
    permission: d.optional(o, 'permission', path, decodeEventPermission),
    createdAt: d.required(o, 'createdAt', path, d.timestamp),
    updatedAt: d.required(o, 'updatedAt', path, d.timestamp),
  })
}

export function decodeEventAttachment(
  value: unknown,
  path: string
): EventAttachment {
  const o = d.object(value, path)
  return d.compact({
    fileName: d.required(o, 'fileName', path, d.string),
    role: d.required(o, 'role', path, d.string),
    mediaType: d.required(o, 'mediaType', path, d.string),
    status: d.optional(o, 'status', path, (v: unknown, p: string) =>
      d.enumValue(v, p, EVENT_ATTACHMENT_STATUS_VALUES)
    ),
    url: d.optional(o, 'url', path, d.string),
  })
}

export function decodeEventInitiator(
  value: unknown,
  path: string
): EventInitiator {
  const o = d.object(value, path)
  switch (o['type']) {
    case 'user':
      return decodeEventInitiatorUser(o, path)
    case 'api-key':
      return decodeEventInitiatorApiKey(o, path)
    default:
      return {
        type: new UnknownValue(d.required(o, 'type', path, d.string)),
        raw: o,
      }
  }
}

export function decodeEventInitiatorApiKey(
  value: unknown,
  path: string
): EventInitiatorApiKey {
  const o = d.object(value, path)
  return d.compact({
    type: d.required(o, 'type', path, (v: unknown, p: string) =>
      d.literal(v, p, 'api-key')
    ),
    apiKeyId: d.required(o, 'apiKeyId', path, d.string),
    displayName: d.required(o, 'displayName', path, d.string),
  })
}

export function decodeEventInitiatorUser(
  value: unknown,
  path: string
): EventInitiatorUser {
  const o = d.object(value, path)
  return d.compact({
    type: d.required(o, 'type', path, (v: unknown, p: string) =>
      d.literal(v, p, 'user')
    ),
    userId: d.required(o, 'userId', path, d.string),
    displayName: d.required(o, 'displayName', path, d.string),
  })
}

export function decodeEventPermission(
  value: unknown,
  path: string
): EventPermission {
  const o = d.object(value, path)
  return d.compact({
    permissionId: d.required(o, 'permissionId', path, d.string),
    cameraId: d.required(o, 'cameraId', path, d.string),
    ownerUserId: d.required(o, 'ownerUserId', path, d.string),
  })
}

export function decodeEventPlate(value: unknown, path: string): EventPlate {
  const o = d.object(value, path)
  return d.compact({
    text: d.required(o, 'text', path, d.string),
    country: d.required(o, 'country', path, d.string),
    confidence: d.required(o, 'confidence', path, d.number),
  })
}

export function decodeEventVehicle(value: unknown, path: string): EventVehicle {
  const o = d.object(value, path)
  return d.compact({
    category: d.required(o, 'category', path, d.string),
    make: d.required(o, 'make', path, d.string),
    model: d.required(o, 'model', path, d.string),
    color: d.required(o, 'color', path, d.string),
  })
}

export function decodeEventWithAttachments(
  value: unknown,
  path: string
): EventWithAttachments {
  const o = d.object(value, path)
  return d.compact({
    eventId: d.required(o, 'eventId', path, d.string),
    type: d.required(o, 'type', path, (v: unknown, p: string) =>
      d.enumValue(v, p, EVENT_TYPE_VALUES)
    ),
    status: d.required(o, 'status', path, (v: unknown, p: string) =>
      d.enumValue(v, p, EVENT_STATUS_VALUES)
    ),
    locationId: d.required(o, 'locationId', path, d.string),
    gateId: d.required(o, 'gateId', path, d.string),
    cameraId: d.optional(o, 'cameraId', path, d.string),
    eventTime: d.required(o, 'eventTime', path, d.timestamp),
    initiator: d.optional(o, 'initiator', path, decodeEventInitiator),
    plate: d.optional(o, 'plate', path, decodeEventPlate),
    vehicle: d.optional(o, 'vehicle', path, decodeEventVehicle),
    direction: d.optional(o, 'direction', path, d.string),
    speed: d.optional(o, 'speed', path, d.number),
    fraudRiskPercentage: d.optional(o, 'fraudRiskPercentage', path, d.number),
    permission: d.optional(o, 'permission', path, decodeEventPermission),
    createdAt: d.required(o, 'createdAt', path, d.timestamp),
    updatedAt: d.required(o, 'updatedAt', path, d.timestamp),
    attachments: d.required(o, 'attachments', path, (v: unknown, p: string) =>
      d.array(v, p, decodeEventAttachment)
    ),
  })
}

export function decodeFailedCamera(value: unknown, path: string): FailedCamera {
  const o = d.object(value, path)
  return d.compact({
    cameraId: d.required(o, 'cameraId', path, d.string),
    error: d.required(
      o,
      'error',
      path,
      (v: unknown, p: string) =>
        decodeEmbeddedProblem(v, p, ['conflict', 'limit-exceeded']) as
          | ConflictProblem
          | LimitExceededProblem
          | UnknownProblem
    ),
  })
}

export function decodeGate(value: unknown, path: string): Gate {
  const o = d.object(value, path)
  return d.compact({
    gateId: d.required(o, 'gateId', path, d.string),
    locationId: d.required(o, 'locationId', path, d.string),
    name: d.required(o, 'name', path, d.string),
    manualOperation: d.required(o, 'manualOperation', path, d.boolean),
    gateControlCameraId: d.optional(o, 'gateControlCameraId', path, d.string),
    createdAt: d.required(o, 'createdAt', path, d.timestamp),
    updatedAt: d.required(o, 'updatedAt', path, d.timestamp),
  })
}

export function decodeInvalidRequestIssue(
  value: unknown,
  path: string
): InvalidRequestIssue {
  const o = d.object(value, path)
  return d.compact({
    path: d.required(o, 'path', path, d.string),
    message: d.required(o, 'message', path, d.string),
  })
}

export function decodeLocation(value: unknown, path: string): Location {
  const o = d.object(value, path)
  return d.compact({
    locationId: d.required(o, 'locationId', path, d.string),
    name: d.required(o, 'name', path, d.string),
    address: d.required(o, 'address', path, d.string),
    timezone: d.optional(o, 'timezone', path, d.string),
    defaultLicensePlateCountry: d.optional(
      o,
      'defaultLicensePlateCountry',
      path,
      d.string
    ),
    limits: d.required(o, 'limits', path, decodeLocationLimits),
    subscriptionActive: d.required(o, 'subscriptionActive', path, d.boolean),
    eventRetentionDays: d.optional(o, 'eventRetentionDays', path, d.integer),
    createdAt: d.required(o, 'createdAt', path, d.timestamp),
    updatedAt: d.required(o, 'updatedAt', path, d.timestamp),
  })
}

export function decodeLocationLimits(
  value: unknown,
  path: string
): LocationLimits {
  const o = d.object(value, path)
  return d.compact({
    maxUsers: d.optional(o, 'maxUsers', path, d.integer),
    maxGates: d.optional(o, 'maxGates', path, d.integer),
    maxCamerasPerGate: d.optional(o, 'maxCamerasPerGate', path, d.integer),
    maxPlatesPerUser: d.optional(o, 'maxPlatesPerUser', path, d.integer),
    maxPlatesInPlan: d.optional(o, 'maxPlatesInPlan', path, d.integer),
    maxEventsWithAttachments: d.optional(
      o,
      'maxEventsWithAttachments',
      path,
      d.integer
    ),
  })
}

export function decodeMe(value: unknown, path: string): Me {
  const o = d.object(value, path)
  return d.compact({
    apiKeyId: d.required(o, 'apiKeyId', path, d.string),
    name: d.required(o, 'name', path, d.string),
    locationId: d.required(o, 'locationId', path, d.string),
    roles: d.required(o, 'roles', path, (v: unknown, p: string) =>
      d.array(v, p, (v: unknown, p: string) =>
        d.enumValue(v, p, API_KEY_ROLE_VALUES)
      )
    ),
    subscriptionActive: d.required(o, 'subscriptionActive', path, d.boolean),
    rateLimit: d.required(o, 'rateLimit', path, decodeRateLimit),
    valueRetiresAt: d.optional(o, 'valueRetiresAt', path, d.timestamp),
  })
}

export function decodeMember(value: unknown, path: string): Member {
  const o = d.object(value, path)
  return d.compact({
    userId: d.optional(o, 'userId', path, d.string),
    email: d.required(o, 'email', path, d.string),
    givenName: d.optional(o, 'givenName', path, d.string),
    familyName: d.optional(o, 'familyName', path, d.string),
    role: d.required(o, 'role', path, (v: unknown, p: string) =>
      d.enumValue(v, p, MEMBER_ROLE_VALUES)
    ),
    status: d.required(o, 'status', path, (v: unknown, p: string) =>
      d.enumValue(v, p, MEMBER_STATUS_VALUES)
    ),
  })
}

export function decodePermission(value: unknown, path: string): Permission {
  const o = d.object(value, path)
  return d.compact({
    permissionId: d.required(o, 'permissionId', path, d.string),
    locationId: d.required(o, 'locationId', path, d.string),
    gateId: d.required(o, 'gateId', path, d.string),
    cameraId: d.required(o, 'cameraId', path, d.string),
    licensePlate: d.required(o, 'licensePlate', path, d.string),
    licensePlateCountry: d.required(
      o,
      'licensePlateCountry',
      path,
      (v: unknown, p: string) => d.nullIfEmpty(d.string(v, p))
    ),
    ownerUserId: d.required(o, 'ownerUserId', path, d.string),
    active: d.required(o, 'active', path, d.boolean),
    supplementalInfo: d.optional(o, 'supplementalInfo', path, d.string),
    numberOfOpenings: d.required(o, 'numberOfOpenings', path, d.integer),
    createdAt: d.required(o, 'createdAt', path, d.timestamp),
    updatedAt: d.required(o, 'updatedAt', path, d.timestamp),
  })
}

export function decodeRateLimit(value: unknown, path: string): RateLimit {
  const o = d.object(value, path)
  return d.compact({
    requestsPerSecond: d.required(o, 'requestsPerSecond', path, d.integer),
    burst: d.required(o, 'burst', path, d.integer),
    requestsPerDay: d.required(o, 'requestsPerDay', path, d.integer),
  })
}

export function decodePage<T>(
  value: unknown,
  path: string,
  item: d.Decoder<T>
): Page<T> {
  const o = d.object(value, path)
  return d.compact({
    items: d.required(o, 'items', path, (v, p) => d.array(v, p, item)),
    continuationToken: d.optional(o, 'continuationToken', path, d.string),
  })
}

// #endregion Decoders
// #region Encoders

export function encodeCamera(value: Camera): Record<string, unknown> {
  return e.compact({
    cameraId: value.cameraId,
    locationId: value.locationId,
    gateId: value.gateId,
    name: value.name,
    status: e.enumValue(value.status),
    connection: encodeCameraConnection(value.connection),
    createdAt: e.timestamp(value.createdAt),
    updatedAt: e.timestamp(value.updatedAt),
  })
}

export function encodeCameraConnection(
  value: CameraConnection
): Record<string, unknown> {
  return e.compact({
    status: e.enumValue(value.status),
    disconnectedAt:
      value.disconnectedAt === undefined
        ? undefined
        : e.timestamp(value.disconnectedAt),
  })
}

export function encodeCreatePermission(
  value: CreatePermission
): Record<string, unknown> {
  return e.compact({
    licensePlate: value.licensePlate,
    licensePlateCountry:
      value.licensePlateCountry === undefined
        ? undefined
        : e.emptyIfNull(value.licensePlateCountry),
    ownerUserId: value.ownerUserId,
    active: value.active,
    supplementalInfo: value.supplementalInfo,
  })
}

export function encodeCreatePermissionResult(
  value: CreatePermissionResult
): Record<string, unknown> {
  return e.compact({
    created: value.created.map((item) => encodePermission(item)),
    failed: value.failed.map((item) => encodeFailedCamera(item)),
  })
}

export function encodeEvent(value: Event): Record<string, unknown> {
  return e.compact({
    eventId: value.eventId,
    type: e.enumValue(value.type),
    status: e.enumValue(value.status),
    locationId: value.locationId,
    gateId: value.gateId,
    cameraId: value.cameraId,
    eventTime: e.timestamp(value.eventTime),
    initiator:
      value.initiator === undefined
        ? undefined
        : encodeEventInitiator(value.initiator),
    plate:
      value.plate === undefined ? undefined : encodeEventPlate(value.plate),
    vehicle:
      value.vehicle === undefined
        ? undefined
        : encodeEventVehicle(value.vehicle),
    direction: value.direction,
    speed: value.speed,
    fraudRiskPercentage: value.fraudRiskPercentage,
    permission:
      value.permission === undefined
        ? undefined
        : encodeEventPermission(value.permission),
    createdAt: e.timestamp(value.createdAt),
    updatedAt: e.timestamp(value.updatedAt),
  })
}

export function encodeEventAttachment(
  value: EventAttachment
): Record<string, unknown> {
  return e.compact({
    fileName: value.fileName,
    role: value.role,
    mediaType: value.mediaType,
    status: value.status === undefined ? undefined : e.enumValue(value.status),
    url: value.url,
  })
}

export function encodeEventInitiator(
  value: EventInitiator
): Record<string, unknown> {
  switch (value.type) {
    case 'user':
      return encodeEventInitiatorUser(value as EventInitiatorUser)
    case 'api-key':
      return encodeEventInitiatorApiKey(value as EventInitiatorApiKey)
    default:
      return { ...(value as UnknownEventInitiator).raw }
  }
}

export function encodeEventInitiatorApiKey(
  value: EventInitiatorApiKey
): Record<string, unknown> {
  return e.compact({
    type: value.type,
    apiKeyId: value.apiKeyId,
    displayName: value.displayName,
  })
}

export function encodeEventInitiatorUser(
  value: EventInitiatorUser
): Record<string, unknown> {
  return e.compact({
    type: value.type,
    userId: value.userId,
    displayName: value.displayName,
  })
}

export function encodeEventPermission(
  value: EventPermission
): Record<string, unknown> {
  return e.compact({
    permissionId: value.permissionId,
    cameraId: value.cameraId,
    ownerUserId: value.ownerUserId,
  })
}

export function encodeEventPlate(value: EventPlate): Record<string, unknown> {
  return e.compact({
    text: value.text,
    country: value.country,
    confidence: value.confidence,
  })
}

export function encodeEventVehicle(
  value: EventVehicle
): Record<string, unknown> {
  return e.compact({
    category: value.category,
    make: value.make,
    model: value.model,
    color: value.color,
  })
}

export function encodeEventWithAttachments(
  value: EventWithAttachments
): Record<string, unknown> {
  return e.compact({
    eventId: value.eventId,
    type: e.enumValue(value.type),
    status: e.enumValue(value.status),
    locationId: value.locationId,
    gateId: value.gateId,
    cameraId: value.cameraId,
    eventTime: e.timestamp(value.eventTime),
    initiator:
      value.initiator === undefined
        ? undefined
        : encodeEventInitiator(value.initiator),
    plate:
      value.plate === undefined ? undefined : encodeEventPlate(value.plate),
    vehicle:
      value.vehicle === undefined
        ? undefined
        : encodeEventVehicle(value.vehicle),
    direction: value.direction,
    speed: value.speed,
    fraudRiskPercentage: value.fraudRiskPercentage,
    permission:
      value.permission === undefined
        ? undefined
        : encodeEventPermission(value.permission),
    createdAt: e.timestamp(value.createdAt),
    updatedAt: e.timestamp(value.updatedAt),
    attachments: value.attachments.map((item) => encodeEventAttachment(item)),
  })
}

export function encodeFailedCamera(
  value: FailedCamera
): Record<string, unknown> {
  return e.compact({
    cameraId: value.cameraId,
    error: value.error.body,
  })
}

export function encodeGate(value: Gate): Record<string, unknown> {
  return e.compact({
    gateId: value.gateId,
    locationId: value.locationId,
    name: value.name,
    manualOperation: value.manualOperation,
    gateControlCameraId: value.gateControlCameraId,
    createdAt: e.timestamp(value.createdAt),
    updatedAt: e.timestamp(value.updatedAt),
  })
}

export function encodeInvalidRequestIssue(
  value: InvalidRequestIssue
): Record<string, unknown> {
  return e.compact({
    path: value.path,
    message: value.message,
  })
}

export function encodeLocation(value: Location): Record<string, unknown> {
  return e.compact({
    locationId: value.locationId,
    name: value.name,
    address: value.address,
    timezone: value.timezone,
    defaultLicensePlateCountry: value.defaultLicensePlateCountry,
    limits: encodeLocationLimits(value.limits),
    subscriptionActive: value.subscriptionActive,
    eventRetentionDays: value.eventRetentionDays,
    createdAt: e.timestamp(value.createdAt),
    updatedAt: e.timestamp(value.updatedAt),
  })
}

export function encodeLocationLimits(
  value: LocationLimits
): Record<string, unknown> {
  return e.compact({
    maxUsers: value.maxUsers,
    maxGates: value.maxGates,
    maxCamerasPerGate: value.maxCamerasPerGate,
    maxPlatesPerUser: value.maxPlatesPerUser,
    maxPlatesInPlan: value.maxPlatesInPlan,
    maxEventsWithAttachments: value.maxEventsWithAttachments,
  })
}

export function encodeMe(value: Me): Record<string, unknown> {
  return e.compact({
    apiKeyId: value.apiKeyId,
    name: value.name,
    locationId: value.locationId,
    roles: value.roles.map((item) => e.enumValue(item)),
    subscriptionActive: value.subscriptionActive,
    rateLimit: encodeRateLimit(value.rateLimit),
    valueRetiresAt:
      value.valueRetiresAt === undefined
        ? undefined
        : e.timestamp(value.valueRetiresAt),
  })
}

export function encodeMember(value: Member): Record<string, unknown> {
  return e.compact({
    userId: value.userId,
    email: value.email,
    givenName: value.givenName,
    familyName: value.familyName,
    role: e.enumValue(value.role),
    status: e.enumValue(value.status),
  })
}

export function encodePermission(value: Permission): Record<string, unknown> {
  return e.compact({
    permissionId: value.permissionId,
    locationId: value.locationId,
    gateId: value.gateId,
    cameraId: value.cameraId,
    licensePlate: value.licensePlate,
    licensePlateCountry: e.emptyIfNull(value.licensePlateCountry),
    ownerUserId: value.ownerUserId,
    active: value.active,
    supplementalInfo: value.supplementalInfo,
    numberOfOpenings: value.numberOfOpenings,
    createdAt: e.timestamp(value.createdAt),
    updatedAt: e.timestamp(value.updatedAt),
  })
}

export function encodeRateLimit(value: RateLimit): Record<string, unknown> {
  return e.compact({
    requestsPerSecond: value.requestsPerSecond,
    burst: value.burst,
    requestsPerDay: value.requestsPerDay,
  })
}

export function encodeReplacePermission(
  value: ReplacePermission
): Record<string, unknown> {
  return e.compact({
    licensePlate: value.licensePlate,
    licensePlateCountry: e.emptyIfNull(value.licensePlateCountry),
    active: value.active,
    supplementalInfo:
      value.supplementalInfo === null ? undefined : value.supplementalInfo,
  })
}

export function encodePage<T>(
  value: Page<T>,
  item: (value: T) => unknown
): Record<string, unknown> {
  return e.compact({
    items: value.items.map(item),
    continuationToken: value.continuationToken,
  })
}

// #endregion Encoders
