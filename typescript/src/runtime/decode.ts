import { UnknownValue } from './unknown-value.js'

/**
 * Building blocks of the generated decoders, which check every success body
 * against the contract while they turn it into the library's types. A body
 * that does not match becomes an `unexpected-response` error, so a value
 * never claims a type it does not have. Decoding is lenient where the
 * contract lets the API grow: unknown members are ignored, and unknown enum
 * values and union variants become `UnknownValue`.
 */

/** Thrown inside a decoder; the transport turns it into a result */
export class DecodeError extends Error {
  constructor(
    readonly path: string,
    readonly expected: string
  ) {
    super(`${path || 'the body'}: expected ${expected}`)
    this.name = 'DecodeError'
  }
}

export type Decoder<T> = (value: unknown, path: string) => T

export type JsonObject = Readonly<Record<string, unknown>>

export function object(value: unknown, path: string): JsonObject {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new DecodeError(path, 'an object')
  }
  return value as JsonObject
}

export function string(value: unknown, path: string): string {
  if (typeof value !== 'string') {
    throw new DecodeError(path, 'a string')
  }
  return value
}

export function number(value: unknown, path: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new DecodeError(path, 'a number')
  }
  return value
}

export function integer(value: unknown, path: string): number {
  if (!Number.isInteger(value)) {
    throw new DecodeError(path, 'an integer')
  }
  return value as number
}

export function boolean(value: unknown, path: string): boolean {
  if (typeof value !== 'boolean') {
    throw new DecodeError(path, 'a boolean')
  }
  return value
}

/** An ISO 8601 timestamp */
export function timestamp(value: unknown, path: string): Date {
  const date = new Date(string(value, path))
  if (Number.isNaN(date.getTime())) {
    throw new DecodeError(path, 'an ISO 8601 timestamp')
  }
  return date
}

export function literal<const T extends string | number>(
  value: unknown,
  path: string,
  expected: T
): T {
  if (value !== expected) {
    throw new DecodeError(path, JSON.stringify(expected))
  }
  return expected
}

/** A known value, or an `UnknownValue` for one added since this release */
export function enumValue<const T extends string>(
  value: unknown,
  path: string,
  values: readonly T[]
): T | UnknownValue {
  const text = string(value, path)
  return (values as readonly string[]).includes(text)
    ? (text as T)
    : new UnknownValue(text)
}

export function array<T>(
  value: unknown,
  path: string,
  item: Decoder<T>
): readonly T[] {
  if (!Array.isArray(value)) {
    throw new DecodeError(path, 'an array')
  }
  return value.map((element, index) => item(element, `${path}.${index}`))
}

export function nonEmptyArray<T>(
  value: unknown,
  path: string,
  item: Decoder<T>
): readonly [T, ...T[]] {
  const items = array(value, path, item)
  if (items.length === 0) {
    throw new DecodeError(path, 'at least one item')
  }
  return items as readonly [T, ...T[]]
}

export function jsonObject(value: unknown, path: string): JsonObject {
  return object(value, path)
}

/** `""` is how the API says "none" in a few fields */
export function nullIfEmpty(value: string): string | null {
  return value === '' ? null : value
}

/** A member that must be present */
export function required<T>(
  value: JsonObject,
  key: string,
  path: string,
  decode: Decoder<T>
): T {
  return decode(value[key], join(path, key))
}

/** A member that may be absent; `null` counts as absent */
export function optional<T>(
  value: JsonObject,
  key: string,
  path: string,
  decode: Decoder<T>
): T | undefined {
  const member = value[key]
  return member === undefined || member === null
    ? undefined
    : decode(member, join(path, key))
}

/** Leaves out the members whose value is `undefined` */
export function compact<T extends object>(value: T): T {
  return Object.fromEntries(
    Object.entries(value).filter(([, member]) => member !== undefined)
  ) as T
}

export function join(path: string, key: string): string {
  return path ? `${path}.${key}` : key
}
