// Pre-push gate: hook/script name alignment.
//
// lefthook.yml is only as good as its wiring. This check fails when the hook
// config and the script tree drift in either direction:
// 1. Every `run:` target in lefthook.yml resolves to a file that exists
//    (scripts/hooks/*.mjs entrypoints, bun test/run targets).
// 2. Every scripts/hooks/check-*.mjs is wired into lefthook.yml (no orphan
//    checks that pass locally in someone's head but never run in the gate).
//
// Hook implementations are namespaced under scripts/hooks/. Run by lefthook
// itself (see lefthook.yml) — keep this file's name stable.
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

function findRoot(start) { let dir = start; for (;;) { try { readdirSync(dir); } catch { throw new Error('repo root not found'); } if (existsSync(join(dir, 'lefthook.yml'))) return dir; const parent = dirname(dir); if (parent === dir) throw new Error('repo root not found (no lefthook.yml above ' + start + ')'); dir = parent; } }
const root = findRoot(dirname(fileURLToPath(import.meta.url)));
const violations = [];

const hookPath = join(root, 'lefthook.yml');
if (!existsSync(hookPath)) {
  console.error('pre-push: FAIL — lefthook.yml is missing from the repo root.');
  process.exit(1);
}
const hook = readFileSync(hookPath, 'utf8');

const referenced = new Set();
for (const line of hook.split('\n')) {
  const match = line.match(/^\s*run:\s*(.+?)\s*$/);
  if (!match) continue;
  const command = match[1];
  for (const token of command.split(/\s+/)) {
    const script = token.match(/^(scripts\/[A-Za-z0-9_./-]+\.mjs)$/);
    if (script) referenced.add(script[1]);
    const bunTarget = token.match(/^(lib|packages|apps)\/[A-Za-z0-9_./-]+$/);
    if (bunTarget && (command.includes('bun test') || command.includes('bun run'))) {
      referenced.add(bunTarget[1]);
    }
  }
}

for (const ref of [...referenced].sort()) {
  if (!existsSync(join(root, ref))) {
    violations.push(`lefthook.yml runs "${ref}" but that path does not exist — rename the script or the job.`);
  }
}

const checksDir = join(root, 'scripts', 'hooks');
const onDisk = existsSync(checksDir)
  ? readdirSync(checksDir).filter((f) => f.startsWith('check-') && f.endsWith('.mjs'))
  : [];
for (const file of onDisk.sort()) {
  if (!hook.includes(`scripts/hooks/${file}`)) {
    violations.push(`scripts/hooks/${file} exists but is not wired into lefthook.yml — add a job or delete it.`);
  }
}

if (violations.length > 0) {
  console.error('pre-push: FAIL — hook/script name misalignment:');
  for (const violation of violations) console.error(`  - ${violation}`);
  process.exit(1);
}
console.log(`pre-push: OK — ${referenced.size} hook targets resolve, ${onDisk.length} check scripts wired.`);
