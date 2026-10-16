# Einar Gate API clients

> **Very early alpha.** The Einar Gate public API is not generally
> available yet, and these clients may change in breaking ways before 1.0:
> pin an exact version.

The official client libraries of the [Einar Gate](https://einargate.com)
public API, which lets your own systems sync license plate permissions, read
gates, cameras and gate openings, and open gates.

| Language | Package | Guide |
| --- | --- | --- |
| TypeScript | [`@einargate/sdk`](./typescript) | [typescript/AGENTS.md](./typescript/AGENTS.md) |
| Python | [`einargate`](./python) | [python/AGENTS.md](./python/AGENTS.md) |

Every client is generated from the API's OpenAPI document,
[`openapi.json`](./openapi.json), the same one the API serves at
`https://api.einargate.com/v1/openapi.json`. Any other language can generate
a client from it.

## What every client does the same way

- Every call returns a typed result; nothing the API or the network does
  throws. Each call's error type lists exactly the problems it can return.
- The built-in retries never repeat a write that may have run: such a
  failure comes back with the idempotency key to send it again with.
- The client is bound to the API key's location: no location ids to pass.
- Values the API adds later (enum values, union variants, error types) are
  represented explicitly, so an older client keeps working.

[AGENTS.md](./AGENTS.md) is the short version for coding agents.

## This repository

This repository is a published snapshot. The clients are developed together
with the API in Einar Gate's own repository, where a change to the API does
not build until the clients match it. Issues are welcome here; we port
contributions into the main repository rather than merging pull requests
here.

## License

[MIT](./LICENSE)
