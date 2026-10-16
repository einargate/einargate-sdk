// Type-checks every ```ts block of the documentation against the library's
// source, so that the examples agents copy always compile (ADR-0022).
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const documents = ['README.md', 'AGENTS.md', '../README.md', '../AGENTS.md']
const out = path.join(root, '.examples')

fs.rmSync(out, { recursive: true, force: true })
fs.mkdirSync(out)

let count = 0
for (const document of documents) {
  const file = path.join(root, document)
  if (!fs.existsSync(file)) {
    continue
  }
  const text = fs.readFileSync(file, 'utf-8')
  for (const [, code] of text.matchAll(/```ts\n([\s\S]*?)```/g)) {
    count++
    const name = `${document.replace(/[^A-Za-z]+/g, '-')}${count}.ts`
    // Each block is a module of its own
    fs.writeFileSync(path.join(out, name), `${code}\nexport {}\n`)
  }
}

fs.writeFileSync(
  path.join(out, 'tsconfig.json'),
  JSON.stringify({
    extends: '../tsconfig.json',
    compilerOptions: {
      noEmit: true,
      paths: {
        '@einargate/sdk': ['../src/index.ts'],
        '@einargate/sdk/testing': ['../src/testing.ts'],
      },
    },
    include: ['./*.ts'],
  })
)

try {
  execFileSync(
    process.execPath,
    [createRequire(import.meta.url).resolve('typescript/bin/tsc'), '-p', out],
    { stdio: 'inherit' }
  )
} catch {
  console.error('A documentation example does not compile (see above).')
  process.exit(1)
} finally {
  fs.rmSync(out, { recursive: true, force: true })
}
console.log(`${count} documentation examples compile.`)
