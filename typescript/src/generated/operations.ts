// Generated from the Einar Gate OpenAPI document by
// packages/aws/scripts/sdk in the Einar Gate monorepo. Do not edit:
// change the route registry or the generator and run
// `npm run public-api:lock --workspace @einargate/aws`.

import * as d from '../runtime/decode.js'
import * as e from '../runtime/encode.js'
import type { CallError, UnknownProblem } from '../runtime/errors.js'
import type { Page } from '../runtime/page.js'
import type { OperationSpec } from '../runtime/transport.js'
import type { UnknownValue } from '../runtime/unknown-value.js'
import * as t from './types.js'

// #region Operations

export const getMeSpec: OperationSpec<t.Me> = {
  id: 'getMe',
  method: 'GET',
  path: '/me',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: t.decodeMe,
  encode: (value) => t.encodeMe(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const getOpenApiDocumentSpec: OperationSpec<
  Readonly<Record<string, unknown>>
> = {
  id: 'getOpenApiDocument',
  method: 'GET',
  path: '/openapi.json',
  status: 200,
  authenticated: false,
  idempotent: false,
  decode: d.jsonObject,
  encode: (value) => value,
  problems: {
    internal: t.decodeInternalProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
  },
}

export const getLocationSpec: OperationSpec<t.Location> = {
  id: 'getLocation',
  method: 'GET',
  path: '/locations/{locationId}',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: t.decodeLocation,
  encode: (value) => t.encodeLocation(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const listMembersSpec: OperationSpec<Page<t.Member>> = {
  id: 'listMembers',
  method: 'GET',
  path: '/locations/{locationId}/members',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: (v: unknown, p: string) => t.decodePage(v, p, t.decodeMember),
  encode: (value) => t.encodePage(value, (item) => t.encodeMember(item)),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const listGatesSpec: OperationSpec<Page<t.Gate>> = {
  id: 'listGates',
  method: 'GET',
  path: '/locations/{locationId}/gates',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: (v: unknown, p: string) => t.decodePage(v, p, t.decodeGate),
  encode: (value) => t.encodePage(value, (item) => t.encodeGate(item)),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const getGateSpec: OperationSpec<t.Gate> = {
  id: 'getGate',
  method: 'GET',
  path: '/locations/{locationId}/gates/{gateId}',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: t.decodeGate,
  encode: (value) => t.encodeGate(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const openGateSpec: OperationSpec<t.Event> = {
  id: 'openGate',
  method: 'POST',
  path: '/locations/{locationId}/gates/{gateId}/open',
  status: 202,
  authenticated: true,
  idempotent: true,
  decode: t.decodeEvent,
  encode: (value) => t.encodeEvent(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    'gate-not-operable': t.decodeGateNotOperableProblem,
    'idempotency-key-in-flight': t.decodeIdempotencyKeyInFlightProblem,
    'idempotency-key-reuse': t.decodeIdempotencyKeyReuseProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const listLocationCamerasSpec: OperationSpec<Page<t.Camera>> = {
  id: 'listLocationCameras',
  method: 'GET',
  path: '/locations/{locationId}/cameras',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: (v: unknown, p: string) => t.decodePage(v, p, t.decodeCamera),
  encode: (value) => t.encodePage(value, (item) => t.encodeCamera(item)),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const listGateCamerasSpec: OperationSpec<Page<t.Camera>> = {
  id: 'listGateCameras',
  method: 'GET',
  path: '/locations/{locationId}/gates/{gateId}/cameras',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: (v: unknown, p: string) => t.decodePage(v, p, t.decodeCamera),
  encode: (value) => t.encodePage(value, (item) => t.encodeCamera(item)),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const getCameraSpec: OperationSpec<t.Camera> = {
  id: 'getCamera',
  method: 'GET',
  path: '/locations/{locationId}/gates/{gateId}/cameras/{cameraId}',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: t.decodeCamera,
  encode: (value) => t.encodeCamera(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const listPermissionsSpec: OperationSpec<Page<t.Permission>> = {
  id: 'listPermissions',
  method: 'GET',
  path: '/locations/{locationId}/permissions',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: (v: unknown, p: string) => t.decodePage(v, p, t.decodePermission),
  encode: (value) => t.encodePage(value, (item) => t.encodePermission(item)),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const createLocationPermissionSpec: OperationSpec<t.CreatePermissionResult> =
  {
    id: 'createLocationPermission',
    method: 'POST',
    path: '/locations/{locationId}/permissions',
    status: 201,
    authenticated: true,
    idempotent: true,
    decode: t.decodeCreatePermissionResult,
    encode: (value) => t.encodeCreatePermissionResult(value),
    problems: {
      conflict: t.decodeConflictProblem,
      forbidden: t.decodeForbiddenProblem,
      'idempotency-key-in-flight': t.decodeIdempotencyKeyInFlightProblem,
      'idempotency-key-reuse': t.decodeIdempotencyKeyReuseProblem,
      internal: t.decodeInternalProblem,
      'invalid-owner': t.decodeInvalidOwnerProblem,
      'invalid-request': t.decodeInvalidRequestProblem,
      'limit-exceeded': t.decodeLimitExceededProblem,
      'not-found': t.decodeNotFoundProblem,
      provisioning: t.decodeProvisioningProblem,
      'rate-limited': t.decodeRateLimitedProblem,
      'service-unavailable': t.decodeServiceUnavailableProblem,
      unauthorized: t.decodeUnauthorizedProblem,
    },
  }

export const createGatePermissionSpec: OperationSpec<t.CreatePermissionResult> =
  {
    id: 'createGatePermission',
    method: 'POST',
    path: '/locations/{locationId}/gates/{gateId}/permissions',
    status: 201,
    authenticated: true,
    idempotent: true,
    decode: t.decodeCreatePermissionResult,
    encode: (value) => t.encodeCreatePermissionResult(value),
    problems: {
      conflict: t.decodeConflictProblem,
      forbidden: t.decodeForbiddenProblem,
      'idempotency-key-in-flight': t.decodeIdempotencyKeyInFlightProblem,
      'idempotency-key-reuse': t.decodeIdempotencyKeyReuseProblem,
      internal: t.decodeInternalProblem,
      'invalid-owner': t.decodeInvalidOwnerProblem,
      'invalid-request': t.decodeInvalidRequestProblem,
      'limit-exceeded': t.decodeLimitExceededProblem,
      'not-found': t.decodeNotFoundProblem,
      provisioning: t.decodeProvisioningProblem,
      'rate-limited': t.decodeRateLimitedProblem,
      'service-unavailable': t.decodeServiceUnavailableProblem,
      unauthorized: t.decodeUnauthorizedProblem,
    },
  }

export const createCameraPermissionSpec: OperationSpec<t.CreatePermissionResult> =
  {
    id: 'createCameraPermission',
    method: 'POST',
    path: '/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions',
    status: 201,
    authenticated: true,
    idempotent: true,
    decode: t.decodeCreatePermissionResult,
    encode: (value) => t.encodeCreatePermissionResult(value),
    problems: {
      conflict: t.decodeConflictProblem,
      forbidden: t.decodeForbiddenProblem,
      'idempotency-key-in-flight': t.decodeIdempotencyKeyInFlightProblem,
      'idempotency-key-reuse': t.decodeIdempotencyKeyReuseProblem,
      internal: t.decodeInternalProblem,
      'invalid-owner': t.decodeInvalidOwnerProblem,
      'invalid-request': t.decodeInvalidRequestProblem,
      'limit-exceeded': t.decodeLimitExceededProblem,
      'not-found': t.decodeNotFoundProblem,
      provisioning: t.decodeProvisioningProblem,
      'rate-limited': t.decodeRateLimitedProblem,
      'service-unavailable': t.decodeServiceUnavailableProblem,
      unauthorized: t.decodeUnauthorizedProblem,
    },
  }

export const getPermissionSpec: OperationSpec<t.Permission> = {
  id: 'getPermission',
  method: 'GET',
  path: '/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: t.decodePermission,
  encode: (value) => t.encodePermission(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const replacePermissionSpec: OperationSpec<t.Permission> = {
  id: 'replacePermission',
  method: 'PUT',
  path: '/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}',
  status: 200,
  authenticated: true,
  idempotent: true,
  decode: t.decodePermission,
  encode: (value) => t.encodePermission(value),
  problems: {
    conflict: t.decodeConflictProblem,
    forbidden: t.decodeForbiddenProblem,
    'idempotency-key-in-flight': t.decodeIdempotencyKeyInFlightProblem,
    'idempotency-key-reuse': t.decodeIdempotencyKeyReuseProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const deletePermissionSpec: OperationSpec<void> = {
  id: 'deletePermission',
  method: 'DELETE',
  path: '/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}',
  status: 204,
  authenticated: true,
  idempotent: true,
  problems: {
    forbidden: t.decodeForbiddenProblem,
    'idempotency-key-in-flight': t.decodeIdempotencyKeyInFlightProblem,
    'idempotency-key-reuse': t.decodeIdempotencyKeyReuseProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const listEventsSpec: OperationSpec<Page<t.Event>> = {
  id: 'listEvents',
  method: 'GET',
  path: '/locations/{locationId}/events',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: (v: unknown, p: string) => t.decodePage(v, p, t.decodeEvent),
  encode: (value) => t.encodePage(value, (item) => t.encodeEvent(item)),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

export const getEventSpec: OperationSpec<t.EventWithAttachments> = {
  id: 'getEvent',
  method: 'GET',
  path: '/locations/{locationId}/events/{eventId}',
  status: 200,
  authenticated: true,
  idempotent: false,
  decode: t.decodeEventWithAttachments,
  encode: (value) => t.encodeEventWithAttachments(value),
  problems: {
    forbidden: t.decodeForbiddenProblem,
    internal: t.decodeInternalProblem,
    'invalid-request': t.decodeInvalidRequestProblem,
    'not-found': t.decodeNotFoundProblem,
    provisioning: t.decodeProvisioningProblem,
    'rate-limited': t.decodeRateLimitedProblem,
    'service-unavailable': t.decodeServiceUnavailableProblem,
    unauthorized: t.decodeUnauthorizedProblem,
  },
}

/** Every operation, by its OpenAPI operation id */
export const OPERATIONS = {
  getMe: getMeSpec,
  getOpenApiDocument: getOpenApiDocumentSpec,
  getLocation: getLocationSpec,
  listMembers: listMembersSpec,
  listGates: listGatesSpec,
  getGate: getGateSpec,
  openGate: openGateSpec,
  listLocationCameras: listLocationCamerasSpec,
  listGateCameras: listGateCamerasSpec,
  getCamera: getCameraSpec,
  listPermissions: listPermissionsSpec,
  createLocationPermission: createLocationPermissionSpec,
  createGatePermission: createGatePermissionSpec,
  createCameraPermission: createCameraPermissionSpec,
  getPermission: getPermissionSpec,
  replacePermission: replacePermissionSpec,
  deletePermission: deletePermissionSpec,
  listEvents: listEventsSpec,
  getEvent: getEventSpec,
} as const

export type OperationId = keyof typeof OPERATIONS

/** What each operation answers: its success data and problem types */
export interface OperationTypes {
  getMe: {
    data: t.Me
    problems:
      | 'forbidden'
      | 'internal'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  getOpenApiDocument: {
    data: Readonly<Record<string, unknown>>
    problems: 'internal' | 'rate-limited' | 'service-unavailable'
  }
  getLocation: {
    data: t.Location
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  listMembers: {
    data: Page<t.Member>
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  listGates: {
    data: Page<t.Gate>
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  getGate: {
    data: t.Gate
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  openGate: {
    data: t.Event
    problems:
      | 'forbidden'
      | 'gate-not-operable'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  listLocationCameras: {
    data: Page<t.Camera>
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  listGateCameras: {
    data: Page<t.Camera>
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  getCamera: {
    data: t.Camera
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  listPermissions: {
    data: Page<t.Permission>
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  createLocationPermission: {
    data: t.CreatePermissionResult
    problems:
      | 'conflict'
      | 'forbidden'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'internal'
      | 'invalid-owner'
      | 'invalid-request'
      | 'limit-exceeded'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  createGatePermission: {
    data: t.CreatePermissionResult
    problems:
      | 'conflict'
      | 'forbidden'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'internal'
      | 'invalid-owner'
      | 'invalid-request'
      | 'limit-exceeded'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  createCameraPermission: {
    data: t.CreatePermissionResult
    problems:
      | 'conflict'
      | 'forbidden'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'internal'
      | 'invalid-owner'
      | 'invalid-request'
      | 'limit-exceeded'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  getPermission: {
    data: t.Permission
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  replacePermission: {
    data: t.Permission
    problems:
      | 'conflict'
      | 'forbidden'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  deletePermission: {
    data: void
    problems:
      | 'forbidden'
      | 'idempotency-key-in-flight'
      | 'idempotency-key-reuse'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  listEvents: {
    data: Page<t.Event>
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
  getEvent: {
    data: t.EventWithAttachments
    problems:
      | 'forbidden'
      | 'internal'
      | 'invalid-request'
      | 'not-found'
      | 'provisioning'
      | 'rate-limited'
      | 'service-unavailable'
      | 'unauthorized'
  }
}

// #endregion Operations
// #region Errors

/** The problem types every authenticated call can return, besides its own */
export type CommonProblem =
  | t.ForbiddenProblem
  | t.InternalProblem
  | t.ProvisioningProblem
  | t.RateLimitedProblem
  | t.ServiceUnavailableProblem
  | t.UnauthorizedProblem

/** The errors `me` can return */
export type GetMeError = CommonProblem | CallError

/** The errors `openApiDocument` can return */
export type GetOpenApiDocumentError =
  | t.InternalProblem
  | t.RateLimitedProblem
  | t.ServiceUnavailableProblem
  | CallError

/** The errors `location.get` can return */
export type GetLocationError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `members.list` can return */
export type ListMembersError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `gates.list` can return */
export type ListGatesError = t.InvalidRequestProblem | CommonProblem | CallError

/** The errors `gates.get` can return */
export type GetGateError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `gates.open` can return */
export type OpenGateError =
  | t.GateNotOperableProblem
  | t.IdempotencyKeyInFlightProblem
  | t.IdempotencyKeyReuseProblem
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `cameras.list` can return */
export type ListCamerasError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `cameras.get` can return */
export type GetCameraError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `permissions.list` can return */
export type ListPermissionsError =
  | t.InvalidRequestProblem
  | CommonProblem
  | CallError

/** The errors `permissions.create` can return */
export type CreatePermissionError =
  | t.ConflictProblem
  | t.IdempotencyKeyInFlightProblem
  | t.IdempotencyKeyReuseProblem
  | t.InvalidOwnerProblem
  | t.InvalidRequestProblem
  | t.LimitExceededProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `permissions.get` can return */
export type GetPermissionError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `permissions.replace` can return */
export type ReplacePermissionError =
  | t.ConflictProblem
  | t.IdempotencyKeyInFlightProblem
  | t.IdempotencyKeyReuseProblem
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `permissions.delete` can return */
export type DeletePermissionError =
  | t.IdempotencyKeyInFlightProblem
  | t.IdempotencyKeyReuseProblem
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `events.list` can return */
export type ListEventsError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

/** The errors `events.get` can return */
export type GetEventError =
  | t.InvalidRequestProblem
  | t.NotFoundProblem
  | CommonProblem
  | CallError

// #endregion Errors
// #region Parameters

/** The parameters of `members.list` */
export interface ListMembersParams {
  /** Items per page, 1 to 200 */
  readonly limit?: number
  /** The `continuationToken` of the previous page, to get the next one */
  readonly continuationToken?: string
}

/** The parameters of `gates.list` */
export interface ListGatesParams {
  /** Items per page, 1 to 200 */
  readonly limit?: number
  /** The `continuationToken` of the previous page, to get the next one */
  readonly continuationToken?: string
}

/** The parameters of `cameras.list` */
export interface ListCamerasParams {
  /**
   * Where: `'location'`: every camera of the location; `{ gateId }`: every
   * camera of a gate. A `Gate` or a `Camera` can be passed as it is. The
   * location when left out.
   */
  readonly at?: ListCamerasScope
  /** Items per page, 1 to 200 */
  readonly limit?: number
  /** The `continuationToken` of the previous page, to get the next one */
  readonly continuationToken?: string
}

/**
 * Where: `'location'`: every camera of the location; `{ gateId }`: every
 * camera of a gate. A `Gate` or a `Camera` can be passed as it is.
 */
export type ListCamerasScope = 'location' | { readonly gateId: string }

/** The parameters of `permissions.list` */
export interface ListPermissionsParams {
  /**
   * Where: `'location'`: every camera of the location; `{ gateId }`: every
   * camera of a gate; `{ gateId, cameraId }`: one camera. A `Gate` or a
   * `Camera` can be passed as it is. The location when left out.
   */
  readonly at?: ListPermissionsScope
  readonly ownerUserId?: string
  readonly active?: boolean
  /**
   * Exact match on the plate, which is normalized as on create (`abc-123`
   * finds `ABC123`)
   */
  readonly licensePlate?: string
  /**
   * Exact match on the country. A plate without a country is found by
   * `licensePlate` alone: its `licensePlateCountry` is empty.
   */
  readonly licensePlateCountry?: string
  /** Matches part of the plate or of the supplemental info */
  readonly search?: string
  /** Items per page, 1 to 200 */
  readonly limit?: number
  /** The `continuationToken` of the previous page, to get the next one */
  readonly continuationToken?: string
}

/**
 * Where: `'location'`: every camera of the location; `{ gateId }`: every
 * camera of a gate; `{ gateId, cameraId }`: one camera. A `Gate` or a
 * `Camera` can be passed as it is.
 */
export type ListPermissionsScope =
  | 'location'
  | { readonly gateId: string; readonly cameraId?: string }

/** The parameters of `permissions.create` */
export type CreatePermissionParams = t.CreatePermission & {
  /** Where: `'location'`: every camera of the location; `{ gateId }`: every camera of a gate; `{ gateId, cameraId }`: one camera. A `Gate` or a `Camera` can be passed as it is. */
  readonly at: CreatePermissionScope
}

/**
 * Where: `'location'`: every camera of the location; `{ gateId }`: every
 * camera of a gate; `{ gateId, cameraId }`: one camera. A `Gate` or a
 * `Camera` can be passed as it is.
 */
export type CreatePermissionScope =
  | 'location'
  | { readonly gateId: string; readonly cameraId?: string }

/** The parameters of `permissions.replace` */
export type ReplacePermissionParams = t.ReplacePermission

/** The parameters of `events.list` */
export interface ListEventsParams {
  /** Events at or after this time; ISO 8601, offsets allowed */
  readonly from?: Date
  /** Events at or before this time; ISO 8601, offsets allowed */
  readonly to?: Date
  readonly gateId?: string
  readonly cameraId?: string
  readonly type?: t.EventType
  /** Exact match on the recognized plate */
  readonly licensePlate?: string
  readonly minFraudRiskPercentage?: number
  /** Items per page, 1 to 200 */
  readonly limit?: number
  /** The `continuationToken` of the previous page, to get the next one */
  readonly continuationToken?: string
}

// #endregion Parameters
