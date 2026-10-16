from __future__ import annotations

import random
import zlib

import pytest

from einargate import EinarGate
from einargate._runtime.api_key import api_key_problem, checksum
from einargate.testing import MOCK_API_KEY

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def server_checksum(body: str) -> str:
    """The API's checksum (packages/aws/lambda/common/api-key-value.ts)."""
    value = zlib.crc32(body.encode())
    result = ""
    while True:
        result = ALPHABET[value % 62] + result
        value //= 62
        if value == 0:
            return result.rjust(6, "0")


def test_computes_the_checksum_the_api_computes() -> None:
    for _ in range(200):
        body = "egk_" + "".join(random.choice(ALPHABET) for _ in range(30))
        assert checksum(body) == server_checksum(body)


def test_says_what_is_wrong_with_a_value() -> None:
    assert api_key_problem(MOCK_API_KEY) is None
    assert "egk_" in (api_key_problem("sk_live_123") or "")
    assert "40 characters" in (api_key_problem(MOCK_API_KEY[:-1]) or "")
    typo = MOCK_API_KEY[:10] + "X" + MOCK_API_KEY[11:]
    assert "checksum" in (api_key_problem(typo) or "")


def test_refuses_a_missing_or_malformed_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EINARGATE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="EINARGATE_API_KEY"):
        EinarGate()
    with pytest.raises(ValueError, match="not valid"):
        EinarGate("egk_short")
    monkeypatch.setenv("EINARGATE_API_KEY", MOCK_API_KEY)
    EinarGate().close()
