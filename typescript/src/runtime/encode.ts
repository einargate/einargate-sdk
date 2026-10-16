import { UnknownValue } from './unknown-value.js'

/** Building blocks of the generated encoders, which write wire JSON */

export function timestamp(value: Date): string {
  return value.toISOString()
}

/** An enum value as sent, known or not */
export function enumValue(value: string | UnknownValue): string {
  return value instanceof UnknownValue ? value.unknown : value
}

/** `null` is sent as `""`, how the API says "none" in a few fields */
export function emptyIfNull(value: string | null): string {
  return value ?? ''
}

/** Leaves out the members whose value is `undefined` */
export function compact(
  value: Record<string, unknown>
): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(value).filter(([, member]) => member !== undefined)
  )
}
