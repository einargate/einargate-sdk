import { UnknownValue } from './unknown-value.js'

/** Writes query parameter values; `undefined` leaves a parameter out */

export function string(value: string | undefined): string | undefined {
  return value
}

export function integer(value: number | undefined): string | undefined {
  return value === undefined ? undefined : String(value)
}

export function boolean(value: boolean | undefined): string | undefined {
  return value === undefined ? undefined : String(value)
}

export function timestamp(value: Date | undefined): string | undefined {
  return value === undefined ? undefined : value.toISOString()
}

export function enumValue(
  value: string | UnknownValue | undefined
): string | undefined {
  return value instanceof UnknownValue ? value.unknown : value
}
