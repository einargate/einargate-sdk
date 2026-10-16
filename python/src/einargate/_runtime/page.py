from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from .result import Err, Ok, ResponseInfo, Result

T = TypeVar("T", covariant=True)
Item = TypeVar("Item")
E = TypeVar("E")

MAX_PAGE_SIZE = 200
"""The largest page the API serves"""


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    """One page of a listing."""

    items: tuple[T, ...]
    continuation_token: str | None = None
    """Present when there are more items: pass it to get the next page"""


def collect_pages(
    fetch_page: Callable[[str | None], Result[Page[Item], E]],
) -> Result[tuple[Item, ...], E]:
    """Fetches pages until the last one; their items, or the first failure."""
    items: list[Item] = []
    token: str | None = None
    while True:
        page = fetch_page(token)
        if isinstance(page, Err):
            return page
        items.extend(page.data.items)
        token = page.data.continuation_token
        if token is None:
            return Ok(tuple(items), page.response)


async def acollect_pages(
    fetch_page: Callable[[str | None], Awaitable[Result[Page[Item], E]]],
) -> Result[tuple[Item, ...], E]:
    """``collect_pages`` for the async client."""
    items: list[Item] = []
    token: str | None = None
    while True:
        page = await fetch_page(token)
        if isinstance(page, Err):
            return page
        items.extend(page.data.items)
        token = page.data.continuation_token
        if token is None:
            return Ok(tuple(items), page.response)


__all__ = ["MAX_PAGE_SIZE", "Page", "ResponseInfo", "acollect_pages", "collect_pages"]
