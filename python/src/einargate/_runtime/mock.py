"""The calls ``einargate.testing``'s mock records; its replies are generated,
typed by each problem type's members (``_generated/mock.py``)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MockCall:
    """A request the client sent."""

    operation: str
    """The snake_case operation id, e.g. ``open_gate``"""
    method: str
    path: str
    """As sent, still percent-encoded, e.g. ``/locations/mock-location/gates/g1``"""
    params: Mapping[str, str]
    """The path parameters, decoded"""
    query: Mapping[str, str]
    body: object
    """The parsed JSON body, or ``None``"""
    headers: Mapping[str, str]
    """Lower-case names"""
