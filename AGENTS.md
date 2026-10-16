# Einar Gate API clients: guide for coding agents

Use the client of your language; each package has its own AGENTS.md with
the rules, recipes and a table of every call:

- TypeScript: [`@einargate/sdk`](./typescript/AGENTS.md)
- Python: [`einargate`](./python/AGENTS.md)

In any other language, generate a client from [openapi.json](./openapi.json)
and follow the same rules:

1. Errors are RFC 9457 problem details (`application/problem+json`). Branch
   on the `type` URI's last segment (`not-found`, `limit-exceeded`, …); an
   unknown type is handled by its HTTP status. Each problem schema's
   description says what to do about it.
2. Every write takes an `Idempotency-Key` header: send one, and the same on
   every retry. Retry a write by itself only when it cannot have run (429
   with `window: "second"`, 503 `provisioning`, `idempotency-key-in-flight`,
   no connection). After a timeout or a 5xx it may have run, and the API
   releases the key of a failed write, so decide before sending it again:
   a retry can open a gate twice.
3. Ignore response members you do not know, and accept enum values you do
   not know: the API adds them within v1.
4. Ids are opaque: use them as returned and URL-encode them in paths.
5. `GET /me` names the API key's location, roles and rate limits; every
   other path is under `/locations/{locationId}` with that location. Each
   operation's `x-einargate-roles` lists the roles that allow it.
