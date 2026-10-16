# Generated from the Einar Gate OpenAPI document by packages/aws/scripts/sdk
# in the Einar Gate monorepo. Do not edit: change the route registry or the
# generator and run `npm run public-api:lock --workspace @einargate/aws`.

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeAlias, Union

from .._runtime import decode as d
from .._runtime.errors import CallError
from .._runtime.page import Page
from .._runtime.transport import OperationSpec
from . import models as t

# region Operations

GET_ME: OperationSpec[t.Me] = OperationSpec(
    id="getMe",
    method="GET",
    path="/me",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.decode_me,
    encode=t.encode_me,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

GET_OPEN_API_DOCUMENT: OperationSpec[Mapping[str, object]] = OperationSpec(
    id="getOpenApiDocument",
    method="GET",
    path="/openapi.json",
    status=200,
    authenticated=False,
    idempotent=False,
    decode=d.json_object,
    encode=lambda v: v,
    problems={
        "internal": t.decode_internal_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
    },
)

GET_LOCATION: OperationSpec[t.Location] = OperationSpec(
    id="getLocation",
    method="GET",
    path="/locations/{locationId}",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.decode_location,
    encode=t.encode_location,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

LIST_MEMBERS: OperationSpec[Page[t.Member]] = OperationSpec(
    id="listMembers",
    method="GET",
    path="/locations/{locationId}/members",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.page_decoder(t.decode_member),
    encode=lambda v: t.encode_page(v, t.encode_member),
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

LIST_GATES: OperationSpec[Page[t.Gate]] = OperationSpec(
    id="listGates",
    method="GET",
    path="/locations/{locationId}/gates",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.page_decoder(t.decode_gate),
    encode=lambda v: t.encode_page(v, t.encode_gate),
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

GET_GATE: OperationSpec[t.Gate] = OperationSpec(
    id="getGate",
    method="GET",
    path="/locations/{locationId}/gates/{gateId}",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.decode_gate,
    encode=t.encode_gate,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

OPEN_GATE: OperationSpec[t.Event] = OperationSpec(
    id="openGate",
    method="POST",
    path="/locations/{locationId}/gates/{gateId}/open",
    status=202,
    authenticated=True,
    idempotent=True,
    decode=t.decode_event,
    encode=t.encode_event,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "gate-not-operable": t.decode_gate_not_operable_problem,
        "idempotency-key-in-flight": t.decode_idempotency_key_in_flight_problem,
        "idempotency-key-reuse": t.decode_idempotency_key_reuse_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

LIST_LOCATION_CAMERAS: OperationSpec[Page[t.Camera]] = OperationSpec(
    id="listLocationCameras",
    method="GET",
    path="/locations/{locationId}/cameras",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.page_decoder(t.decode_camera),
    encode=lambda v: t.encode_page(v, t.encode_camera),
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

LIST_GATE_CAMERAS: OperationSpec[Page[t.Camera]] = OperationSpec(
    id="listGateCameras",
    method="GET",
    path="/locations/{locationId}/gates/{gateId}/cameras",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.page_decoder(t.decode_camera),
    encode=lambda v: t.encode_page(v, t.encode_camera),
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

GET_CAMERA: OperationSpec[t.Camera] = OperationSpec(
    id="getCamera",
    method="GET",
    path="/locations/{locationId}/gates/{gateId}/cameras/{cameraId}",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.decode_camera,
    encode=t.encode_camera,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

LIST_PERMISSIONS: OperationSpec[Page[t.Permission]] = OperationSpec(
    id="listPermissions",
    method="GET",
    path="/locations/{locationId}/permissions",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.page_decoder(t.decode_permission),
    encode=lambda v: t.encode_page(v, t.encode_permission),
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

CREATE_LOCATION_PERMISSION: OperationSpec[t.CreatePermissionResult] = OperationSpec(
    id="createLocationPermission",
    method="POST",
    path="/locations/{locationId}/permissions",
    status=201,
    authenticated=True,
    idempotent=True,
    decode=t.decode_create_permission_result,
    encode=t.encode_create_permission_result,
    problems={
        "conflict": t.decode_conflict_problem,
        "forbidden": t.decode_forbidden_problem,
        "idempotency-key-in-flight": t.decode_idempotency_key_in_flight_problem,
        "idempotency-key-reuse": t.decode_idempotency_key_reuse_problem,
        "internal": t.decode_internal_problem,
        "invalid-owner": t.decode_invalid_owner_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "limit-exceeded": t.decode_limit_exceeded_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

CREATE_GATE_PERMISSION: OperationSpec[t.CreatePermissionResult] = OperationSpec(
    id="createGatePermission",
    method="POST",
    path="/locations/{locationId}/gates/{gateId}/permissions",
    status=201,
    authenticated=True,
    idempotent=True,
    decode=t.decode_create_permission_result,
    encode=t.encode_create_permission_result,
    problems={
        "conflict": t.decode_conflict_problem,
        "forbidden": t.decode_forbidden_problem,
        "idempotency-key-in-flight": t.decode_idempotency_key_in_flight_problem,
        "idempotency-key-reuse": t.decode_idempotency_key_reuse_problem,
        "internal": t.decode_internal_problem,
        "invalid-owner": t.decode_invalid_owner_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "limit-exceeded": t.decode_limit_exceeded_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

CREATE_CAMERA_PERMISSION: OperationSpec[t.CreatePermissionResult] = OperationSpec(
    id="createCameraPermission",
    method="POST",
    path="/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions",
    status=201,
    authenticated=True,
    idempotent=True,
    decode=t.decode_create_permission_result,
    encode=t.encode_create_permission_result,
    problems={
        "conflict": t.decode_conflict_problem,
        "forbidden": t.decode_forbidden_problem,
        "idempotency-key-in-flight": t.decode_idempotency_key_in_flight_problem,
        "idempotency-key-reuse": t.decode_idempotency_key_reuse_problem,
        "internal": t.decode_internal_problem,
        "invalid-owner": t.decode_invalid_owner_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "limit-exceeded": t.decode_limit_exceeded_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

GET_PERMISSION: OperationSpec[t.Permission] = OperationSpec(
    id="getPermission",
    method="GET",
    path="/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.decode_permission,
    encode=t.encode_permission,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

REPLACE_PERMISSION: OperationSpec[t.Permission] = OperationSpec(
    id="replacePermission",
    method="PUT",
    path="/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}",
    status=200,
    authenticated=True,
    idempotent=True,
    decode=t.decode_permission,
    encode=t.encode_permission,
    problems={
        "conflict": t.decode_conflict_problem,
        "forbidden": t.decode_forbidden_problem,
        "idempotency-key-in-flight": t.decode_idempotency_key_in_flight_problem,
        "idempotency-key-reuse": t.decode_idempotency_key_reuse_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

DELETE_PERMISSION: OperationSpec[None] = OperationSpec(
    id="deletePermission",
    method="DELETE",
    path="/locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}",
    status=204,
    authenticated=True,
    idempotent=True,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "idempotency-key-in-flight": t.decode_idempotency_key_in_flight_problem,
        "idempotency-key-reuse": t.decode_idempotency_key_reuse_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

LIST_EVENTS: OperationSpec[Page[t.Event]] = OperationSpec(
    id="listEvents",
    method="GET",
    path="/locations/{locationId}/events",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.page_decoder(t.decode_event),
    encode=lambda v: t.encode_page(v, t.encode_event),
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

GET_EVENT: OperationSpec[t.EventWithAttachments] = OperationSpec(
    id="getEvent",
    method="GET",
    path="/locations/{locationId}/events/{eventId}",
    status=200,
    authenticated=True,
    idempotent=False,
    decode=t.decode_event_with_attachments,
    encode=t.encode_event_with_attachments,
    problems={
        "forbidden": t.decode_forbidden_problem,
        "internal": t.decode_internal_problem,
        "invalid-request": t.decode_invalid_request_problem,
        "not-found": t.decode_not_found_problem,
        "provisioning": t.decode_provisioning_problem,
        "rate-limited": t.decode_rate_limited_problem,
        "service-unavailable": t.decode_service_unavailable_problem,
        "unauthorized": t.decode_unauthorized_problem,
    },
)

OPERATIONS: Mapping[str, OperationSpec[Any]] = {
    "get_me": GET_ME,
    "get_open_api_document": GET_OPEN_API_DOCUMENT,
    "get_location": GET_LOCATION,
    "list_members": LIST_MEMBERS,
    "list_gates": LIST_GATES,
    "get_gate": GET_GATE,
    "open_gate": OPEN_GATE,
    "list_location_cameras": LIST_LOCATION_CAMERAS,
    "list_gate_cameras": LIST_GATE_CAMERAS,
    "get_camera": GET_CAMERA,
    "list_permissions": LIST_PERMISSIONS,
    "create_location_permission": CREATE_LOCATION_PERMISSION,
    "create_gate_permission": CREATE_GATE_PERMISSION,
    "create_camera_permission": CREATE_CAMERA_PERMISSION,
    "get_permission": GET_PERMISSION,
    "replace_permission": REPLACE_PERMISSION,
    "delete_permission": DELETE_PERMISSION,
    "list_events": LIST_EVENTS,
    "get_event": GET_EVENT,
}
"""Every operation, by the snake_case form of its OpenAPI operation id"""

# endregion Operations
# region Errors

CommonProblem: TypeAlias = Union[
    t.ForbiddenProblem,
    t.InternalProblem,
    t.ProvisioningProblem,
    t.RateLimitedProblem,
    t.ServiceUnavailableProblem,
    t.UnauthorizedProblem,
]
"""The problem types every authenticated call can return, besides its own"""

GetMeError: TypeAlias = Union[CommonProblem, CallError]
"""The errors ``me`` can return"""

GetOpenApiDocumentError: TypeAlias = Union[
    t.InternalProblem, t.RateLimitedProblem, t.ServiceUnavailableProblem, CallError
]
"""The errors ``open_api_document`` can return"""

GetLocationError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``location.get`` can return"""

ListMembersError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``members.list`` can return"""

ListGatesError: TypeAlias = Union[t.InvalidRequestProblem, CommonProblem, CallError]
"""The errors ``gates.list`` can return"""

GetGateError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``gates.get`` can return"""

OpenGateError: TypeAlias = Union[
    t.GateNotOperableProblem,
    t.IdempotencyKeyInFlightProblem,
    t.IdempotencyKeyReuseProblem,
    t.InvalidRequestProblem,
    t.NotFoundProblem,
    CommonProblem,
    CallError,
]
"""The errors ``gates.open`` can return"""

ListCamerasError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``cameras.list`` can return"""

GetCameraError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``cameras.get`` can return"""

ListPermissionsError: TypeAlias = Union[
    t.InvalidRequestProblem, CommonProblem, CallError
]
"""The errors ``permissions.list`` can return"""

CreatePermissionError: TypeAlias = Union[
    t.ConflictProblem,
    t.IdempotencyKeyInFlightProblem,
    t.IdempotencyKeyReuseProblem,
    t.InvalidOwnerProblem,
    t.InvalidRequestProblem,
    t.LimitExceededProblem,
    t.NotFoundProblem,
    CommonProblem,
    CallError,
]
"""The errors ``permissions.create`` can return"""

GetPermissionError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``permissions.get`` can return"""

ReplacePermissionError: TypeAlias = Union[
    t.ConflictProblem,
    t.IdempotencyKeyInFlightProblem,
    t.IdempotencyKeyReuseProblem,
    t.InvalidRequestProblem,
    t.NotFoundProblem,
    CommonProblem,
    CallError,
]
"""The errors ``permissions.replace`` can return"""

DeletePermissionError: TypeAlias = Union[
    t.IdempotencyKeyInFlightProblem,
    t.IdempotencyKeyReuseProblem,
    t.InvalidRequestProblem,
    t.NotFoundProblem,
    CommonProblem,
    CallError,
]
"""The errors ``permissions.delete`` can return"""

ListEventsError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``events.list`` can return"""

GetEventError: TypeAlias = Union[
    t.InvalidRequestProblem, t.NotFoundProblem, CommonProblem, CallError
]
"""The errors ``events.get`` can return"""

# endregion Errors
# region Scopes

ListCamerasScope: TypeAlias = Union[Literal["location"], t.Gate, t.GateScope]
"""Where ``cameras.list`` acts: ``"location"``, a gate or a camera"""

ListPermissionsScope: TypeAlias = Union[
    Literal["location"], t.Gate, t.GateScope, t.Camera, t.CameraScope
]
"""Where ``permissions.list`` acts: ``"location"``, a gate or a camera"""

CreatePermissionScope: TypeAlias = Union[
    Literal["location"], t.Gate, t.GateScope, t.Camera, t.CameraScope
]
"""Where ``permissions.create`` acts: ``"location"``, a gate or a camera"""

# endregion Scopes

OperationName: TypeAlias = Literal[
    "get_me",
    "get_open_api_document",
    "get_location",
    "list_members",
    "list_gates",
    "get_gate",
    "open_gate",
    "list_location_cameras",
    "list_gate_cameras",
    "get_camera",
    "list_permissions",
    "create_location_permission",
    "create_gate_permission",
    "create_camera_permission",
    "get_permission",
    "replace_permission",
    "delete_permission",
    "list_events",
    "get_event",
]
"""An operation, by the snake_case form of its OpenAPI operation id"""

__all__ = [
    "OPERATIONS",
    "CommonProblem",
    "CreatePermissionError",
    "CreatePermissionScope",
    "DeletePermissionError",
    "GetCameraError",
    "GetEventError",
    "GetGateError",
    "GetLocationError",
    "GetMeError",
    "GetOpenApiDocumentError",
    "GetPermissionError",
    "ListCamerasError",
    "ListCamerasScope",
    "ListEventsError",
    "ListGatesError",
    "ListMembersError",
    "ListPermissionsError",
    "ListPermissionsScope",
    "OpenGateError",
    "OperationName",
    "ReplacePermissionError",
]
