"""Methods for the recipes where the API has a trap (ADR-0022)."""

from __future__ import annotations

import asyncio
import contextvars
import threading
import time
from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, TypeVar

from ._generated import models as t
from ._generated import operations as o
from ._generated.resources import AsyncEventsResource as _AsyncEvents
from ._generated.resources import AsyncPermissionsResource as _AsyncPermissions
from ._generated.resources import EventsResource as _Events
from ._generated.resources import PermissionsResource as _Permissions
from ._runtime.encode import NOT_GIVEN, NotGiven
from ._runtime.result import Err, Ok, Result
from ._runtime.transport import Deadline, deadline

R = TypeVar("R")

CARRIED_FIELDS = (
    "license_plate",
    "license_plate_country",
    "active",
    "supplemental_info",
)
"""The fields ``update`` carries over from the permission. A test fails when
``ReplacePermission`` gains one, so that ``update`` cannot remove it by leaving
it out."""


@dataclass(frozen=True, slots=True, kw_only=True)
class WaitTimeout:
    """``wait_for_attachments`` gave up; ``event`` is the event as last seen."""

    type: Literal["wait-timeout"] = "wait-timeout"
    message: str
    event: t.EventWithAttachments | None = None
    """The event as last seen, if a poll answered in time"""

    def __str__(self) -> str:
        return self.message


def _replacement(
    permission: t.Permission,
    license_plate: str | NotGiven,
    license_plate_country: str | NotGiven | None,
    active: bool | NotGiven,
    supplemental_info: str | NotGiven | None,
) -> t.ReplacePermission:
    return t.ReplacePermission(
        license_plate=permission.license_plate
        if isinstance(license_plate, NotGiven)
        else license_plate,
        license_plate_country=permission.license_plate_country
        if isinstance(license_plate_country, NotGiven)
        else license_plate_country,
        active=permission.active if isinstance(active, NotGiven) else active,
        supplemental_info=permission.supplemental_info
        if isinstance(supplemental_info, NotGiven)
        else supplemental_info,
    )


def _poll(get: Callable[[], R], scope: Deadline) -> R | None:
    """The poll's result, or ``None`` when the deadline came first; its read
    is then closed, and its daemon worker cannot keep the process alive"""
    outcome: list[R] = []
    failure: list[BaseException] = []
    context = contextvars.copy_context()

    def run() -> None:
        try:
            outcome.append(context.run(get))
        except BaseException as error:  # handed to the waiting thread
            failure.append(error)

    worker = threading.Thread(target=run, name="einargate-wait", daemon=True)
    worker.start()
    worker.join(max(0.0, scope.remaining()))
    if worker.is_alive():
        scope.abort()
        return None
    if failure:
        raise failure[0]
    return outcome[0]


def _spent(scope: Deadline) -> bool:
    """Whether a failure is the wait running out rather than the API's"""
    return scope.cut_short or scope.remaining() <= 0


def _start(from_: datetime | None) -> datetime:
    """Where ``follow`` starts, in whole milliseconds as the API sends times,
    so that an event at the start is not taken for an older one"""
    start = from_ or datetime.now(timezone.utc)
    return start.replace(microsecond=start.microsecond // 1000 * 1000)


def _is_settled(event: t.EventWithAttachments) -> bool:
    return event.status != "pending" and all(
        attachment.status != "requested" for attachment in event.attachments
    )


def _timed_out(
    event: t.Event | t.EventWithAttachments | t.EventRef,
    last: t.EventWithAttachments | None,
    wait: float,
) -> Err[WaitTimeout]:
    return Err(
        WaitTimeout(
            message=(
                f"Event {event.event_id} still had pending attachments after {wait} s"
            ),
            event=last,
        )
    )


class PermissionsResource(_Permissions):
    __doc__ = _Permissions.__doc__

    def update(
        self,
        permission: t.Permission,
        *,
        license_plate: str | NotGiven = NOT_GIVEN,
        license_plate_country: str | NotGiven | None = NOT_GIVEN,
        active: bool | NotGiven = NOT_GIVEN,
        supplemental_info: str | NotGiven | None = NOT_GIVEN,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.Permission, o.ReplacePermissionError]:
        """Changes some fields of a permission and keeps the others.

        A ``replace`` built from the permission as you got it, so that a field
        you do not mention is not removed. It does not read the permission
        again. Changing the plate or the country changes the
        ``permission_id``: use the permission this returns from then on.
        """
        body = _replacement(
            permission, license_plate, license_plate_country, active, supplemental_info
        )
        return self.replace(
            permission,
            license_plate=body.license_plate,
            license_plate_country=body.license_plate_country,
            active=body.active,
            supplemental_info=body.supplemental_info,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )


class AsyncPermissionsResource(_AsyncPermissions):
    __doc__ = _AsyncPermissions.__doc__

    async def update(
        self,
        permission: t.Permission,
        *,
        license_plate: str | NotGiven = NOT_GIVEN,
        license_plate_country: str | NotGiven | None = NOT_GIVEN,
        active: bool | NotGiven = NOT_GIVEN,
        supplemental_info: str | NotGiven | None = NOT_GIVEN,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> Result[t.Permission, o.ReplacePermissionError]:
        """``PermissionsResource.update`` for the async client."""
        body = _replacement(
            permission, license_plate, license_plate_country, active, supplemental_info
        )
        return await self.replace(
            permission,
            license_plate=body.license_plate,
            license_plate_country=body.license_plate_country,
            active=body.active,
            supplemental_info=body.supplemental_info,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )


class EventsResource(_Events):
    __doc__ = _Events.__doc__

    def follow(
        self,
        *,
        from_: datetime | None = None,
        gate_id: str | None = None,
        camera_id: str | None = None,
        type: t.EventType | None = None,
        license_plate: str | None = None,
        min_fraud_risk_percentage: int | None = None,
        poll_interval: float = 5.0,
        timeout: float | None = None,
    ) -> Iterator[Result[t.Event, o.ListEventsError]]:
        """Yields every event from ``from_`` on, then each new one as it appears.

        ``from_`` is now when left out. Oldest first, polling ``list``; each
        event is yielded once, as first seen: get it again for a later status.
        A failure is yielded and ends the iteration; stop it by breaking out
        of the loop. An event that reaches the API late, with an earlier time
        than the last one seen, is not yielded.
        """
        cursor = _start(from_)
        seen: set[str] = set()
        while True:
            events = self.list_all(
                from_=cursor,
                gate_id=gate_id,
                camera_id=camera_id,
                type=type,
                license_plate=license_plate,
                min_fraud_risk_percentage=min_fraud_risk_percentage,
                timeout=timeout,
            )
            if isinstance(events, Err):
                yield events
                return
            for event in events.data:
                if event.event_time < cursor or (
                    event.event_time == cursor and event.event_id in seen
                ):
                    continue
                if event.event_time > cursor:
                    cursor = event.event_time
                    seen = set()
                seen.add(event.event_id)
                yield Ok(event, events.response)
            time.sleep(poll_interval)

    def wait_for_attachments(
        self,
        event: t.Event | t.EventWithAttachments | t.EventRef,
        *,
        wait: float = 60.0,
        poll_interval: float = 2.0,
        timeout: float | None = None,
    ) -> Result[t.EventWithAttachments, o.GetEventError | WaitTimeout]:
        """Gets an event again until its snapshots arrive.

        Until it is no longer ``pending`` and none of its attachments is still
        ``requested``: after ``gates.open``, the snapshots of the opening. The
        attachments' URLs are valid for 15 minutes. ``wait`` is the time in all,
        in seconds: each poll gets at most the time left.
        """
        last: t.EventWithAttachments | None = None
        # The deadline bounds each poll's attempts, retries and lookup. A poll
        # runs in a worker so that the wait ends on time even while a
        # response arrives slowly, which a timeout per network operation
        # cannot bound; the response is then closed, which ends the worker.
        with deadline(wait) as scope:
            while True:
                result = _poll(lambda: self.get(event, timeout=timeout), scope)
                if result is None:
                    return _timed_out(event, last, wait)
                if isinstance(result, Err):
                    return _timed_out(event, last, wait) if _spent(scope) else result
                if _is_settled(result.data):
                    return result
                last = result.data
                if scope.remaining() <= poll_interval:
                    return _timed_out(event, last, wait)
                time.sleep(poll_interval)


class AsyncEventsResource(_AsyncEvents):
    __doc__ = _AsyncEvents.__doc__

    async def follow(
        self,
        *,
        from_: datetime | None = None,
        gate_id: str | None = None,
        camera_id: str | None = None,
        type: t.EventType | None = None,
        license_plate: str | None = None,
        min_fraud_risk_percentage: int | None = None,
        poll_interval: float = 5.0,
        timeout: float | None = None,
    ) -> AsyncIterator[Result[t.Event, o.ListEventsError]]:
        """``EventsResource.follow`` for the async client."""
        cursor = _start(from_)
        seen: set[str] = set()
        while True:
            events = await self.list_all(
                from_=cursor,
                gate_id=gate_id,
                camera_id=camera_id,
                type=type,
                license_plate=license_plate,
                min_fraud_risk_percentage=min_fraud_risk_percentage,
                timeout=timeout,
            )
            if isinstance(events, Err):
                yield events
                return
            for event in events.data:
                if event.event_time < cursor or (
                    event.event_time == cursor and event.event_id in seen
                ):
                    continue
                if event.event_time > cursor:
                    cursor = event.event_time
                    seen = set()
                seen.add(event.event_id)
                yield Ok(event, events.response)
            await asyncio.sleep(poll_interval)

    async def wait_for_attachments(
        self,
        event: t.Event | t.EventWithAttachments | t.EventRef,
        *,
        wait: float = 60.0,
        poll_interval: float = 2.0,
        timeout: float | None = None,
    ) -> Result[t.EventWithAttachments, o.GetEventError | WaitTimeout]:
        """``EventsResource.wait_for_attachments`` for the async client."""
        last: t.EventWithAttachments | None = None
        with deadline(wait) as scope:
            while True:
                try:
                    # Bounds the poll even where the deadline cannot reach
                    result = await asyncio.wait_for(
                        self.get(event, timeout=timeout), max(0.0, scope.remaining())
                    )
                except asyncio.TimeoutError:
                    return _timed_out(event, last, wait)
                if isinstance(result, Err):
                    return _timed_out(event, last, wait) if _spent(scope) else result
                if _is_settled(result.data):
                    return result
                last = result.data
                if scope.remaining() <= poll_interval:
                    return _timed_out(event, last, wait)
                await asyncio.sleep(poll_interval)
