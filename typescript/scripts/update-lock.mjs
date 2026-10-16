// Writes package-lock.json for this package on its own, outside the
// monorepo's workspace (ADR-0022). The public repository installs with
// `npm ci` from it, so that a snapshot is built from reviewed dependency
// versions. Run it after changing package.json's dependencies:
//
//   npm run lock --workspace @einargate/sdk
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const work = fs.mkdtempSync(path.join(os.tmpdir(), 'einargate-sdk-lock-'))

try {
  fs.copyFileSync(
    path.join(root, 'package.json'),
    path.join(work, 'package.json')
  )
  const lock = path.join(root, 'package-lock.json')
  if (fs.existsSync(lock)) {
    fs.copyFileSync(lock, path.join(work, 'package-lock.json'))
  }
  execFileSync(
    'npm',
    [
      'install',
      '--package-lock-only',
      '--ignore-scripts',
      '--no-audit',
      '--no-fund',
    ],
    { cwd: work, stdio: 'inherit' }
  )
  fs.copyFileSync(path.join(work, 'package-lock.json'), lock)
  console.log('Updated sdks/typescript/package-lock.json')
} finally {
  fs.rmSync(work, { recursive: true, force: true })
}
