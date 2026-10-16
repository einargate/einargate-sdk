import { crc32 } from 'node:zlib'
import { describe, expect, it } from 'vitest'
import { EinarGate } from '../src/index.js'
import { apiKeyProblem, checksum } from '../src/runtime/api-key.js'
import { MOCK_API_KEY } from '../src/testing.js'

const ALPHABET =
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

/** The API's own checksum (packages/aws/lambda/common/api-key-value.ts) */
function serverChecksum(body: string): string {
  let value = crc32(body)
  let result = ''
  do {
    result = ALPHABET[value % 62] + result
    value = Math.floor(value / 62)
  } while (value > 0)
  return result.padStart(6, '0')
}

describe('API key values', () => {
  it('computes the checksum the API computes', () => {
    for (let i = 0; i < 200; i++) {
      let body = 'egk_'
      for (let j = 0; j < 30; j++) {
        body += ALPHABET[Math.floor(Math.random() * 62)]
      }
      expect(checksum(body)).toBe(serverChecksum(body))
    }
  })

  it('accepts a well-formed value and says what is wrong with others', () => {
    expect(apiKeyProblem(MOCK_API_KEY)).toBeUndefined()
    expect(apiKeyProblem('sk_live_123')).toMatch(/egk_/)
    expect(apiKeyProblem(MOCK_API_KEY.slice(0, -1))).toMatch(/40 characters/)
    const typo = MOCK_API_KEY.slice(0, 10) + 'X' + MOCK_API_KEY.slice(11)
    expect(apiKeyProblem(typo)).toMatch(/checksum/)
  })

  it('refuses to create a client without a valid key', () => {
    const saved = process.env.EINARGATE_API_KEY
    delete process.env.EINARGATE_API_KEY
    try {
      expect(() => new EinarGate()).toThrow(/EINARGATE_API_KEY/)
      expect(() => new EinarGate({ apiKey: 'egk_short' })).toThrow(/not valid/)
      process.env.EINARGATE_API_KEY = MOCK_API_KEY
      expect(() => new EinarGate()).not.toThrow()
    } finally {
      if (saved === undefined) {
        delete process.env.EINARGATE_API_KEY
      } else {
        process.env.EINARGATE_API_KEY = saved
      }
    }
  })
})
