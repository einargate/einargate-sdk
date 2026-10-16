import * as d from './decode.js'
import type { ProblemFields } from './errors.js'
import type { ProblemInfo } from './transport.js'

/** A problem type as the generated code describes it */
export interface ProblemType<T extends string, S extends number> {
  readonly slug: T
  readonly status: S
  readonly title: string
  readonly hint: string
  readonly docsUrl: string
}

/** Decodes the members every problem has */
export function problemFields<T extends string, S extends number>(
  body: d.JsonObject,
  type: ProblemType<T, S>,
  info: ProblemInfo
): ProblemFields<T, S> {
  d.literal(body.type, 'type', type.docsUrl)
  d.literal(body.status, 'status', type.status)
  // A problem whose body and HTTP status disagree is not that problem
  if (info.status !== undefined && info.status !== type.status) {
    throw new d.DecodeError('status', `HTTP status ${type.status}`)
  }
  const title = d.required(body, 'title', '', d.string)
  const requestId = d.required(body, 'requestId', '', d.string)
  const detail = d.optional(body, 'detail', '', d.string)
  const instance = d.optional(body, 'instance', '', d.string)

  return d.compact({
    type: type.slug,
    status: type.status,
    title,
    detail,
    instance,
    requestId,
    hint: type.hint,
    docsUrl: type.docsUrl,
    retryAfterSeconds: info.retryAfterSeconds,
    message:
      `${title} (${type.status} ${type.slug})` +
      (detail ? `: ${detail}` : '') +
      `. ${type.hint} Request id ${requestId}; see ${type.docsUrl}`,
    body,
  })
}
