"""The official Python client of the Einar Gate API.

Start with ``EinarGate()`` (or ``AsyncEinarGate()``), and read AGENTS.md in
this package's repository for the model: every call returns ``Ok`` or
``Err``, and ``error.type`` says what happened.
"""

from ._client import DEFAULT_BASE_URL, AppInfo, AsyncEinarGate, EinarGate
from ._generated import models as _models
from ._generated import operations as _operations
from ._generated.models import *  # noqa: F403
from ._generated.operations import *  # noqa: F403
from ._helpers import WaitTimeout
from ._runtime.encode import NOT_GIVEN, NotGiven
from ._runtime.errors import (
    CallError,
    EinarGateError,
    NetworkError,
    ProblemBase,
    RequestTimeout,
    UnexpectedResponse,
    UnknownProblem,
)
from ._runtime.page import Page
from ._runtime.result import Err, Ok, ResponseInfo, Result
from ._runtime.unknown import UnknownValue, is_unknown
from ._version import __version__

__all__ = [
    "DEFAULT_BASE_URL",
    "NOT_GIVEN",
    "AppInfo",
    "AsyncEinarGate",
    "CallError",
    "EinarGate",
    "EinarGateError",
    "Err",
    "NetworkError",
    "NotGiven",
    "Ok",
    "Page",
    "ProblemBase",
    "RequestTimeout",
    "ResponseInfo",
    "Result",
    "UnexpectedResponse",
    "UnknownProblem",
    "UnknownValue",
    "WaitTimeout",
    "__version__",
    "is_unknown",
]
__all__ += _models.__all__
__all__ += _operations.__all__
