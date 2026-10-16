/**
 * A value that this version of the library does not know: an enum value or
 * a union variant that the API added after this version was released. The
 * API may add them within v1, so every enum and union in a response
 * includes `UnknownValue`, and an exhaustive `switch` needs a branch for it.
 *
 * It is an object, so that comparing it with a known value cannot compile
 * by mistake. `String(value)` and `JSON.stringify` give the value as sent.
 */
export class UnknownValue {
  /** The value as the API sent it */
  readonly unknown: string

  constructor(value: string) {
    this.unknown = value
    Object.freeze(this)
  }

  toString(): string {
    return this.unknown
  }

  toJSON(): string {
    return this.unknown
  }
}

/** Whether a value is one this version of the library does not know */
export function isUnknown(value: unknown): value is UnknownValue {
  return value instanceof UnknownValue
}
