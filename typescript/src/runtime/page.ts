import type { AnyError } from './errors.js'
import { type Result, type ResponseInfo, success } from './result.js'

/** One page of a listing */
export interface Page<T> {
  readonly items: readonly T[]
  /** Present when there are more items: pass it to get the next page */
  readonly continuationToken?: string
}

/** The largest page the API serves */
export const MAX_PAGE_SIZE = 200

/**
 * Fetches pages until the last one and returns their items as one result,
 * or the first failure
 */
export async function collectPages<T, E extends AnyError>(
  fetchPage: (
    continuationToken: string | undefined
  ) => Promise<Result<Page<T>, E>>
): Promise<Result<readonly T[], E>> {
  const items: T[] = []
  let continuationToken: string | undefined
  let response: ResponseInfo

  do {
    const page = await fetchPage(continuationToken)
    if (!page.success) {
      return page
    }
    items.push(...page.data.items)
    continuationToken = page.data.continuationToken
    response = page.response
  } while (continuationToken !== undefined)

  return success(items, response)
}
