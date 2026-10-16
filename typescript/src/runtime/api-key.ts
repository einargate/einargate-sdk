/**
 * Checks the format of an API key value, `egk_` + 30 random base62
 * characters + a 6-character CRC32 checksum, so that a mistyped or
 * truncated value fails when the client is created rather than as
 * `unauthorized` on the first call.
 */

const PATTERN = /^egk_[0-9A-Za-z]{36}$/
const ALPHABET =
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
const CHECKSUM_LENGTH = 6

/** Why a value is not an API key value, or `undefined` when it is one */
export function apiKeyProblem(value: string): string | undefined {
  if (!PATTERN.test(value)) {
    return value.startsWith('egk_')
      ? 'it is not 40 characters of egk_ and letters and digits'
      : 'it does not start with egk_'
  }
  const body = value.slice(0, -CHECKSUM_LENGTH)
  if (checksum(body) !== value.slice(-CHECKSUM_LENGTH)) {
    return 'its checksum does not match: it was mistyped or truncated'
  }
  return undefined
}

export function checksum(body: string): string {
  let value = crc32(body)
  let result = ''
  do {
    result = ALPHABET[value % 62] + result
    value = Math.floor(value / 62)
  } while (value > 0)
  return result.padStart(CHECKSUM_LENGTH, '0')
}

let table: Uint32Array | undefined

/** CRC-32 (IEEE), as `zlib.crc32` computes it, of an ASCII string */
function crc32(text: string): number {
  table ??= buildTable()
  let crc = 0xffffffff
  for (let i = 0; i < text.length; i++) {
    crc = table[(crc ^ text.charCodeAt(i)) & 0xff] ^ (crc >>> 8)
  }
  return (crc ^ 0xffffffff) >>> 0
}

function buildTable(): Uint32Array {
  const result = new Uint32Array(256)
  for (let n = 0; n < 256; n++) {
    let c = n
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
    }
    result[n] = c >>> 0
  }
  return result
}
