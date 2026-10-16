// Generated from the Einar Gate OpenAPI document by
// packages/aws/scripts/sdk in the Einar Gate monorepo. Do not edit:
// change the route registry or the generator and run
// `npm run public-api:lock --workspace @einargate/aws`.

import type { AnyError, UnknownProblem } from '../runtime/errors.js'
import { collectPages, type Page } from '../runtime/page.js'
import * as q from '../runtime/query.js'
import type { Result } from '../runtime/result.js'
import type {
  CallInput,
  CallOptions,
  OperationSpec,
  WriteOptions,
} from '../runtime/transport.js'
import type { UnknownValue } from '../runtime/unknown-value.js'
import * as o from './operations.js'
import * as t from './types.js'

/** What the resources need from the client */
export interface ResourceContext {
  send<T, E extends AnyError>(
    spec: OperationSpec<T>,
    input: CallInput
  ): Promise<Result<T, E>>
  /** The API key’s location, from `GET /me` unless the client was given it */
  locationId(options: CallOptions): Promise<Result<string, o.GetMeError>>
}

/** The calls that belong to no resource */
export class RootResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The calling API key.
   *
   * The API key the calling value belongs to: its roles, the subscription
   * state of its location and the configured rate limits. Every authenticated
   * API key may call it; check it when a request is answered with `forbidden`.
   *
   * - `GET /me`
   * - Roles: `IntegrationSetupReader`, `IntegrationPermissionReader`,
   *   `IntegrationEventReader`, `IntegrationPermissionManager`,
   *   `IntegrationGateOperator`
   * - Errors: those of every call (`CommonProblem`, `CallError`)
   */
  async me(options: CallOptions = {}): Promise<Result<t.Me, o.GetMeError>> {
    return this.context.send<t.Me, o.GetMeError>(o.getMeSpec, { ...options })
  }

  /**
   * This OpenAPI document.
   *
   * The OpenAPI 3.1 document of v1. No authentication needed.
   *
   * - `GET /openapi.json`
   * - No API key needed
   * - Errors: `internal`, `rate-limited`, `service-unavailable`, `CallError`
   */
  async openApiDocument(
    options: CallOptions = {}
  ): Promise<
    Result<Readonly<Record<string, unknown>>, o.GetOpenApiDocumentError>
  > {
    return this.context.send<
      Readonly<Record<string, unknown>>,
      o.GetOpenApiDocumentError
    >(o.getOpenApiDocumentSpec, { ...options })
  }
}

/** The API key’s location */
export class LocationResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The location.
   *
   * The API key’s location: its address, time zone, default plate country,
   * limits, subscription state and event retention.
   *
   * - `GET /locations/{locationId}`
   * - Roles: `IntegrationSetupReader`, `IntegrationEventReader`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async get(
    options: CallOptions = {}
  ): Promise<Result<t.Location, o.GetLocationError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.Location, o.GetLocationError>(
      o.getLocationSpec,
      { ...options, path: { locationId: location.data } }
    )
  }
}

/** The members and invitees of the API key’s location */
export class MembersResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The location’s members.
   *
   * Members and invitees, sorted by name. A permission’s owner is a member
   * whose status is `member`.
   *
   * - `GET /locations/{locationId}/members`
   * - Roles: `IntegrationPermissionReader`, `IntegrationPermissionManager`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async list(
    params: o.ListMembersParams = {},
    options: CallOptions = {}
  ): Promise<Result<Page<t.Member>, o.ListMembersError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<Page<t.Member>, o.ListMembersError>(
      o.listMembersSpec,
      {
        ...options,
        path: { locationId: location.data },
        query: {
          limit: q.integer(params.limit),
          continuationToken: q.string(params.continuationToken),
        },
      }
    )
  }

  /**
   * Every page of `list`, as one array: fetches pages of 200 items until the
   * last one. The first failure ends it.
   */
  async listAll(
    params: Omit<o.ListMembersParams, 'limit' | 'continuationToken'> = {},
    options: CallOptions = {}
  ): Promise<Result<readonly t.Member[], o.ListMembersError>> {
    return collectPages<t.Member, o.ListMembersError>((continuationToken) =>
      this.list(
        {
          ...params,
          limit: 200,
          ...(continuationToken !== undefined && { continuationToken }),
        },
        options
      )
    )
  }
}

/** The gates of the API key’s location */
export class GatesResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The location’s gates.
   *
   * Sorted by name.
   *
   * - `GET /locations/{locationId}/gates`
   * - Roles: `IntegrationSetupReader`, `IntegrationPermissionReader`,
   *   `IntegrationEventReader`, `IntegrationPermissionManager`,
   *   `IntegrationGateOperator`
   * - Errors: `invalid-request`, those of every call (`CommonProblem`,
   *   `CallError`)
   */
  async list(
    params: o.ListGatesParams = {},
    options: CallOptions = {}
  ): Promise<Result<Page<t.Gate>, o.ListGatesError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<Page<t.Gate>, o.ListGatesError>(o.listGatesSpec, {
      ...options,
      path: { locationId: location.data },
      query: {
        limit: q.integer(params.limit),
        continuationToken: q.string(params.continuationToken),
      },
    })
  }

  /**
   * Every page of `list`, as one array: fetches pages of 200 items until the
   * last one. The first failure ends it.
   */
  async listAll(
    params: Omit<o.ListGatesParams, 'limit' | 'continuationToken'> = {},
    options: CallOptions = {}
  ): Promise<Result<readonly t.Gate[], o.ListGatesError>> {
    return collectPages<t.Gate, o.ListGatesError>((continuationToken) =>
      this.list(
        {
          ...params,
          limit: 200,
          ...(continuationToken !== undefined && { continuationToken }),
        },
        options
      )
    )
  }

  /**
   * A gate.
   *
   * - `GET /locations/{locationId}/gates/{gateId}`
   * - Roles: `IntegrationSetupReader`, `IntegrationPermissionReader`,
   *   `IntegrationEventReader`, `IntegrationPermissionManager`,
   *   `IntegrationGateOperator`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async get(
    gate: t.GateRef,
    options: CallOptions = {}
  ): Promise<Result<t.Gate, o.GetGateError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.Gate, o.GetGateError>(o.getGateSpec, {
      ...options,
      path: { locationId: location.data, gateId: gate.gateId },
    })
  }

  /**
   * Open a gate.
   *
   * Sends the open command to the gate’s control camera and answers the manual
   * opening event while it is still pending: its snapshots are requested from
   * the gate’s cameras, and `GET /events/{eventId}` shows them once they
   * arrive. Requires an active subscription. No body. Send an
   * `Idempotency-Key` so that a retry does not open the gate twice.
   *
   * - `POST /locations/{locationId}/gates/{gateId}/open`
   * - Roles: `IntegrationGateOperator`
   * - Errors: `gate-not-operable`, `idempotency-key-in-flight`,
   *   `idempotency-key-reuse`, `invalid-request`, `not-found`, those of every
   *   call (`CommonProblem`, `CallError`)
   * - Idempotent: an `Idempotency-Key` is sent, so retries are safe; pass
   *   `idempotencyKey` to choose it
   */
  async open(
    gate: t.GateRef,
    options: WriteOptions = {}
  ): Promise<Result<t.Event, o.OpenGateError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.Event, o.OpenGateError>(o.openGateSpec, {
      ...options,
      path: { locationId: location.data, gateId: gate.gateId },
    })
  }
}

/** The cameras of the API key’s location */
export class CamerasResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The cameras of the location, or of one of its gates.
   *
   * Every camera registered at a gate of the location, with its connection
   * status.
   *
   * - `GET /locations/{locationId}/cameras` (`at`: `'location'`)
   * - `GET /locations/{locationId}/gates/{gateId}/cameras` (`at`: `{ gateId
   *   }`)
   * - Roles: `IntegrationSetupReader`, `IntegrationPermissionReader`,
   *   `IntegrationEventReader`, `IntegrationPermissionManager`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async list(
    params: o.ListCamerasParams = {},
    options: CallOptions = {}
  ): Promise<Result<Page<t.Camera>, o.ListCamerasError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    const at = params.at ?? 'location'
    if (at === 'location') {
      return this.context.send<Page<t.Camera>, o.ListCamerasError>(
        o.listLocationCamerasSpec,
        {
          ...options,
          path: { locationId: location.data },
          query: {
            limit: q.integer(params.limit),
            continuationToken: q.string(params.continuationToken),
          },
        }
      )
    }
    return this.context.send<Page<t.Camera>, o.ListCamerasError>(
      o.listGateCamerasSpec,
      {
        ...options,
        path: { locationId: location.data, gateId: at.gateId },
        query: {
          limit: q.integer(params.limit),
          continuationToken: q.string(params.continuationToken),
        },
      }
    )
  }

  /**
   * Every page of `list`, as one array: fetches pages of 200 items until the
   * last one. The first failure ends it.
   */
  async listAll(
    params: Omit<o.ListCamerasParams, 'limit' | 'continuationToken'> = {},
    options: CallOptions = {}
  ): Promise<Result<readonly t.Camera[], o.ListCamerasError>> {
    return collectPages<t.Camera, o.ListCamerasError>((continuationToken) =>
      this.list(
        {
          ...params,
          limit: 200,
          ...(continuationToken !== undefined && { continuationToken }),
        },
        options
      )
    )
  }

  /**
   * A camera of a gate.
   *
   * - `GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}`
   * - Roles: `IntegrationSetupReader`, `IntegrationPermissionReader`,
   *   `IntegrationEventReader`, `IntegrationPermissionManager`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async get(
    camera: t.CameraRef,
    options: CallOptions = {}
  ): Promise<Result<t.Camera, o.GetCameraError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.Camera, o.GetCameraError>(o.getCameraSpec, {
      ...options,
      path: {
        locationId: location.data,
        gateId: camera.gateId,
        cameraId: camera.cameraId,
      },
    })
  }
}

/** The permissions of the API key’s location */
export class PermissionsResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The location’s permissions.
   *
   * One item per camera: a plate permitted at a gate with two cameras is
   * listed twice. To find a plate’s permissions, filter by `licensePlate` (and
   * `licensePlateCountry`) rather than building ids.
   *
   * - `GET /locations/{locationId}/permissions`
   * - Roles: `IntegrationPermissionReader`, `IntegrationPermissionManager`
   * - Errors: `invalid-request`, those of every call (`CommonProblem`,
   *   `CallError`)
   */
  async list(
    params: o.ListPermissionsParams = {},
    options: CallOptions = {}
  ): Promise<Result<Page<t.Permission>, o.ListPermissionsError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    const at = params.at ?? 'location'
    return this.context.send<Page<t.Permission>, o.ListPermissionsError>(
      o.listPermissionsSpec,
      {
        ...options,
        path: { locationId: location.data },
        query: {
          gateId: at === 'location' ? undefined : at.gateId,
          cameraId: at === 'location' ? undefined : at.cameraId,
          ownerUserId: q.string(params.ownerUserId),
          active: q.boolean(params.active),
          licensePlate: q.string(params.licensePlate),
          licensePlateCountry: q.string(params.licensePlateCountry),
          search: q.string(params.search),
          limit: q.integer(params.limit),
          continuationToken: q.string(params.continuationToken),
        },
      }
    )
  }

  /**
   * Every page of `list`, as one array: fetches pages of 200 items until the
   * last one. The first failure ends it.
   */
  async listAll(
    params: Omit<o.ListPermissionsParams, 'limit' | 'continuationToken'> = {},
    options: CallOptions = {}
  ): Promise<Result<readonly t.Permission[], o.ListPermissionsError>> {
    return collectPages<t.Permission, o.ListPermissionsError>(
      (continuationToken) =>
        this.list(
          {
            ...params,
            limit: 200,
            ...(continuationToken !== undefined && { continuationToken }),
          },
          options
        )
    )
  }

  /**
   * Permit a plate at every camera of the location, at every camera of a gate,
   * or at one camera.
   *
   * The plate is added camera by camera. The answer is `201` when at least one
   * camera got it, listing the cameras that did not with a problem each
   * (`conflict`: it already has the plate; `limit-exceeded`: a plate limit
   * would be exceeded). When no camera got it, the answer is that problem:
   * `conflict` if every camera already has the plate, `limit-exceeded`
   * otherwise. The owner must be a member whose status is `member`
   * (`invalid-owner`). Send an `Idempotency-Key` to retry safely.
   *
   * - `POST /locations/{locationId}/permissions` (`at`: `'location'`)
   * - `POST /locations/{locationId}/gates/{gateId}/permissions` (`at`: `{
   *   gateId }`)
   * - `POST
   *   /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions`
   *   (`at`: `{ gateId, cameraId }`)
   * - Roles: `IntegrationPermissionManager`
   * - Errors: `conflict`, `idempotency-key-in-flight`,
   *   `idempotency-key-reuse`, `invalid-owner`, `invalid-request`,
   *   `limit-exceeded`, `not-found`, those of every call (`CommonProblem`,
   *   `CallError`)
   * - Idempotent: an `Idempotency-Key` is sent, so retries are safe; pass
   *   `idempotencyKey` to choose it
   */
  async create(
    params: o.CreatePermissionParams,
    options: WriteOptions = {}
  ): Promise<Result<t.CreatePermissionResult, o.CreatePermissionError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    const { at, ...body } = params
    if (at === 'location') {
      return this.context.send<
        t.CreatePermissionResult,
        o.CreatePermissionError
      >(o.createLocationPermissionSpec, {
        ...options,
        path: { locationId: location.data },
        body: t.encodeCreatePermission(body),
      })
    }
    if (at.cameraId !== undefined) {
      return this.context.send<
        t.CreatePermissionResult,
        o.CreatePermissionError
      >(o.createCameraPermissionSpec, {
        ...options,
        path: {
          locationId: location.data,
          gateId: at.gateId,
          cameraId: at.cameraId,
        },
        body: t.encodeCreatePermission(body),
      })
    }
    return this.context.send<t.CreatePermissionResult, o.CreatePermissionError>(
      o.createGatePermissionSpec,
      {
        ...options,
        path: { locationId: location.data, gateId: at.gateId },
        body: t.encodeCreatePermission(body),
      }
    )
  }

  /**
   * A permission of a camera.
   *
   * - `GET
   *   /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`
   * - Roles: `IntegrationPermissionReader`, `IntegrationPermissionManager`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async get(
    permission: t.PermissionRef,
    options: CallOptions = {}
  ): Promise<Result<t.Permission, o.GetPermissionError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.Permission, o.GetPermissionError>(
      o.getPermissionSpec,
      {
        ...options,
        path: {
          locationId: location.data,
          gateId: permission.gateId,
          cameraId: permission.cameraId,
          permissionId: permission.permissionId,
        },
      }
    )
  }

  /**
   * Replace a permission of a camera.
   *
   * Send the full representation: a field that is not given is removed.
   * Changing the plate or country changes the `permissionId`; the response
   * carries the new one. The owner cannot be changed: remove the permission
   * and create it for the new owner.
   *
   * - `PUT
   *   /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`
   * - Roles: `IntegrationPermissionManager`
   * - Errors: `conflict`, `idempotency-key-in-flight`,
   *   `idempotency-key-reuse`, `invalid-request`, `not-found`, those of every
   *   call (`CommonProblem`, `CallError`)
   * - Idempotent: an `Idempotency-Key` is sent, so retries are safe; pass
   *   `idempotencyKey` to choose it
   */
  async replace(
    permission: t.PermissionRef,
    params: o.ReplacePermissionParams,
    options: WriteOptions = {}
  ): Promise<Result<t.Permission, o.ReplacePermissionError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.Permission, o.ReplacePermissionError>(
      o.replacePermissionSpec,
      {
        ...options,
        path: {
          locationId: location.data,
          gateId: permission.gateId,
          cameraId: permission.cameraId,
          permissionId: permission.permissionId,
        },
        body: t.encodeReplacePermission(params),
      }
    )
  }

  /**
   * Remove a permission from a camera.
   *
   * - `DELETE
   *   /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}`
   * - Roles: `IntegrationPermissionManager`
   * - Errors: `idempotency-key-in-flight`, `idempotency-key-reuse`,
   *   `invalid-request`, `not-found`, those of every call (`CommonProblem`,
   *   `CallError`)
   * - Idempotent: an `Idempotency-Key` is sent, so retries are safe; pass
   *   `idempotencyKey` to choose it
   */
  async delete(
    permission: t.PermissionRef,
    options: WriteOptions = {}
  ): Promise<Result<void, o.DeletePermissionError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<void, o.DeletePermissionError>(
      o.deletePermissionSpec,
      {
        ...options,
        path: {
          locationId: location.data,
          gateId: permission.gateId,
          cameraId: permission.cameraId,
          permissionId: permission.permissionId,
        },
      }
    )
  }
}

/** The events of the API key’s location */
export class EventsResource {
  constructor(protected readonly context: ResourceContext) {}

  /**
   * The location’s gate openings.
   *
   * Oldest first, within the location’s event retention. To follow new events,
   * pass the last event time seen as `from`. The list carries no images: get
   * an event for its attachments.
   *
   * - `GET /locations/{locationId}/events`
   * - Roles: `IntegrationEventReader`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async list(
    params: o.ListEventsParams = {},
    options: CallOptions = {}
  ): Promise<Result<Page<t.Event>, o.ListEventsError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<Page<t.Event>, o.ListEventsError>(
      o.listEventsSpec,
      {
        ...options,
        path: { locationId: location.data },
        query: {
          from: q.timestamp(params.from),
          to: q.timestamp(params.to),
          gateId: q.string(params.gateId),
          cameraId: q.string(params.cameraId),
          type: q.enumValue(params.type),
          licensePlate: q.string(params.licensePlate),
          minFraudRiskPercentage: q.integer(params.minFraudRiskPercentage),
          limit: q.integer(params.limit),
          continuationToken: q.string(params.continuationToken),
        },
      }
    )
  }

  /**
   * Every page of `list`, as one array: fetches pages of 200 items until the
   * last one. The first failure ends it.
   */
  async listAll(
    params: Omit<o.ListEventsParams, 'limit' | 'continuationToken'> = {},
    options: CallOptions = {}
  ): Promise<Result<readonly t.Event[], o.ListEventsError>> {
    return collectPages<t.Event, o.ListEventsError>((continuationToken) =>
      this.list(
        {
          ...params,
          limit: 200,
          ...(continuationToken !== undefined && { continuationToken }),
        },
        options
      )
    )
  }

  /**
   * A gate opening with its images.
   *
   * The attachments’ URLs are presigned and valid for 15 minutes; get the
   * event again for fresh ones.
   *
   * - `GET /locations/{locationId}/events/{eventId}`
   * - Roles: `IntegrationEventReader`
   * - Errors: `invalid-request`, `not-found`, those of every call
   *   (`CommonProblem`, `CallError`)
   */
  async get(
    event: t.EventRef,
    options: CallOptions = {}
  ): Promise<Result<t.EventWithAttachments, o.GetEventError>> {
    const location = await this.context.locationId(options)
    if (!location.success) return location
    return this.context.send<t.EventWithAttachments, o.GetEventError>(
      o.getEventSpec,
      {
        ...options,
        path: { locationId: location.data, eventId: event.eventId },
      }
    )
  }
}
