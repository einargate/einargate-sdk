"""Checks the format of an API key value.

``egk_`` + 30 random base62 characters + a 6-character CRC32 checksum, so
that a mistyped or truncated value fails when the client is created rather
than as ``unauthorized`` on the first call.
"""

from __future__ import annotations

import re
import zlib

_PATTERN = re.compile(r"egk_[0-9A-Za-z]{36}")
_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_CHECKSUM_LENGTH = 6


def api_key_problem(value: str) -> str | None:
    """Why a value is not an API key value, or ``None`` when it is one."""
    if not _PATTERN.fullmatch(value):
        if value.startswith("egk_"):
            return "it is not 40 characters of egk_ and letters and digits"
        return "it does not start with egk_"
    body = value[:-_CHECKSUM_LENGTH]
    if checksum(body) != value[-_CHECKSUM_LENGTH:]:
        return "its checksum does not match: it was mistyped or truncated"
    return None


def checksum(body: str) -> str:
    value = zlib.crc32(body.encode("ascii"))
    result = ""
    while True:
        result = _ALPHABET[value % 62] + result
        value //= 62
        if value == 0:
            break
    return result.rjust(_CHECKSUM_LENGTH, "0")
