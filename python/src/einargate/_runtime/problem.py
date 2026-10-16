from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypedDict

from . import decode as d
from .transport import ProblemInfo


@dataclass(frozen=True, slots=True)
class ProblemType:
    """A problem type as the generated code describes it."""

    slug: str
    status: int
    title: str
    hint: str
    docs_url: str


class ProblemCommon(TypedDict):
    title: str
    detail: str | None
    instance: str | None
    request_id: str
    hint: str
    docs_url: str
    retry_after_seconds: int | None
    message: str
    body: Mapping[str, object]


def problem_fields(
    body: d.JsonObject, problem: ProblemType, info: ProblemInfo
) -> ProblemCommon:
    """Decodes the members every problem has."""
    d.literal(body.get("type"), "type", problem.docs_url)
    d.literal(body.get("status"), "status", problem.status)
    # A problem whose body and HTTP status disagree is not that problem
    if info.status is not None and info.status != problem.status:
        raise d.DecodeError("status", f"HTTP status {problem.status}")
    title = d.required(body, "title", "", d.string)
    request_id = d.required(body, "requestId", "", d.string)
    detail = d.optional(body, "detail", "", d.string)
    instance = d.optional(body, "instance", "", d.string)
    message = (
        f"{title} ({problem.status} {problem.slug})"
        + (f": {detail}" if detail else "")
        + f". {problem.hint} Request id {request_id}; see {problem.docs_url}"
    )
    return ProblemCommon(
        title=title,
        detail=detail,
        instance=instance,
        request_id=request_id,
        hint=problem.hint,
        docs_url=problem.docs_url,
        retry_after_seconds=info.retry_after_seconds,
        message=message,
        body=body,
    )
