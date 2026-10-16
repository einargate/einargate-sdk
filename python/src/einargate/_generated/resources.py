# Generated from the Einar Gate OpenAPI document by packages/aws/scripts/sdk
# in the Einar Gate monorepo. Do not edit: change the route registry or the
# generator and run `npm run public-api:lock --workspace @einargate/aws`.

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .._runtime import encode as e
from .._runtime.context import AsyncClientContext, ClientContext
from .._runtime.encode import NOT_GIVEN, NotGiven
from .._runtime.page import MAX_PAGE_SIZE, Page, acollect_pages, collect_pages
from .._runtime.result import Err, Result
from . import models as t
from . import operations as o


class RootResource:
    """The calls that belong to no resource."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def me(self, *, timeout: float | None = None) -> Result[t.Me, o.GetMeError]:
        """The calling API key.

        The API key the calling value belongs to: its roles, the subscription state of
        its location and the configured rate limits. Every authenticated API key may
        call it; check it when a request is answered with ``forbidden``.

        - ``GET /me``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``,
          ``IntegrationGateOperator``
        - Errors: those of every call (``CommonProblem``, ``CallError``)
        """
        return self._context.send(o.GET_ME, timeout=timeout)

    def open_api_document(
        self, *, timeout: float | None = None
    ) -> Result[Mapping[str, object], o.GetOpenApiDocumentError]:
        """This OpenAPI document.

        The OpenAPI 3.1 document of v1. No authentication needed.

        - ``GET /openapi.json``
        - No API key needed
        - Errors: ``internal``, ``rate-limited``, ``service-unavailable``, ``CallError``
        """
        return self._context.send(o.GET_OPEN_API_DOCUMENT, timeout=timeout)


class LocationResource:
    """The API key’s location."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def get(
        self, *, timeout: float | None = None
    ) -> Result[t.Location, o.GetLocationError]:
        """The location.

        The API key’s location: its address, time zone, default plate country, limits,
        subscription state and event retention.

        - ``GET /locations/{locationId}``
        - Roles: ``IntegrationSetupReader``, ``IntegrationEventReader``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.GET_LOCATION, path={"locationId": location.data}, timeout=timeout
        )


class MembersResource:
    """The members and invitees of the API key’s location."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def list(
        self,
        *,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Member], o.ListMembersError]:
        """The location’s members.

        Members and invitees, sorted by name. A permission’s owner is a member whose
        status is ``member``.

        - ``GET /locations/{locationId}/members``
        - Roles: ``IntegrationPermissionReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.LIST_MEMBERS,
            path={"locationId": location.data},
            query={
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    def list_all(
        self, *, timeout: float | None = None
    ) -> Result[tuple[t.Member, ...], o.ListMembersError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        def page(token: str | None) -> Result[Page[t.Member], o.ListMembersError]:
            return self.list(
                timeout=timeout, limit=MAX_PAGE_SIZE, continuation_token=token
            )

        return collect_pages(page)


class GatesResource:
    """The gates of the API key’s location."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def list(
        self,
        *,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Gate], o.ListGatesError]:
        """The location’s gates.

        Sorted by name.

        - ``GET /locations/{locationId}/gates``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``,
          ``IntegrationGateOperator``
        - Errors: ``invalid-request``, those of every call (``CommonProblem``,
          ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.LIST_GATES,
            path={"locationId": location.data},
            query={
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    def list_all(
        self, *, timeout: float | None = None
    ) -> Result[tuple[t.Gate, ...], o.ListGatesError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        def page(token: str | None) -> Result[Page[t.Gate], o.ListGatesError]:
            return self.list(
                timeout=timeout, limit=MAX_PAGE_SIZE, continuation_token=token
            )

        return collect_pages(page)

    def get(
        self, gate: t.Gate | t.GateRef, *, timeout: float | None = None
    ) -> Result[t.Gate, o.GetGateError]:
        """A gate.

        - ``GET /locations/{locationId}/gates/{gateId}``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``,
          ``IntegrationGateOperator``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.GET_GATE,
            path={"locationId": location.data, "gateId": gate.gate_id},
            timeout=timeout,
        )

    def open(
        self,
        gate: t.Gate | t.GateRef,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.Event, o.OpenGateError]:
        """Open a gate.

        Sends the open command to the gate’s control camera and answers the manual
        opening event while it is still pending: its snapshots are requested from the
        gate’s cameras, and ``GET /events/{eventId}`` shows them once they arrive.
        Requires an active subscription. No body. Send an ``Idempotency-Key`` so that a
        retry does not open the gate twice.

        - ``POST /locations/{locationId}/gates/{gateId}/open``
        - Roles: ``IntegrationGateOperator``
        - Errors: ``gate-not-operable``, ``idempotency-key-in-flight``,
          ``idempotency-key-reuse``, ``invalid-request``, ``not-found``, those of every
          call (``CommonProblem``, ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.OPEN_GATE,
            path={"locationId": location.data, "gateId": gate.gate_id},
            idempotency_key=idempotency_key,
            timeout=timeout,
        )


class CamerasResource:
    """The cameras of the API key’s location."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def list(
        self,
        *,
        at: o.ListCamerasScope = "location",
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Camera], o.ListCamerasError]:
        """The cameras of the location, or of one of its gates.

        Every camera registered at a gate of the location, with its connection status.

        - ``GET /locations/{locationId}/cameras`` (``at``: ``"location"``)
        - ``GET /locations/{locationId}/gates/{gateId}/cameras`` (``at``: a ``Gate`` or
          ``GateScope``)
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        if at == "location":
            return self._context.send(
                o.LIST_LOCATION_CAMERAS,
                path={"locationId": location.data},
                query={
                    "limit": e.query_integer(limit),
                    "continuationToken": continuation_token,
                },
                timeout=timeout,
            )
        return self._context.send(
            o.LIST_GATE_CAMERAS,
            path={"locationId": location.data, "gateId": at.gate_id},
            query={
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    def list_all(
        self, *, at: o.ListCamerasScope = "location", timeout: float | None = None
    ) -> Result[tuple[t.Camera, ...], o.ListCamerasError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        def page(token: str | None) -> Result[Page[t.Camera], o.ListCamerasError]:
            return self.list(
                at=at, timeout=timeout, limit=MAX_PAGE_SIZE, continuation_token=token
            )

        return collect_pages(page)

    def get(
        self, camera: t.Camera | t.CameraRef, *, timeout: float | None = None
    ) -> Result[t.Camera, o.GetCameraError]:
        """A camera of a gate.

        - ``GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.GET_CAMERA,
            path={
                "locationId": location.data,
                "gateId": camera.gate_id,
                "cameraId": camera.camera_id,
            },
            timeout=timeout,
        )


class PermissionsResource:
    """The permissions of the API key’s location."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def list(
        self,
        *,
        at: o.ListPermissionsScope = "location",
        owner_user_id: str | None = None,
        active: bool | None = None,
        license_plate: str | None = None,
        license_plate_country: str | None = None,
        search: str | None = None,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Permission], o.ListPermissionsError]:
        """The location’s permissions.

        One item per camera: a plate permitted at a gate with two cameras is listed
        twice. To find a plate’s permissions, filter by ``licensePlate`` (and
        ``licensePlateCountry``) rather than building ids.

        - ``GET /locations/{locationId}/permissions``
        - Roles: ``IntegrationPermissionReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, those of every call (``CommonProblem``,
          ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.LIST_PERMISSIONS,
            path={"locationId": location.data},
            query={
                "gateId": None if at == "location" else at.gate_id,
                "cameraId": getattr(at, "camera_id", None),
                "ownerUserId": owner_user_id,
                "active": e.query_boolean(active),
                "licensePlate": license_plate,
                "licensePlateCountry": license_plate_country,
                "search": search,
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    def list_all(
        self,
        *,
        at: o.ListPermissionsScope = "location",
        owner_user_id: str | None = None,
        active: bool | None = None,
        license_plate: str | None = None,
        license_plate_country: str | None = None,
        search: str | None = None,
        timeout: float | None = None,
    ) -> Result[tuple[t.Permission, ...], o.ListPermissionsError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        def page(
            token: str | None,
        ) -> Result[Page[t.Permission], o.ListPermissionsError]:
            return self.list(
                at=at,
                owner_user_id=owner_user_id,
                active=active,
                license_plate=license_plate,
                license_plate_country=license_plate_country,
                search=search,
                timeout=timeout,
                limit=MAX_PAGE_SIZE,
                continuation_token=token,
            )

        return collect_pages(page)

    def create(
        self,
        *,
        at: o.CreatePermissionScope,
        license_plate: str,
        owner_user_id: str,
        active: bool,
        license_plate_country: str | NotGiven | None = NOT_GIVEN,
        supplemental_info: str | None = None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.CreatePermissionResult, o.CreatePermissionError]:
        """Permit a plate at every camera of the location, at every camera of a gate, or at
        one camera.

        The plate is added camera by camera. The answer is ``201`` when at least one
        camera got it, listing the cameras that did not with a problem each
        (``conflict``: it already has the plate; ``limit-exceeded``: a plate limit would
        be exceeded). When no camera got it, the answer is that problem: ``conflict`` if
        every camera already has the plate, ``limit-exceeded`` otherwise. The owner must
        be a member whose status is ``member`` (``invalid-owner``). Send an
        ``Idempotency-Key`` to retry safely.

        - ``POST /locations/{locationId}/permissions`` (``at``: ``"location"``)
        - ``POST /locations/{locationId}/gates/{gateId}/permissions`` (``at``: a
          ``Gate`` or ``GateScope``)
        - ``POST /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions``
          (``at``: a ``Camera`` or ``CameraScope``)
        - Roles: ``IntegrationPermissionManager``
        - Errors: ``conflict``, ``idempotency-key-in-flight``,
          ``idempotency-key-reuse``, ``invalid-owner``, ``invalid-request``,
          ``limit-exceeded``, ``not-found``, those of every call (``CommonProblem``,
          ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        body = t.encode_create_permission(
            t.CreatePermission(
                license_plate=license_plate,
                license_plate_country=license_plate_country,
                owner_user_id=owner_user_id,
                active=active,
                supplemental_info=supplemental_info,
            )
        )
        if at == "location":
            return self._context.send(
                o.CREATE_LOCATION_PERMISSION,
                path={"locationId": location.data},
                body=body,
                idempotency_key=idempotency_key,
                timeout=timeout,
            )
        if isinstance(at, (t.Camera, t.CameraScope)):
            return self._context.send(
                o.CREATE_CAMERA_PERMISSION,
                path={
                    "locationId": location.data,
                    "gateId": at.gate_id,
                    "cameraId": at.camera_id,
                },
                body=body,
                idempotency_key=idempotency_key,
                timeout=timeout,
            )
        return self._context.send(
            o.CREATE_GATE_PERMISSION,
            path={"locationId": location.data, "gateId": at.gate_id},
            body=body,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )

    def get(
        self,
        permission: t.Permission | t.PermissionRef,
        *,
        timeout: float | None = None,
    ) -> Result[t.Permission, o.GetPermissionError]:
        """A permission of a camera.

        - ``GET
          /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}``
        - Roles: ``IntegrationPermissionReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.GET_PERMISSION,
            path={
                "locationId": location.data,
                "gateId": permission.gate_id,
                "cameraId": permission.camera_id,
                "permissionId": permission.permission_id,
            },
            timeout=timeout,
        )

    def replace(
        self,
        permission: t.Permission | t.PermissionRef,
        *,
        license_plate: str,
        license_plate_country: str | None,
        active: bool,
        supplemental_info: str | None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.Permission, o.ReplacePermissionError]:
        """Replace a permission of a camera.

        Send the full representation: a field that is not given is removed. Changing the
        plate or country changes the ``permissionId``; the response carries the new one.
        The owner cannot be changed: remove the permission and create it for the new
        owner.

        - ``PUT
          /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}``
        - Roles: ``IntegrationPermissionManager``
        - Errors: ``conflict``, ``idempotency-key-in-flight``,
          ``idempotency-key-reuse``, ``invalid-request``, ``not-found``, those of every
          call (``CommonProblem``, ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        body = t.encode_replace_permission(
            t.ReplacePermission(
                license_plate=license_plate,
                license_plate_country=license_plate_country,
                active=active,
                supplemental_info=supplemental_info,
            )
        )
        return self._context.send(
            o.REPLACE_PERMISSION,
            path={
                "locationId": location.data,
                "gateId": permission.gate_id,
                "cameraId": permission.camera_id,
                "permissionId": permission.permission_id,
            },
            body=body,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )

    def delete(
        self,
        permission: t.Permission | t.PermissionRef,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[None, o.DeletePermissionError]:
        """Remove a permission from a camera.

        - ``DELETE
          /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}``
        - Roles: ``IntegrationPermissionManager``
        - Errors: ``idempotency-key-in-flight``, ``idempotency-key-reuse``,
          ``invalid-request``, ``not-found``, those of every call (``CommonProblem``,
          ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.DELETE_PERMISSION,
            path={
                "locationId": location.data,
                "gateId": permission.gate_id,
                "cameraId": permission.camera_id,
                "permissionId": permission.permission_id,
            },
            idempotency_key=idempotency_key,
            timeout=timeout,
        )


class EventsResource:
    """The events of the API key’s location."""

    def __init__(self, context: ClientContext) -> None:
        self._context = context

    def list(
        self,
        *,
        from_: datetime | None = None,
        to: datetime | None = None,
        gate_id: str | None = None,
        camera_id: str | None = None,
        type: t.EventType | None = None,
        license_plate: str | None = None,
        min_fraud_risk_percentage: int | None = None,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Event], o.ListEventsError]:
        """The location’s gate openings.

        Oldest first, within the location’s event retention. To follow new events, pass
        the last event time seen as ``from``. The list carries no images: get an event
        for its attachments.

        - ``GET /locations/{locationId}/events``
        - Roles: ``IntegrationEventReader``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.LIST_EVENTS,
            path={"locationId": location.data},
            query={
                "from": e.query_timestamp(from_, "from_"),
                "to": e.query_timestamp(to, "to"),
                "gateId": gate_id,
                "cameraId": camera_id,
                "type": e.query_enum(type),
                "licensePlate": license_plate,
                "minFraudRiskPercentage": e.query_integer(min_fraud_risk_percentage),
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    def list_all(
        self,
        *,
        from_: datetime | None = None,
        to: datetime | None = None,
        gate_id: str | None = None,
        camera_id: str | None = None,
        type: t.EventType | None = None,
        license_plate: str | None = None,
        min_fraud_risk_percentage: int | None = None,
        timeout: float | None = None,
    ) -> Result[tuple[t.Event, ...], o.ListEventsError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        def page(token: str | None) -> Result[Page[t.Event], o.ListEventsError]:
            return self.list(
                from_=from_,
                to=to,
                gate_id=gate_id,
                camera_id=camera_id,
                type=type,
                license_plate=license_plate,
                min_fraud_risk_percentage=min_fraud_risk_percentage,
                timeout=timeout,
                limit=MAX_PAGE_SIZE,
                continuation_token=token,
            )

        return collect_pages(page)

    def get(
        self,
        event: t.Event | t.EventWithAttachments | t.EventRef,
        *,
        timeout: float | None = None,
    ) -> Result[t.EventWithAttachments, o.GetEventError]:
        """A gate opening with its images.

        The attachments’ URLs are presigned and valid for 15 minutes; get the event
        again for fresh ones.

        - ``GET /locations/{locationId}/events/{eventId}``
        - Roles: ``IntegrationEventReader``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return self._context.send(
            o.GET_EVENT,
            path={"locationId": location.data, "eventId": event.event_id},
            timeout=timeout,
        )


class AsyncRootResource:
    """The calls that belong to no resource."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def me(self, *, timeout: float | None = None) -> Result[t.Me, o.GetMeError]:
        """The calling API key.

        The API key the calling value belongs to: its roles, the subscription state of
        its location and the configured rate limits. Every authenticated API key may
        call it; check it when a request is answered with ``forbidden``.

        - ``GET /me``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``,
          ``IntegrationGateOperator``
        - Errors: those of every call (``CommonProblem``, ``CallError``)
        """
        return await self._context.send(o.GET_ME, timeout=timeout)

    async def open_api_document(
        self, *, timeout: float | None = None
    ) -> Result[Mapping[str, object], o.GetOpenApiDocumentError]:
        """This OpenAPI document.

        The OpenAPI 3.1 document of v1. No authentication needed.

        - ``GET /openapi.json``
        - No API key needed
        - Errors: ``internal``, ``rate-limited``, ``service-unavailable``, ``CallError``
        """
        return await self._context.send(o.GET_OPEN_API_DOCUMENT, timeout=timeout)


class AsyncLocationResource:
    """The API key’s location."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def get(
        self, *, timeout: float | None = None
    ) -> Result[t.Location, o.GetLocationError]:
        """The location.

        The API key’s location: its address, time zone, default plate country, limits,
        subscription state and event retention.

        - ``GET /locations/{locationId}``
        - Roles: ``IntegrationSetupReader``, ``IntegrationEventReader``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.GET_LOCATION, path={"locationId": location.data}, timeout=timeout
        )


class AsyncMembersResource:
    """The members and invitees of the API key’s location."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def list(
        self,
        *,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Member], o.ListMembersError]:
        """The location’s members.

        Members and invitees, sorted by name. A permission’s owner is a member whose
        status is ``member``.

        - ``GET /locations/{locationId}/members``
        - Roles: ``IntegrationPermissionReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.LIST_MEMBERS,
            path={"locationId": location.data},
            query={
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    async def list_all(
        self, *, timeout: float | None = None
    ) -> Result[tuple[t.Member, ...], o.ListMembersError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        async def page(token: str | None) -> Result[Page[t.Member], o.ListMembersError]:
            return await self.list(
                timeout=timeout, limit=MAX_PAGE_SIZE, continuation_token=token
            )

        return await acollect_pages(page)


class AsyncGatesResource:
    """The gates of the API key’s location."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def list(
        self,
        *,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Gate], o.ListGatesError]:
        """The location’s gates.

        Sorted by name.

        - ``GET /locations/{locationId}/gates``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``,
          ``IntegrationGateOperator``
        - Errors: ``invalid-request``, those of every call (``CommonProblem``,
          ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.LIST_GATES,
            path={"locationId": location.data},
            query={
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    async def list_all(
        self, *, timeout: float | None = None
    ) -> Result[tuple[t.Gate, ...], o.ListGatesError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        async def page(token: str | None) -> Result[Page[t.Gate], o.ListGatesError]:
            return await self.list(
                timeout=timeout, limit=MAX_PAGE_SIZE, continuation_token=token
            )

        return await acollect_pages(page)

    async def get(
        self, gate: t.Gate | t.GateRef, *, timeout: float | None = None
    ) -> Result[t.Gate, o.GetGateError]:
        """A gate.

        - ``GET /locations/{locationId}/gates/{gateId}``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``,
          ``IntegrationGateOperator``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.GET_GATE,
            path={"locationId": location.data, "gateId": gate.gate_id},
            timeout=timeout,
        )

    async def open(
        self,
        gate: t.Gate | t.GateRef,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.Event, o.OpenGateError]:
        """Open a gate.

        Sends the open command to the gate’s control camera and answers the manual
        opening event while it is still pending: its snapshots are requested from the
        gate’s cameras, and ``GET /events/{eventId}`` shows them once they arrive.
        Requires an active subscription. No body. Send an ``Idempotency-Key`` so that a
        retry does not open the gate twice.

        - ``POST /locations/{locationId}/gates/{gateId}/open``
        - Roles: ``IntegrationGateOperator``
        - Errors: ``gate-not-operable``, ``idempotency-key-in-flight``,
          ``idempotency-key-reuse``, ``invalid-request``, ``not-found``, those of every
          call (``CommonProblem``, ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.OPEN_GATE,
            path={"locationId": location.data, "gateId": gate.gate_id},
            idempotency_key=idempotency_key,
            timeout=timeout,
        )


class AsyncCamerasResource:
    """The cameras of the API key’s location."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def list(
        self,
        *,
        at: o.ListCamerasScope = "location",
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Camera], o.ListCamerasError]:
        """The cameras of the location, or of one of its gates.

        Every camera registered at a gate of the location, with its connection status.

        - ``GET /locations/{locationId}/cameras`` (``at``: ``"location"``)
        - ``GET /locations/{locationId}/gates/{gateId}/cameras`` (``at``: a ``Gate`` or
          ``GateScope``)
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        if at == "location":
            return await self._context.send(
                o.LIST_LOCATION_CAMERAS,
                path={"locationId": location.data},
                query={
                    "limit": e.query_integer(limit),
                    "continuationToken": continuation_token,
                },
                timeout=timeout,
            )
        return await self._context.send(
            o.LIST_GATE_CAMERAS,
            path={"locationId": location.data, "gateId": at.gate_id},
            query={
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    async def list_all(
        self, *, at: o.ListCamerasScope = "location", timeout: float | None = None
    ) -> Result[tuple[t.Camera, ...], o.ListCamerasError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        async def page(token: str | None) -> Result[Page[t.Camera], o.ListCamerasError]:
            return await self.list(
                at=at, timeout=timeout, limit=MAX_PAGE_SIZE, continuation_token=token
            )

        return await acollect_pages(page)

    async def get(
        self, camera: t.Camera | t.CameraRef, *, timeout: float | None = None
    ) -> Result[t.Camera, o.GetCameraError]:
        """A camera of a gate.

        - ``GET /locations/{locationId}/gates/{gateId}/cameras/{cameraId}``
        - Roles: ``IntegrationSetupReader``, ``IntegrationPermissionReader``,
          ``IntegrationEventReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.GET_CAMERA,
            path={
                "locationId": location.data,
                "gateId": camera.gate_id,
                "cameraId": camera.camera_id,
            },
            timeout=timeout,
        )


class AsyncPermissionsResource:
    """The permissions of the API key’s location."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def list(
        self,
        *,
        at: o.ListPermissionsScope = "location",
        owner_user_id: str | None = None,
        active: bool | None = None,
        license_plate: str | None = None,
        license_plate_country: str | None = None,
        search: str | None = None,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Permission], o.ListPermissionsError]:
        """The location’s permissions.

        One item per camera: a plate permitted at a gate with two cameras is listed
        twice. To find a plate’s permissions, filter by ``licensePlate`` (and
        ``licensePlateCountry``) rather than building ids.

        - ``GET /locations/{locationId}/permissions``
        - Roles: ``IntegrationPermissionReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, those of every call (``CommonProblem``,
          ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.LIST_PERMISSIONS,
            path={"locationId": location.data},
            query={
                "gateId": None if at == "location" else at.gate_id,
                "cameraId": getattr(at, "camera_id", None),
                "ownerUserId": owner_user_id,
                "active": e.query_boolean(active),
                "licensePlate": license_plate,
                "licensePlateCountry": license_plate_country,
                "search": search,
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    async def list_all(
        self,
        *,
        at: o.ListPermissionsScope = "location",
        owner_user_id: str | None = None,
        active: bool | None = None,
        license_plate: str | None = None,
        license_plate_country: str | None = None,
        search: str | None = None,
        timeout: float | None = None,
    ) -> Result[tuple[t.Permission, ...], o.ListPermissionsError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        async def page(
            token: str | None,
        ) -> Result[Page[t.Permission], o.ListPermissionsError]:
            return await self.list(
                at=at,
                owner_user_id=owner_user_id,
                active=active,
                license_plate=license_plate,
                license_plate_country=license_plate_country,
                search=search,
                timeout=timeout,
                limit=MAX_PAGE_SIZE,
                continuation_token=token,
            )

        return await acollect_pages(page)

    async def create(
        self,
        *,
        at: o.CreatePermissionScope,
        license_plate: str,
        owner_user_id: str,
        active: bool,
        license_plate_country: str | NotGiven | None = NOT_GIVEN,
        supplemental_info: str | None = None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.CreatePermissionResult, o.CreatePermissionError]:
        """Permit a plate at every camera of the location, at every camera of a gate, or at
        one camera.

        The plate is added camera by camera. The answer is ``201`` when at least one
        camera got it, listing the cameras that did not with a problem each
        (``conflict``: it already has the plate; ``limit-exceeded``: a plate limit would
        be exceeded). When no camera got it, the answer is that problem: ``conflict`` if
        every camera already has the plate, ``limit-exceeded`` otherwise. The owner must
        be a member whose status is ``member`` (``invalid-owner``). Send an
        ``Idempotency-Key`` to retry safely.

        - ``POST /locations/{locationId}/permissions`` (``at``: ``"location"``)
        - ``POST /locations/{locationId}/gates/{gateId}/permissions`` (``at``: a
          ``Gate`` or ``GateScope``)
        - ``POST /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions``
          (``at``: a ``Camera`` or ``CameraScope``)
        - Roles: ``IntegrationPermissionManager``
        - Errors: ``conflict``, ``idempotency-key-in-flight``,
          ``idempotency-key-reuse``, ``invalid-owner``, ``invalid-request``,
          ``limit-exceeded``, ``not-found``, those of every call (``CommonProblem``,
          ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        body = t.encode_create_permission(
            t.CreatePermission(
                license_plate=license_plate,
                license_plate_country=license_plate_country,
                owner_user_id=owner_user_id,
                active=active,
                supplemental_info=supplemental_info,
            )
        )
        if at == "location":
            return await self._context.send(
                o.CREATE_LOCATION_PERMISSION,
                path={"locationId": location.data},
                body=body,
                idempotency_key=idempotency_key,
                timeout=timeout,
            )
        if isinstance(at, (t.Camera, t.CameraScope)):
            return await self._context.send(
                o.CREATE_CAMERA_PERMISSION,
                path={
                    "locationId": location.data,
                    "gateId": at.gate_id,
                    "cameraId": at.camera_id,
                },
                body=body,
                idempotency_key=idempotency_key,
                timeout=timeout,
            )
        return await self._context.send(
            o.CREATE_GATE_PERMISSION,
            path={"locationId": location.data, "gateId": at.gate_id},
            body=body,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )

    async def get(
        self,
        permission: t.Permission | t.PermissionRef,
        *,
        timeout: float | None = None,
    ) -> Result[t.Permission, o.GetPermissionError]:
        """A permission of a camera.

        - ``GET
          /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}``
        - Roles: ``IntegrationPermissionReader``, ``IntegrationPermissionManager``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.GET_PERMISSION,
            path={
                "locationId": location.data,
                "gateId": permission.gate_id,
                "cameraId": permission.camera_id,
                "permissionId": permission.permission_id,
            },
            timeout=timeout,
        )

    async def replace(
        self,
        permission: t.Permission | t.PermissionRef,
        *,
        license_plate: str,
        license_plate_country: str | None,
        active: bool,
        supplemental_info: str | None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.Permission, o.ReplacePermissionError]:
        """Replace a permission of a camera.

        Send the full representation: a field that is not given is removed. Changing the
        plate or country changes the ``permissionId``; the response carries the new one.
        The owner cannot be changed: remove the permission and create it for the new
        owner.

        - ``PUT
          /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}``
        - Roles: ``IntegrationPermissionManager``
        - Errors: ``conflict``, ``idempotency-key-in-flight``,
          ``idempotency-key-reuse``, ``invalid-request``, ``not-found``, those of every
          call (``CommonProblem``, ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        body = t.encode_replace_permission(
            t.ReplacePermission(
                license_plate=license_plate,
                license_plate_country=license_plate_country,
                active=active,
                supplemental_info=supplemental_info,
            )
        )
        return await self._context.send(
            o.REPLACE_PERMISSION,
            path={
                "locationId": location.data,
                "gateId": permission.gate_id,
                "cameraId": permission.camera_id,
                "permissionId": permission.permission_id,
            },
            body=body,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )

    async def delete(
        self,
        permission: t.Permission | t.PermissionRef,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[None, o.DeletePermissionError]:
        """Remove a permission from a camera.

        - ``DELETE
          /locations/{locationId}/gates/{gateId}/cameras/{cameraId}/permissions/{permissionId}``
        - Roles: ``IntegrationPermissionManager``
        - Errors: ``idempotency-key-in-flight``, ``idempotency-key-reuse``,
          ``invalid-request``, ``not-found``, those of every call (``CommonProblem``,
          ``CallError``)
        - Idempotent: an ``Idempotency-Key`` is sent, so retries are safe; pass
          ``idempotency_key`` to choose it
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.DELETE_PERMISSION,
            path={
                "locationId": location.data,
                "gateId": permission.gate_id,
                "cameraId": permission.camera_id,
                "permissionId": permission.permission_id,
            },
            idempotency_key=idempotency_key,
            timeout=timeout,
        )


class AsyncEventsResource:
    """The events of the API key’s location."""

    def __init__(self, context: AsyncClientContext) -> None:
        self._context = context

    async def list(
        self,
        *,
        from_: datetime | None = None,
        to: datetime | None = None,
        gate_id: str | None = None,
        camera_id: str | None = None,
        type: t.EventType | None = None,
        license_plate: str | None = None,
        min_fraud_risk_percentage: int | None = None,
        limit: int | None = None,
        continuation_token: str | None = None,
        timeout: float | None = None,
    ) -> Result[Page[t.Event], o.ListEventsError]:
        """The location’s gate openings.

        Oldest first, within the location’s event retention. To follow new events, pass
        the last event time seen as ``from``. The list carries no images: get an event
        for its attachments.

        - ``GET /locations/{locationId}/events``
        - Roles: ``IntegrationEventReader``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.LIST_EVENTS,
            path={"locationId": location.data},
            query={
                "from": e.query_timestamp(from_, "from_"),
                "to": e.query_timestamp(to, "to"),
                "gateId": gate_id,
                "cameraId": camera_id,
                "type": e.query_enum(type),
                "licensePlate": license_plate,
                "minFraudRiskPercentage": e.query_integer(min_fraud_risk_percentage),
                "limit": e.query_integer(limit),
                "continuationToken": continuation_token,
            },
            timeout=timeout,
        )

    async def list_all(
        self,
        *,
        from_: datetime | None = None,
        to: datetime | None = None,
        gate_id: str | None = None,
        camera_id: str | None = None,
        type: t.EventType | None = None,
        license_plate: str | None = None,
        min_fraud_risk_percentage: int | None = None,
        timeout: float | None = None,
    ) -> Result[tuple[t.Event, ...], o.ListEventsError]:
        """Every page of ``list``, as one tuple: fetches pages of 200 items until the last
        one. The first failure ends it.
        """

        async def page(token: str | None) -> Result[Page[t.Event], o.ListEventsError]:
            return await self.list(
                from_=from_,
                to=to,
                gate_id=gate_id,
                camera_id=camera_id,
                type=type,
                license_plate=license_plate,
                min_fraud_risk_percentage=min_fraud_risk_percentage,
                timeout=timeout,
                limit=MAX_PAGE_SIZE,
                continuation_token=token,
            )

        return await acollect_pages(page)

    async def get(
        self,
        event: t.Event | t.EventWithAttachments | t.EventRef,
        *,
        timeout: float | None = None,
    ) -> Result[t.EventWithAttachments, o.GetEventError]:
        """A gate opening with its images.

        The attachments’ URLs are presigned and valid for 15 minutes; get the event
        again for fresh ones.

        - ``GET /locations/{locationId}/events/{eventId}``
        - Roles: ``IntegrationEventReader``
        - Errors: ``invalid-request``, ``not-found``, those of every call
          (``CommonProblem``, ``CallError``)
        """
        location = await self._context.location_id(timeout)
        if isinstance(location, Err):
            return location
        return await self._context.send(
            o.GET_EVENT,
            path={"locationId": location.data, "eventId": event.event_id},
            timeout=timeout,
        )
