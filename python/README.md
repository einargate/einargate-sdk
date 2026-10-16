# einargate

> **Very early alpha.** The Einar Gate public API is not generally
> available yet, and this client may change in breaking ways before 1.0:
> pin an exact version.

The official Python client of the [Einar Gate](https://einargate.com) API:
sync license plate permissions, read gates, cameras and gate openings, and
open gates from your own system.

- **Typed results instead of exceptions.** Every call returns `Ok` or `Err`,
  and each call's error type lists exactly the problems it can return.
- **Safe retries.** The client retries only what cannot run twice; a
  write that may have run comes back with its idempotency key instead of
  opening a gate twice.
- **Built for coding agents.** [AGENTS.md](https://github.com/einargate/einargate-sdk/blob/main/python/AGENTS.md) is the complete
  guide; the docstrings name each call's roles and errors.

```sh
pip install einargate
```

```python
from einargate import EinarGate

with EinarGate() as eg:  # reads EINARGATE_API_KEY
    for gate in eg.gates.list_all().unwrap():
        print(gate.gate_id, gate.name)
```

Python 3.10 or later, sync and async (`AsyncEinarGate`); the only dependency
is `httpx`. API keys are created in the Einar Gate app by a location Owner
or Admin.

## Compatibility

The client follows semantic versioning on its own, separately from the
API's `/v1`. Within v1 the API only adds things: new calls, fields, enum
values and error types. The client is written for that: a value it does not
know arrives as `UnknownValue` and an error type it does not know as
`UnknownProblem`, so an older client keeps working.

## License

MIT
