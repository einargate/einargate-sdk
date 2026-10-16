# @einargate/sdk

> **Very early alpha.** The Einar Gate public API is not generally
> available yet, and this client may change in breaking ways before 1.0:
> pin an exact version.

The official TypeScript client of the [Einar Gate](https://einargate.com)
API: sync license plate permissions, read gates, cameras and gate openings,
and open gates from your own system.

- **Typed results instead of exceptions.** Every call returns a `Result`
  whose error lists exactly the problems that call can return.
- **Safe retries.** The client retries only what cannot run twice; a
  write that may have run comes back with its idempotency key instead of
  opening a gate twice.
- **Built for coding agents.** [AGENTS.md](https://github.com/einargate/einargate-sdk/blob/main/typescript/AGENTS.md) is the complete
  guide; the doc comments name each call's roles and errors.

```sh
npm install @einargate/sdk
```

```ts
import { EinarGate } from '@einargate/sdk'

const eg = new EinarGate() // reads EINARGATE_API_KEY

const gates = await eg.gates.listAll()
if (!gates.success) {
  throw new Error(gates.error.message)
}
for (const gate of gates.data) {
  console.log(gate.gateId, gate.name)
}
```

Node.js 22.12 or later, Bun or Deno; no runtime dependencies. API keys are
created in the Einar Gate app by a location Owner or Admin.

## Compatibility

The client follows semantic versioning on its own, separately from the
API's `/v1`. Within v1 the API only adds things: new calls, fields, enum
values and error types. The client is written for that: a value it does not
know arrives as `UnknownValue` and an error type it does not know as
`unknown-problem`, so an older client keeps working.

## License

MIT
