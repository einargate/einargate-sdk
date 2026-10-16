# Generated from the Einar Gate OpenAPI document by packages/aws/scripts/sdk
# in the Einar Gate monorepo. Do not edit: change the route registry or the
# generator and run `npm run public-api:lock --workspace @einargate/aws`.

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias, TypeVar, Union

from .._runtime import decode as d
from .._runtime import encode as e
from .._runtime.encode import NOT_GIVEN, NotGiven
from .._runtime.errors import ProblemBase, UnknownProblem
from .._runtime.page import Page
from .._runtime.problem import ProblemType, problem_fields
from .._runtime.transport import ProblemInfo, unknown_problem
from .._runtime.unknown import UnknownValue

T = TypeVar("T")

# region Enums

ApiKeyRole: TypeAlias = Literal[
    "IntegrationSetupReader",
    "IntegrationPermissionReader",
    "IntegrationEventReader",
    "IntegrationPermissionManager",
    "IntegrationGateOperator",
]
"""A response field of this type is ``ApiKeyRole | UnknownValue``: the API may add values
within v1.
"""

API_KEY_ROLE_VALUES: tuple[ApiKeyRole, ...] = (
    "IntegrationSetupReader",
    "IntegrationPermissionReader",
    "IntegrationEventReader",
    "IntegrationPermissionManager",
    "IntegrationGateOperator",
)


def decode_api_key_role(value: object, path: str) -> ApiKeyRole | UnknownValue:
    text = d.string(value, path)
    if text in API_KEY_ROLE_VALUES:
        return text
    return UnknownValue(text)


CameraConnectionStatus: TypeAlias = Literal["online", "offline"]
"""A response field of this type is ``CameraConnectionStatus | UnknownValue``: the API may
add values within v1.
"""

CAMERA_CONNECTION_STATUS_VALUES: tuple[CameraConnectionStatus, ...] = (
    "online",
    "offline",
)


def decode_camera_connection_status(
    value: object, path: str
) -> CameraConnectionStatus | UnknownValue:
    text = d.string(value, path)
    if text in CAMERA_CONNECTION_STATUS_VALUES:
        return text
    return UnknownValue(text)


CameraStatus: TypeAlias = Literal["initializing", "active", "deleting"]
"""The camera’s registration at the gate.

A response field of this type is ``CameraStatus | UnknownValue``: the API may add values
within v1.
"""

CAMERA_STATUS_VALUES: tuple[CameraStatus, ...] = ("initializing", "active", "deleting")


def decode_camera_status(value: object, path: str) -> CameraStatus | UnknownValue:
    text = d.string(value, path)
    if text in CAMERA_STATUS_VALUES:
        return text
    return UnknownValue(text)


EventAttachmentStatus: TypeAlias = Literal["requested", "uploaded", "error"]
"""A manual opening’s snapshot: requested from the camera, uploaded, or failed.

A response field of this type is ``EventAttachmentStatus | UnknownValue``: the API may
add values within v1.
"""

EVENT_ATTACHMENT_STATUS_VALUES: tuple[EventAttachmentStatus, ...] = (
    "requested",
    "uploaded",
    "error",
)


def decode_event_attachment_status(
    value: object, path: str
) -> EventAttachmentStatus | UnknownValue:
    text = d.string(value, path)
    if text in EVENT_ATTACHMENT_STATUS_VALUES:
        return text
    return UnknownValue(text)


EventStatus: TypeAlias = Literal["pending", "finalized", "canceled", "failed"]
"""A gate opening is ``pending`` until its data and images arrive.

A response field of this type is ``EventStatus | UnknownValue``: the API may add values
within v1.
"""

EVENT_STATUS_VALUES: tuple[EventStatus, ...] = (
    "pending",
    "finalized",
    "canceled",
    "failed",
)


def decode_event_status(value: object, path: str) -> EventStatus | UnknownValue:
    text = d.string(value, path)
    if text in EVENT_STATUS_VALUES:
        return text
    return UnknownValue(text)


EventType: TypeAlias = Literal["AutomaticGateOpening", "ManualGateOpening"]
"""A response field of this type is ``EventType | UnknownValue``: the API may add values
within v1.
"""

EVENT_TYPE_VALUES: tuple[EventType, ...] = ("AutomaticGateOpening", "ManualGateOpening")


def decode_event_type(value: object, path: str) -> EventType | UnknownValue:
    text = d.string(value, path)
    if text in EVENT_TYPE_VALUES:
        return text
    return UnknownValue(text)


MemberRole: TypeAlias = Literal["LocationOwner", "LocationAdmin", "LocationUser"]
"""A response field of this type is ``MemberRole | UnknownValue``: the API may add values
within v1.
"""

MEMBER_ROLE_VALUES: tuple[MemberRole, ...] = (
    "LocationOwner",
    "LocationAdmin",
    "LocationUser",
)


def decode_member_role(value: object, path: str) -> MemberRole | UnknownValue:
    text = d.string(value, path)
    if text in MEMBER_ROLE_VALUES:
        return text
    return UnknownValue(text)


MemberStatus: TypeAlias = Literal[
    "invited", "invitation_declined", "acknowledged", "member", "deleting"
]
"""Only a ``member`` can own permissions; the others are invitations in progress or a
membership being removed.

A response field of this type is ``MemberStatus | UnknownValue``: the API may add values
within v1.
"""

MEMBER_STATUS_VALUES: tuple[MemberStatus, ...] = (
    "invited",
    "invitation_declined",
    "acknowledged",
    "member",
    "deleting",
)


def decode_member_status(value: object, path: str) -> MemberStatus | UnknownValue:
    text = d.string(value, path)
    if text in MEMBER_STATUS_VALUES:
        return text
    return UnknownValue(text)


RateLimitWindow: TypeAlias = Literal["second", "day"]
"""A response field of this type is ``RateLimitWindow | UnknownValue``: the API may add
values within v1.
"""

RATE_LIMIT_WINDOW_VALUES: tuple[RateLimitWindow, ...] = ("second", "day")


def decode_rate_limit_window(
    value: object, path: str
) -> RateLimitWindow | UnknownValue:
    text = d.string(value, path)
    if text in RATE_LIMIT_WINDOW_VALUES:
        return text
    return UnknownValue(text)


# endregion Enums
# region References and scopes


@dataclass(frozen=True, slots=True)
class GateRef:
    """A gate of the location: a ``Gate``, or its id. Calls also take the entity itself."""

    gate_id: str


@dataclass(frozen=True, slots=True)
class CameraRef:
    """A camera of a gate: a ``Camera``, or its gate and camera ids. Calls also take the
    entity itself.
    """

    gate_id: str
    camera_id: str


@dataclass(frozen=True, slots=True)
class PermissionRef:
    """A permission of a camera: a ``Permission``, or its gate, camera and permission ids.
    The permission id is opaque: use it as returned.. Calls also take the entity itself.
    """

    gate_id: str
    camera_id: str
    permission_id: str


@dataclass(frozen=True, slots=True)
class EventRef:
    """An event of the location: an ``Event``, or its id. Calls also take the entity
    itself.
    """

    event_id: str


@dataclass(frozen=True, slots=True)
class GateScope:
    """Every camera of a gate, as a call’s ``at``."""

    gate_id: str


@dataclass(frozen=True, slots=True)
class CameraScope:
    """One camera of a gate, as a call’s ``at``."""

    gate_id: str
    camera_id: str


# endregion References and scopes
# region Models


@dataclass(frozen=True, slots=True, kw_only=True)
class Camera:
    """A camera registered at a gate"""

    camera_id: str
    location_id: str
    gate_id: str
    name: str
    status: CameraStatus | UnknownValue
    """The camera’s registration at the gate"""
    connection: CameraConnection
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CameraConnection:
    status: CameraConnectionStatus | UnknownValue
    disconnected_at: datetime | None = None
    """When an offline camera was last connected, if known"""


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePermission:
    license_plate: str
    """As typed; whitespace and dashes are removed"""
    license_plate_country: str | NotGiven | None = NOT_GIVEN
    """``null`` for a plate without a country; when left out, the location’s
    ``defaultLicensePlateCountry``
    """
    owner_user_id: str
    """A member of the location whose status is ``member``; the plate counts against
    their limit
    """
    active: bool
    supplemental_info: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePermissionResult:
    """The permission as added to each camera that got it, and the cameras that did not"""

    created: tuple[Permission, ...]
    """Never empty: when no camera got it, the answer is a problem"""
    failed: tuple[FailedCamera, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Event:
    """A gate opening"""

    event_id: str
    type: EventType | UnknownValue
    status: EventStatus | UnknownValue
    """A gate opening is ``pending`` until its data and images arrive"""
    location_id: str
    gate_id: str
    camera_id: str | None = None
    """The camera that recognized the plate; not set on manual openings"""
    event_time: datetime
    initiator: EventInitiator | None = None
    plate: EventPlate | None = None
    """The recognized plate; automatic openings"""
    vehicle: EventVehicle | None = None
    """The recognized vehicle; automatic openings"""
    direction: str | None = None
    speed: float | None = None
    fraud_risk_percentage: float | None = None
    permission: EventPermission | None = None
    """The permission that let the vehicle in"""
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class EventAttachment:
    file_name: str
    role: str
    """E.g. ``Overview`` or ``Plate``"""
    media_type: str
    status: EventAttachmentStatus | UnknownValue | None = None
    """A manual opening’s snapshot: requested from the camera, uploaded, or failed"""
    url: str | None = None
    """A presigned URL, valid for 15 minutes; set once the file is uploaded"""


@dataclass(frozen=True, slots=True, kw_only=True)
class EventInitiatorUser:
    type: Literal["user"] = "user"
    user_id: str
    display_name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EventInitiatorApiKey:
    type: Literal["api-key"] = "api-key"
    api_key_id: str
    display_name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UnknownEventInitiator:
    """A variant of ``EventInitiator`` that this version does not know. ``raw`` is the
    object as sent.
    """

    type: UnknownValue
    raw: Mapping[str, object]


EventInitiator: TypeAlias = Union[
    EventInitiatorUser, EventInitiatorApiKey, UnknownEventInitiator
]
"""Manual openings only"""


@dataclass(frozen=True, slots=True, kw_only=True)
class EventPermission:
    """The permission that let the vehicle in"""

    permission_id: str
    camera_id: str
    owner_user_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EventPlate:
    """The recognized plate; automatic openings"""

    text: str
    country: str
    confidence: float


@dataclass(frozen=True, slots=True, kw_only=True)
class EventVehicle:
    """The recognized vehicle; automatic openings"""

    category: str
    make: str
    model: str
    color: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EventWithAttachments(Event):
    """A gate opening with its images"""

    attachments: tuple[EventAttachment, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class FailedCamera:
    """A camera that did not get the permission: ``conflict`` when it already has one for
    the plate and country, ``limit-exceeded`` when a plate limit of the location or the
    owner would be exceeded
    """

    camera_id: str
    error: ConflictProblem | LimitExceededProblem | UnknownProblem


@dataclass(frozen=True, slots=True, kw_only=True)
class Gate:
    gate_id: str
    location_id: str
    name: str
    manual_operation: bool
    """Whether any member of the location may open it in the app"""
    gate_control_camera_id: str | None = None
    """The camera that opens the gate; a gate without one cannot be opened"""
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class InvalidRequestIssue:
    path: str
    message: str

    @property
    def python_name(self) -> str:
        """The member’s name in this library, e.g. ``license_plate``."""
        return d.python_name(self.path)


@dataclass(frozen=True, slots=True, kw_only=True)
class Location:
    location_id: str
    name: str
    address: str
    timezone: str | None = None
    """IANA time zone, e.g. ``Europe/Budapest``"""
    default_license_plate_country: str | None = None
    """The country a permission gets when it is created without one"""
    limits: LocationLimits
    subscription_active: bool
    """Opening gates requires an active subscription"""
    event_retention_days: int | None = None
    """How many days events are kept; not set when they are kept indefinitely"""
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class LocationLimits:
    """The location’s limits. A limit that is not set is the default of the location’s
    plan.
    """

    max_users: int | None = None
    max_gates: int | None = None
    max_cameras_per_gate: int | None = None
    max_plates_per_user: int | None = None
    max_plates_in_plan: int | None = None
    max_events_with_attachments: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Me:
    """The calling API key"""

    api_key_id: str
    name: str
    location_id: str
    roles: tuple[ApiKeyRole | UnknownValue, ...]
    """The roles the API key holds at its location"""
    subscription_active: bool
    """Whether the location's subscription is active. Opening gates requires an
    active subscription.
    """
    rate_limit: RateLimit
    value_retires_at: datetime | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Member:
    """A member or an invitee of the location"""

    user_id: str | None = None
    """Set once the user has an account; a permission’s owner must be a member whose
    status is ``member``
    """
    email: str
    given_name: str | None = None
    family_name: str | None = None
    role: MemberRole | UnknownValue
    status: MemberStatus | UnknownValue
    """Only a ``member`` can own permissions; the others are invitations in progress
    or a membership being removed
    """


@dataclass(frozen=True, slots=True, kw_only=True)
class Permission:
    """A plate’s permission on one camera. The owner’s private name and comment are never
    exposed.
    """

    permission_id: str
    """**Opaque: store it as it is and URL-encode it in paths.** Find a permission by
    plate with the ``licensePlate`` filter instead of building an id.
    """
    location_id: str
    gate_id: str
    camera_id: str
    license_plate: str
    """Normalized"""
    license_plate_country: str | None
    """Upper-case; ``null`` when the plate has no country"""
    owner_user_id: str
    active: bool
    supplemental_info: str | None = None
    number_of_openings: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class RateLimit:
    """The configured limits, shared by all API keys of the location. Live counters are not
    available.
    """

    requests_per_second: int
    """Sustained requests per second for the location"""
    burst: int
    """Requests the location may send at once before throttling"""
    requests_per_day: int
    """Daily quota of the location; it resets at the start of each day"""


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplacePermission:
    """The full representation of the permission’s fields an API key manages; a field that
    is not given is removed. The owner cannot be changed, and the owner’s private name
    and comment are kept.
    """

    license_plate: str
    """As typed; changing it changes the ``permissionId``, which the response returns"""
    license_plate_country: str | None
    """``null`` for a plate without a country"""
    active: bool
    supplemental_info: str | None
    """``null`` removes it"""


# endregion Models
# region Problems


@dataclass(frozen=True, slots=True, kw_only=True)
class ConflictProblem(ProblemBase):
    """Conflict: The entity already exists (for a permission: the camera already has the
    plate and country) or was changed at the same time. Read it again before deciding; a
    concurrent change is safe to retry.
    """

    type: Literal["conflict"] = "conflict"
    status: Literal[409] = 409


CONFLICT_PROBLEM = ProblemType(
    slug="conflict",
    status=409,
    title="Conflict",
    hint="The entity already exists (for a permission: the camera already has the plate and country) or was changed at the same time. Read it again before deciding; a concurrent change is safe to retry.",
    docs_url="https://developers.einargate.com/errors/conflict",
)


def decode_conflict_problem(body: d.JsonObject, info: ProblemInfo) -> ConflictProblem:
    return ConflictProblem(**problem_fields(body, CONFLICT_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class ForbiddenProblem(ProblemBase):
    """Forbidden: The API key lacks a role for this action, the path names another
    location, or the action needs an active subscription. ``GET /me`` shows the key’s
    roles, location and subscription state; a location Owner or Admin changes its roles
    in the app.
    """

    type: Literal["forbidden"] = "forbidden"
    status: Literal[403] = 403


FORBIDDEN_PROBLEM = ProblemType(
    slug="forbidden",
    status=403,
    title="Forbidden",
    hint="The API key lacks a role for this action, the path names another location, or the action needs an active subscription. `GET /me` shows the key’s roles, location and subscription state; a location Owner or Admin changes its roles in the app.",
    docs_url="https://developers.einargate.com/errors/forbidden",
)


def decode_forbidden_problem(body: d.JsonObject, info: ProblemInfo) -> ForbiddenProblem:
    return ForbiddenProblem(**problem_fields(body, FORBIDDEN_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class GateNotOperableProblem(ProblemBase):
    """Gate not operable: The gate cannot be opened now: it has no control camera, the
    camera is offline, or the gate is not set up for control. Check its
    ``gateControlCameraId`` and that camera’s ``connection.status``.
    """

    type: Literal["gate-not-operable"] = "gate-not-operable"
    status: Literal[422] = 422


GATE_NOT_OPERABLE_PROBLEM = ProblemType(
    slug="gate-not-operable",
    status=422,
    title="Gate not operable",
    hint="The gate cannot be opened now: it has no control camera, the camera is offline, or the gate is not set up for control. Check its `gateControlCameraId` and that camera’s `connection.status`.",
    docs_url="https://developers.einargate.com/errors/gate-not-operable",
)


def decode_gate_not_operable_problem(
    body: d.JsonObject, info: ProblemInfo
) -> GateNotOperableProblem:
    return GateNotOperableProblem(
        **problem_fields(body, GATE_NOT_OPERABLE_PROBLEM, info)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class IdempotencyKeyInFlightProblem(ProblemBase):
    """Idempotency key in flight: A request with the same ``Idempotency-Key`` is still
    running: wait a moment and retry with the same key.
    """

    type: Literal["idempotency-key-in-flight"] = "idempotency-key-in-flight"
    status: Literal[409] = 409


IDEMPOTENCY_KEY_IN_FLIGHT_PROBLEM = ProblemType(
    slug="idempotency-key-in-flight",
    status=409,
    title="Idempotency key in flight",
    hint="A request with the same `Idempotency-Key` is still running: wait a moment and retry with the same key.",
    docs_url="https://developers.einargate.com/errors/idempotency-key-in-flight",
)


def decode_idempotency_key_in_flight_problem(
    body: d.JsonObject, info: ProblemInfo
) -> IdempotencyKeyInFlightProblem:
    return IdempotencyKeyInFlightProblem(
        **problem_fields(body, IDEMPOTENCY_KEY_IN_FLIGHT_PROBLEM, info)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class IdempotencyKeyReuseProblem(ProblemBase):
    """Idempotency key reused: The ``Idempotency-Key`` was used for a different request in
    the last 24 hours: send a new request with a new key.
    """

    type: Literal["idempotency-key-reuse"] = "idempotency-key-reuse"
    status: Literal[422] = 422


IDEMPOTENCY_KEY_REUSE_PROBLEM = ProblemType(
    slug="idempotency-key-reuse",
    status=422,
    title="Idempotency key reused",
    hint="The `Idempotency-Key` was used for a different request in the last 24 hours: send a new request with a new key.",
    docs_url="https://developers.einargate.com/errors/idempotency-key-reuse",
)


def decode_idempotency_key_reuse_problem(
    body: d.JsonObject, info: ProblemInfo
) -> IdempotencyKeyReuseProblem:
    return IdempotencyKeyReuseProblem(
        **problem_fields(body, IDEMPOTENCY_KEY_REUSE_PROBLEM, info)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class InternalProblem(ProblemBase):
    """Internal error: An unexpected error on our side. Retry later, and send the
    ``requestId`` to support if it persists. Before retrying a gate opening, check the
    events: the gate may have opened.
    """

    type: Literal["internal"] = "internal"
    status: Literal[500] = 500


INTERNAL_PROBLEM = ProblemType(
    slug="internal",
    status=500,
    title="Internal error",
    hint="An unexpected error on our side. Retry later, and send the `requestId` to support if it persists. Before retrying a gate opening, check the events: the gate may have opened.",
    docs_url="https://developers.einargate.com/errors/internal",
)


def decode_internal_problem(body: d.JsonObject, info: ProblemInfo) -> InternalProblem:
    return InternalProblem(**problem_fields(body, INTERNAL_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class InvalidOwnerProblem(ProblemBase):
    """Invalid owner: Set ``ownerUserId`` to the ``userId`` of a member whose status is
    ``member`` (``GET /locations/{locationId}/members``).
    """

    type: Literal["invalid-owner"] = "invalid-owner"
    status: Literal[422] = 422


INVALID_OWNER_PROBLEM = ProblemType(
    slug="invalid-owner",
    status=422,
    title="Invalid owner",
    hint="Set `ownerUserId` to the `userId` of a member whose status is `member` (`GET /locations/{locationId}/members`).",
    docs_url="https://developers.einargate.com/errors/invalid-owner",
)


def decode_invalid_owner_problem(
    body: d.JsonObject, info: ProblemInfo
) -> InvalidOwnerProblem:
    return InvalidOwnerProblem(**problem_fields(body, INVALID_OWNER_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class InvalidRequestProblem(ProblemBase):
    """Invalid request: Fix the members that ``errors[]`` lists and send the request again.
    A body member’s path is bare (``licensePlate``); query and path parameters are
    prefixed ``query.`` and ``path.``.
    """

    type: Literal["invalid-request"] = "invalid-request"
    status: Literal[400] = 400
    errors: tuple[InvalidRequestIssue, ...]


INVALID_REQUEST_PROBLEM = ProblemType(
    slug="invalid-request",
    status=400,
    title="Invalid request",
    hint="Fix the members that `errors[]` lists and send the request again. A body member’s path is bare (`licensePlate`); query and path parameters are prefixed `query.` and `path.`.",
    docs_url="https://developers.einargate.com/errors/invalid-request",
)


def decode_invalid_request_problem(
    body: d.JsonObject, info: ProblemInfo
) -> InvalidRequestProblem:
    return InvalidRequestProblem(
        **problem_fields(body, INVALID_REQUEST_PROBLEM, info),
        errors=d.required(
            body, "errors", "", d.array_decoder(decode_invalid_request_issue)
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class LimitExceededProblem(ProblemBase):
    """Limit exceeded: A limit of the location’s plan or of the owner would be exceeded;
    the location’s ``limits`` show them. Remove permissions first, or ask the location
    Owner to change the plan.
    """

    type: Literal["limit-exceeded"] = "limit-exceeded"
    status: Literal[422] = 422


LIMIT_EXCEEDED_PROBLEM = ProblemType(
    slug="limit-exceeded",
    status=422,
    title="Limit exceeded",
    hint="A limit of the location’s plan or of the owner would be exceeded; the location’s `limits` show them. Remove permissions first, or ask the location Owner to change the plan.",
    docs_url="https://developers.einargate.com/errors/limit-exceeded",
)


def decode_limit_exceeded_problem(
    body: d.JsonObject, info: ProblemInfo
) -> LimitExceededProblem:
    return LimitExceededProblem(**problem_fields(body, LIMIT_EXCEEDED_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class NotFoundProblem(ProblemBase):
    """Not found: Use ids exactly as the API returned them, under the API key’s own
    location, and URL-encode permission ids. Never build an id.
    """

    type: Literal["not-found"] = "not-found"
    status: Literal[404] = 404


NOT_FOUND_PROBLEM = ProblemType(
    slug="not-found",
    status=404,
    title="Not found",
    hint="Use ids exactly as the API returned them, under the API key’s own location, and URL-encode permission ids. Never build an id.",
    docs_url="https://developers.einargate.com/errors/not-found",
)


def decode_not_found_problem(body: d.JsonObject, info: ProblemInfo) -> NotFoundProblem:
    return NotFoundProblem(**problem_fields(body, NOT_FOUND_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvisioningProblem(ProblemBase):
    """Provisioning in progress: The location’s first API key was created moments ago:
    retry after ``Retry-After`` seconds.
    """

    type: Literal["provisioning"] = "provisioning"
    status: Literal[503] = 503


PROVISIONING_PROBLEM = ProblemType(
    slug="provisioning",
    status=503,
    title="Provisioning in progress",
    hint="The location’s first API key was created moments ago: retry after `Retry-After` seconds.",
    docs_url="https://developers.einargate.com/errors/provisioning",
)


def decode_provisioning_problem(
    body: d.JsonObject, info: ProblemInfo
) -> ProvisioningProblem:
    return ProvisioningProblem(**problem_fields(body, PROVISIONING_PROBLEM, info))


@dataclass(frozen=True, slots=True, kw_only=True)
class RateLimitedProblem(ProblemBase):
    """Rate limit exceeded: Wait ``Retry-After`` seconds when ``window`` is ``second``, or
    until the next day when it is ``day``. Every API key of the location shares the
    limits that ``GET /me`` shows.
    """

    type: Literal["rate-limited"] = "rate-limited"
    status: Literal[429] = 429
    window: RateLimitWindow | UnknownValue


RATE_LIMITED_PROBLEM = ProblemType(
    slug="rate-limited",
    status=429,
    title="Rate limit exceeded",
    hint="Wait `Retry-After` seconds when `window` is `second`, or until the next day when it is `day`. Every API key of the location shares the limits that `GET /me` shows.",
    docs_url="https://developers.einargate.com/errors/rate-limited",
)


def decode_rate_limited_problem(
    body: d.JsonObject, info: ProblemInfo
) -> RateLimitedProblem:
    return RateLimitedProblem(
        **problem_fields(body, RATE_LIMITED_PROBLEM, info),
        window=d.required(body, "window", "", decode_rate_limit_window),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ServiceUnavailableProblem(ProblemBase):
    """Service unavailable: A dependency was briefly unavailable: send the same request
    again after a short wait, with the same ``Idempotency-Key`` for a write.
    """

    type: Literal["service-unavailable"] = "service-unavailable"
    status: Literal[503] = 503


SERVICE_UNAVAILABLE_PROBLEM = ProblemType(
    slug="service-unavailable",
    status=503,
    title="Service unavailable",
    hint="A dependency was briefly unavailable: send the same request again after a short wait, with the same `Idempotency-Key` for a write.",
    docs_url="https://developers.einargate.com/errors/service-unavailable",
)


def decode_service_unavailable_problem(
    body: d.JsonObject, info: ProblemInfo
) -> ServiceUnavailableProblem:
    return ServiceUnavailableProblem(
        **problem_fields(body, SERVICE_UNAVAILABLE_PROBLEM, info)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class UnauthorizedProblem(ProblemBase):
    """Unauthorized: Send a working API key value as ``Authorization: Bearer egk_…``. A
    value stops working when it is revoked, or retired after a rotation: get the current
    one from whoever manages the API key in the Einar Gate app.
    """

    type: Literal["unauthorized"] = "unauthorized"
    status: Literal[401] = 401


UNAUTHORIZED_PROBLEM = ProblemType(
    slug="unauthorized",
    status=401,
    title="Unauthorized",
    hint="Send a working API key value as `Authorization: Bearer egk_…`. A value stops working when it is revoked, or retired after a rotation: get the current one from whoever manages the API key in the Einar Gate app.",
    docs_url="https://developers.einargate.com/errors/unauthorized",
)


def decode_unauthorized_problem(
    body: d.JsonObject, info: ProblemInfo
) -> UnauthorizedProblem:
    return UnauthorizedProblem(**problem_fields(body, UNAUTHORIZED_PROBLEM, info))


Problem: TypeAlias = Union[
    ConflictProblem,
    ForbiddenProblem,
    GateNotOperableProblem,
    IdempotencyKeyInFlightProblem,
    IdempotencyKeyReuseProblem,
    InternalProblem,
    InvalidOwnerProblem,
    InvalidRequestProblem,
    LimitExceededProblem,
    NotFoundProblem,
    ProvisioningProblem,
    RateLimitedProblem,
    ServiceUnavailableProblem,
    UnauthorizedProblem,
]
"""A problem of a type this version knows"""

PROBLEM_TYPES: dict[str, ProblemType] = {
    "conflict": CONFLICT_PROBLEM,
    "forbidden": FORBIDDEN_PROBLEM,
    "gate-not-operable": GATE_NOT_OPERABLE_PROBLEM,
    "idempotency-key-in-flight": IDEMPOTENCY_KEY_IN_FLIGHT_PROBLEM,
    "idempotency-key-reuse": IDEMPOTENCY_KEY_REUSE_PROBLEM,
    "internal": INTERNAL_PROBLEM,
    "invalid-owner": INVALID_OWNER_PROBLEM,
    "invalid-request": INVALID_REQUEST_PROBLEM,
    "limit-exceeded": LIMIT_EXCEEDED_PROBLEM,
    "not-found": NOT_FOUND_PROBLEM,
    "provisioning": PROVISIONING_PROBLEM,
    "rate-limited": RATE_LIMITED_PROBLEM,
    "service-unavailable": SERVICE_UNAVAILABLE_PROBLEM,
    "unauthorized": UNAUTHORIZED_PROBLEM,
}
"""Every problem type: its status, title, hint and catalogue page"""


def decode_embedded_problem(
    value: object, path: str, slugs: tuple[str, ...]
) -> Problem | UnknownProblem:
    """Decodes a problem embedded in a body (a failed camera of a permission create). A
    type not listed is an ``UnknownProblem``.
    """
    body = d.object_(value, path)
    type_ = body.get("type")
    base = "https://developers.einargate.com/errors/"
    if isinstance(type_, str) and type_.startswith(base):
        slug = type_[len(base) :]
        decoder = _PROBLEM_DECODERS.get(slug)
        if slug in slugs and decoder is not None:
            try:
                return decoder(body, ProblemInfo())
            except d.DecodeError:
                pass
    status = body.get("status")
    return unknown_problem(status if isinstance(status, int) else 0, body)


_PROBLEM_DECODERS = {
    "conflict": decode_conflict_problem,
    "forbidden": decode_forbidden_problem,
    "gate-not-operable": decode_gate_not_operable_problem,
    "idempotency-key-in-flight": decode_idempotency_key_in_flight_problem,
    "idempotency-key-reuse": decode_idempotency_key_reuse_problem,
    "internal": decode_internal_problem,
    "invalid-owner": decode_invalid_owner_problem,
    "invalid-request": decode_invalid_request_problem,
    "limit-exceeded": decode_limit_exceeded_problem,
    "not-found": decode_not_found_problem,
    "provisioning": decode_provisioning_problem,
    "rate-limited": decode_rate_limited_problem,
    "service-unavailable": decode_service_unavailable_problem,
    "unauthorized": decode_unauthorized_problem,
}

# endregion Problems
# region Decoders


def decode_camera(value: object, path: str) -> Camera:
    o = d.object_(value, path)
    return Camera(
        camera_id=d.required(o, "cameraId", path, d.string),
        location_id=d.required(o, "locationId", path, d.string),
        gate_id=d.required(o, "gateId", path, d.string),
        name=d.required(o, "name", path, d.string),
        status=d.required(o, "status", path, decode_camera_status),
        connection=d.required(o, "connection", path, decode_camera_connection),
        created_at=d.required(o, "createdAt", path, d.timestamp),
        updated_at=d.required(o, "updatedAt", path, d.timestamp),
    )


def decode_camera_connection(value: object, path: str) -> CameraConnection:
    o = d.object_(value, path)
    return CameraConnection(
        status=d.required(o, "status", path, decode_camera_connection_status),
        disconnected_at=d.optional(o, "disconnectedAt", path, d.timestamp),
    )


def decode_create_permission_result(value: object, path: str) -> CreatePermissionResult:
    o = d.object_(value, path)
    return CreatePermissionResult(
        created=d.required(
            o, "created", path, d.non_empty_array_decoder(decode_permission)
        ),
        failed=d.required(o, "failed", path, d.array_decoder(decode_failed_camera)),
    )


def decode_event(value: object, path: str) -> Event:
    o = d.object_(value, path)
    return Event(
        event_id=d.required(o, "eventId", path, d.string),
        type=d.required(o, "type", path, decode_event_type),
        status=d.required(o, "status", path, decode_event_status),
        location_id=d.required(o, "locationId", path, d.string),
        gate_id=d.required(o, "gateId", path, d.string),
        camera_id=d.optional(o, "cameraId", path, d.string),
        event_time=d.required(o, "eventTime", path, d.timestamp),
        initiator=d.optional(o, "initiator", path, decode_event_initiator),
        plate=d.optional(o, "plate", path, decode_event_plate),
        vehicle=d.optional(o, "vehicle", path, decode_event_vehicle),
        direction=d.optional(o, "direction", path, d.string),
        speed=d.optional(o, "speed", path, d.number),
        fraud_risk_percentage=d.optional(o, "fraudRiskPercentage", path, d.number),
        permission=d.optional(o, "permission", path, decode_event_permission),
        created_at=d.required(o, "createdAt", path, d.timestamp),
        updated_at=d.required(o, "updatedAt", path, d.timestamp),
    )


def decode_event_attachment(value: object, path: str) -> EventAttachment:
    o = d.object_(value, path)
    return EventAttachment(
        file_name=d.required(o, "fileName", path, d.string),
        role=d.required(o, "role", path, d.string),
        media_type=d.required(o, "mediaType", path, d.string),
        status=d.optional(o, "status", path, decode_event_attachment_status),
        url=d.optional(o, "url", path, d.string),
    )


def decode_event_initiator_user(value: object, path: str) -> EventInitiatorUser:
    o = d.object_(value, path)
    return EventInitiatorUser(
        user_id=d.required(o, "userId", path, d.string),
        display_name=d.required(o, "displayName", path, d.string),
    )


def decode_event_initiator_api_key(value: object, path: str) -> EventInitiatorApiKey:
    o = d.object_(value, path)
    return EventInitiatorApiKey(
        api_key_id=d.required(o, "apiKeyId", path, d.string),
        display_name=d.required(o, "displayName", path, d.string),
    )


def decode_event_initiator(value: object, path: str) -> EventInitiator:
    o = d.object_(value, path)
    kind = o.get("type")
    if kind == "user":
        return decode_event_initiator_user(o, path)
    if kind == "api-key":
        return decode_event_initiator_api_key(o, path)
    return UnknownEventInitiator(
        type=UnknownValue(d.required(o, "type", path, d.string)), raw=o
    )


def decode_event_permission(value: object, path: str) -> EventPermission:
    o = d.object_(value, path)
    return EventPermission(
        permission_id=d.required(o, "permissionId", path, d.string),
        camera_id=d.required(o, "cameraId", path, d.string),
        owner_user_id=d.required(o, "ownerUserId", path, d.string),
    )


def decode_event_plate(value: object, path: str) -> EventPlate:
    o = d.object_(value, path)
    return EventPlate(
        text=d.required(o, "text", path, d.string),
        country=d.required(o, "country", path, d.string),
        confidence=d.required(o, "confidence", path, d.number),
    )


def decode_event_vehicle(value: object, path: str) -> EventVehicle:
    o = d.object_(value, path)
    return EventVehicle(
        category=d.required(o, "category", path, d.string),
        make=d.required(o, "make", path, d.string),
        model=d.required(o, "model", path, d.string),
        color=d.required(o, "color", path, d.string),
    )


def decode_event_with_attachments(value: object, path: str) -> EventWithAttachments:
    o = d.object_(value, path)
    return EventWithAttachments(
        event_id=d.required(o, "eventId", path, d.string),
        type=d.required(o, "type", path, decode_event_type),
        status=d.required(o, "status", path, decode_event_status),
        location_id=d.required(o, "locationId", path, d.string),
        gate_id=d.required(o, "gateId", path, d.string),
        camera_id=d.optional(o, "cameraId", path, d.string),
        event_time=d.required(o, "eventTime", path, d.timestamp),
        initiator=d.optional(o, "initiator", path, decode_event_initiator),
        plate=d.optional(o, "plate", path, decode_event_plate),
        vehicle=d.optional(o, "vehicle", path, decode_event_vehicle),
        direction=d.optional(o, "direction", path, d.string),
        speed=d.optional(o, "speed", path, d.number),
        fraud_risk_percentage=d.optional(o, "fraudRiskPercentage", path, d.number),
        permission=d.optional(o, "permission", path, decode_event_permission),
        created_at=d.required(o, "createdAt", path, d.timestamp),
        updated_at=d.required(o, "updatedAt", path, d.timestamp),
        attachments=d.required(
            o, "attachments", path, d.array_decoder(decode_event_attachment)
        ),
    )


def decode_failed_camera(value: object, path: str) -> FailedCamera:
    o = d.object_(value, path)
    return FailedCamera(
        camera_id=d.required(o, "cameraId", path, d.string),
        error=d.required(
            o, "error", path, problems_decoder(("conflict", "limit-exceeded"))
        ),
    )


def decode_gate(value: object, path: str) -> Gate:
    o = d.object_(value, path)
    return Gate(
        gate_id=d.required(o, "gateId", path, d.string),
        location_id=d.required(o, "locationId", path, d.string),
        name=d.required(o, "name", path, d.string),
        manual_operation=d.required(o, "manualOperation", path, d.boolean),
        gate_control_camera_id=d.optional(o, "gateControlCameraId", path, d.string),
        created_at=d.required(o, "createdAt", path, d.timestamp),
        updated_at=d.required(o, "updatedAt", path, d.timestamp),
    )


def decode_invalid_request_issue(value: object, path: str) -> InvalidRequestIssue:
    o = d.object_(value, path)
    return InvalidRequestIssue(
        path=d.required(o, "path", path, d.string),
        message=d.required(o, "message", path, d.string),
    )


def decode_location(value: object, path: str) -> Location:
    o = d.object_(value, path)
    return Location(
        location_id=d.required(o, "locationId", path, d.string),
        name=d.required(o, "name", path, d.string),
        address=d.required(o, "address", path, d.string),
        timezone=d.optional(o, "timezone", path, d.string),
        default_license_plate_country=d.optional(
            o, "defaultLicensePlateCountry", path, d.string
        ),
        limits=d.required(o, "limits", path, decode_location_limits),
        subscription_active=d.required(o, "subscriptionActive", path, d.boolean),
        event_retention_days=d.optional(o, "eventRetentionDays", path, d.integer),
        created_at=d.required(o, "createdAt", path, d.timestamp),
        updated_at=d.required(o, "updatedAt", path, d.timestamp),
    )


def decode_location_limits(value: object, path: str) -> LocationLimits:
    o = d.object_(value, path)
    return LocationLimits(
        max_users=d.optional(o, "maxUsers", path, d.integer),
        max_gates=d.optional(o, "maxGates", path, d.integer),
        max_cameras_per_gate=d.optional(o, "maxCamerasPerGate", path, d.integer),
        max_plates_per_user=d.optional(o, "maxPlatesPerUser", path, d.integer),
        max_plates_in_plan=d.optional(o, "maxPlatesInPlan", path, d.integer),
        max_events_with_attachments=d.optional(
            o, "maxEventsWithAttachments", path, d.integer
        ),
    )


def decode_me(value: object, path: str) -> Me:
    o = d.object_(value, path)
    return Me(
        api_key_id=d.required(o, "apiKeyId", path, d.string),
        name=d.required(o, "name", path, d.string),
        location_id=d.required(o, "locationId", path, d.string),
        roles=d.required(o, "roles", path, d.array_decoder(decode_api_key_role)),
        subscription_active=d.required(o, "subscriptionActive", path, d.boolean),
        rate_limit=d.required(o, "rateLimit", path, decode_rate_limit),
        value_retires_at=d.optional(o, "valueRetiresAt", path, d.timestamp),
    )


def decode_member(value: object, path: str) -> Member:
    o = d.object_(value, path)
    return Member(
        user_id=d.optional(o, "userId", path, d.string),
        email=d.required(o, "email", path, d.string),
        given_name=d.optional(o, "givenName", path, d.string),
        family_name=d.optional(o, "familyName", path, d.string),
        role=d.required(o, "role", path, decode_member_role),
        status=d.required(o, "status", path, decode_member_status),
    )


def decode_permission(value: object, path: str) -> Permission:
    o = d.object_(value, path)
    return Permission(
        permission_id=d.required(o, "permissionId", path, d.string),
        location_id=d.required(o, "locationId", path, d.string),
        gate_id=d.required(o, "gateId", path, d.string),
        camera_id=d.required(o, "cameraId", path, d.string),
        license_plate=d.required(o, "licensePlate", path, d.string),
        license_plate_country=d.required(
            o, "licensePlateCountry", path, d.null_if_empty
        ),
        owner_user_id=d.required(o, "ownerUserId", path, d.string),
        active=d.required(o, "active", path, d.boolean),
        supplemental_info=d.optional(o, "supplementalInfo", path, d.string),
        number_of_openings=d.required(o, "numberOfOpenings", path, d.integer),
        created_at=d.required(o, "createdAt", path, d.timestamp),
        updated_at=d.required(o, "updatedAt", path, d.timestamp),
    )


def decode_rate_limit(value: object, path: str) -> RateLimit:
    o = d.object_(value, path)
    return RateLimit(
        requests_per_second=d.required(o, "requestsPerSecond", path, d.integer),
        burst=d.required(o, "burst", path, d.integer),
        requests_per_day=d.required(o, "requestsPerDay", path, d.integer),
    )


def page_decoder(item: d.Decoder[T]) -> d.Decoder[Page[T]]:

    def decode(value: object, path: str) -> Page[T]:
        o = d.object_(value, path)
        return Page(
            items=d.required(o, "items", path, d.array_decoder(item)),
            continuation_token=d.optional(o, "continuationToken", path, d.string),
        )

    return decode


def problems_decoder(slugs: tuple[str, ...]) -> d.Decoder[Any]:
    """The field’s own type names the problems it can be."""

    def decode(value: object, path: str) -> Any:
        return decode_embedded_problem(value, path, slugs)

    return decode


# endregion Decoders
# region Encoders


def encode_camera(value: Camera) -> dict[str, object]:
    return e.compact(
        {
            "cameraId": value.camera_id,
            "locationId": value.location_id,
            "gateId": value.gate_id,
            "name": value.name,
            "status": e.enum_value(value.status),
            "connection": encode_camera_connection(value.connection),
            "createdAt": e.timestamp(value.created_at),
            "updatedAt": e.timestamp(value.updated_at),
        }
    )


def encode_camera_connection(value: CameraConnection) -> dict[str, object]:
    return e.compact(
        {
            "status": e.enum_value(value.status),
            "disconnectedAt": e.optional(value.disconnected_at, e.timestamp),
        }
    )


def encode_create_permission(value: CreatePermission) -> dict[str, object]:
    return e.compact(
        {
            "licensePlate": value.license_plate,
            "licensePlateCountry": e.three_state(value.license_plate_country),
            "ownerUserId": value.owner_user_id,
            "active": value.active,
            "supplementalInfo": value.supplemental_info,
        }
    )


def encode_create_permission_result(value: CreatePermissionResult) -> dict[str, object]:
    return e.compact(
        {
            "created": [encode_permission(item) for item in value.created],
            "failed": [encode_failed_camera(item) for item in value.failed],
        }
    )


def encode_event(value: Event) -> dict[str, object]:
    return e.compact(
        {
            "eventId": value.event_id,
            "type": e.enum_value(value.type),
            "status": e.enum_value(value.status),
            "locationId": value.location_id,
            "gateId": value.gate_id,
            "cameraId": value.camera_id,
            "eventTime": e.timestamp(value.event_time),
            "initiator": e.optional(value.initiator, encode_event_initiator),
            "plate": e.optional(value.plate, encode_event_plate),
            "vehicle": e.optional(value.vehicle, encode_event_vehicle),
            "direction": value.direction,
            "speed": value.speed,
            "fraudRiskPercentage": value.fraud_risk_percentage,
            "permission": e.optional(value.permission, encode_event_permission),
            "createdAt": e.timestamp(value.created_at),
            "updatedAt": e.timestamp(value.updated_at),
        }
    )


def encode_event_attachment(value: EventAttachment) -> dict[str, object]:
    return e.compact(
        {
            "fileName": value.file_name,
            "role": value.role,
            "mediaType": value.media_type,
            "status": e.optional(value.status, e.enum_value),
            "url": value.url,
        }
    )


def encode_event_initiator_user(value: EventInitiatorUser) -> dict[str, object]:
    return e.compact(
        {"type": value.type, "userId": value.user_id, "displayName": value.display_name}
    )


def encode_event_initiator_api_key(value: EventInitiatorApiKey) -> dict[str, object]:
    return e.compact(
        {
            "type": value.type,
            "apiKeyId": value.api_key_id,
            "displayName": value.display_name,
        }
    )


def encode_event_initiator(value: EventInitiator) -> dict[str, object]:
    if isinstance(value, EventInitiatorUser):
        return encode_event_initiator_user(value)
    if isinstance(value, EventInitiatorApiKey):
        return encode_event_initiator_api_key(value)
    return {**value.raw, "type": str(value.type)}


def encode_event_permission(value: EventPermission) -> dict[str, object]:
    return e.compact(
        {
            "permissionId": value.permission_id,
            "cameraId": value.camera_id,
            "ownerUserId": value.owner_user_id,
        }
    )


def encode_event_plate(value: EventPlate) -> dict[str, object]:
    return e.compact(
        {"text": value.text, "country": value.country, "confidence": value.confidence}
    )


def encode_event_vehicle(value: EventVehicle) -> dict[str, object]:
    return e.compact(
        {
            "category": value.category,
            "make": value.make,
            "model": value.model,
            "color": value.color,
        }
    )


def encode_event_with_attachments(value: EventWithAttachments) -> dict[str, object]:
    return e.compact(
        {
            "eventId": value.event_id,
            "type": e.enum_value(value.type),
            "status": e.enum_value(value.status),
            "locationId": value.location_id,
            "gateId": value.gate_id,
            "cameraId": value.camera_id,
            "eventTime": e.timestamp(value.event_time),
            "initiator": e.optional(value.initiator, encode_event_initiator),
            "plate": e.optional(value.plate, encode_event_plate),
            "vehicle": e.optional(value.vehicle, encode_event_vehicle),
            "direction": value.direction,
            "speed": value.speed,
            "fraudRiskPercentage": value.fraud_risk_percentage,
            "permission": e.optional(value.permission, encode_event_permission),
            "createdAt": e.timestamp(value.created_at),
            "updatedAt": e.timestamp(value.updated_at),
            "attachments": [
                encode_event_attachment(item) for item in value.attachments
            ],
        }
    )


def encode_failed_camera(value: FailedCamera) -> dict[str, object]:
    return e.compact({"cameraId": value.camera_id, "error": value.error.body})


def encode_gate(value: Gate) -> dict[str, object]:
    return e.compact(
        {
            "gateId": value.gate_id,
            "locationId": value.location_id,
            "name": value.name,
            "manualOperation": value.manual_operation,
            "gateControlCameraId": value.gate_control_camera_id,
            "createdAt": e.timestamp(value.created_at),
            "updatedAt": e.timestamp(value.updated_at),
        }
    )


def encode_invalid_request_issue(value: InvalidRequestIssue) -> dict[str, object]:
    return e.compact({"path": value.path, "message": value.message})


def encode_location(value: Location) -> dict[str, object]:
    return e.compact(
        {
            "locationId": value.location_id,
            "name": value.name,
            "address": value.address,
            "timezone": value.timezone,
            "defaultLicensePlateCountry": value.default_license_plate_country,
            "limits": encode_location_limits(value.limits),
            "subscriptionActive": value.subscription_active,
            "eventRetentionDays": value.event_retention_days,
            "createdAt": e.timestamp(value.created_at),
            "updatedAt": e.timestamp(value.updated_at),
        }
    )


def encode_location_limits(value: LocationLimits) -> dict[str, object]:
    return e.compact(
        {
            "maxUsers": value.max_users,
            "maxGates": value.max_gates,
            "maxCamerasPerGate": value.max_cameras_per_gate,
            "maxPlatesPerUser": value.max_plates_per_user,
            "maxPlatesInPlan": value.max_plates_in_plan,
            "maxEventsWithAttachments": value.max_events_with_attachments,
        }
    )


def encode_me(value: Me) -> dict[str, object]:
    return e.compact(
        {
            "apiKeyId": value.api_key_id,
            "name": value.name,
            "locationId": value.location_id,
            "roles": [e.enum_value(item) for item in value.roles],
            "subscriptionActive": value.subscription_active,
            "rateLimit": encode_rate_limit(value.rate_limit),
            "valueRetiresAt": e.optional(value.value_retires_at, e.timestamp),
        }
    )


def encode_member(value: Member) -> dict[str, object]:
    return e.compact(
        {
            "userId": value.user_id,
            "email": value.email,
            "givenName": value.given_name,
            "familyName": value.family_name,
            "role": e.enum_value(value.role),
            "status": e.enum_value(value.status),
        }
    )


def encode_permission(value: Permission) -> dict[str, object]:
    return e.compact(
        {
            "permissionId": value.permission_id,
            "locationId": value.location_id,
            "gateId": value.gate_id,
            "cameraId": value.camera_id,
            "licensePlate": value.license_plate,
            "licensePlateCountry": e.empty_if_none(value.license_plate_country),
            "ownerUserId": value.owner_user_id,
            "active": value.active,
            "supplementalInfo": value.supplemental_info,
            "numberOfOpenings": value.number_of_openings,
            "createdAt": e.timestamp(value.created_at),
            "updatedAt": e.timestamp(value.updated_at),
        }
    )


def encode_rate_limit(value: RateLimit) -> dict[str, object]:
    return e.compact(
        {
            "requestsPerSecond": value.requests_per_second,
            "burst": value.burst,
            "requestsPerDay": value.requests_per_day,
        }
    )


def encode_replace_permission(value: ReplacePermission) -> dict[str, object]:
    return e.compact(
        {
            "licensePlate": value.license_plate,
            "licensePlateCountry": e.empty_if_none(value.license_plate_country),
            "active": value.active,
            "supplementalInfo": value.supplemental_info,
        }
    )


def encode_page(value: Page[T], item: Callable[[T], object]) -> dict[str, object]:
    return e.compact(
        {
            "items": [item(element) for element in value.items],
            "continuationToken": value.continuation_token,
        }
    )


# endregion Encoders

__all__ = [
    "API_KEY_ROLE_VALUES",
    "CAMERA_CONNECTION_STATUS_VALUES",
    "CAMERA_STATUS_VALUES",
    "EVENT_ATTACHMENT_STATUS_VALUES",
    "EVENT_STATUS_VALUES",
    "EVENT_TYPE_VALUES",
    "MEMBER_ROLE_VALUES",
    "MEMBER_STATUS_VALUES",
    "PROBLEM_TYPES",
    "RATE_LIMIT_WINDOW_VALUES",
    "ApiKeyRole",
    "Camera",
    "CameraConnection",
    "CameraConnectionStatus",
    "CameraRef",
    "CameraScope",
    "CameraStatus",
    "ConflictProblem",
    "CreatePermission",
    "CreatePermissionResult",
    "Event",
    "EventAttachment",
    "EventAttachmentStatus",
    "EventInitiator",
    "EventInitiatorApiKey",
    "EventInitiatorUser",
    "EventPermission",
    "EventPlate",
    "EventRef",
    "EventStatus",
    "EventType",
    "EventVehicle",
    "EventWithAttachments",
    "FailedCamera",
    "ForbiddenProblem",
    "Gate",
    "GateNotOperableProblem",
    "GateRef",
    "GateScope",
    "IdempotencyKeyInFlightProblem",
    "IdempotencyKeyReuseProblem",
    "InternalProblem",
    "InvalidOwnerProblem",
    "InvalidRequestIssue",
    "InvalidRequestProblem",
    "LimitExceededProblem",
    "Location",
    "LocationLimits",
    "Me",
    "Member",
    "MemberRole",
    "MemberStatus",
    "NotFoundProblem",
    "Permission",
    "PermissionRef",
    "Problem",
    "ProvisioningProblem",
    "RateLimit",
    "RateLimitWindow",
    "RateLimitedProblem",
    "ReplacePermission",
    "ServiceUnavailableProblem",
    "UnauthorizedProblem",
    "UnknownEventInitiator",
]
