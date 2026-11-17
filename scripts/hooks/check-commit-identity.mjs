// Pre-commit gate: commits in matt's repos go out under matt's identity (~/.buzz/AGENTS.md, "Git identity").
//
// Reads the identity git will actually use for this commit (`git var`, so GIT_AUTHOR_* env and GIT_CONFIG_* both
// count). An agent session's injected identity (a nostr pubkey @ the relay host) fails here: prefix git with
// GIT_CONFIG_COUNT=0 so matt's own config is used.
import { execSync } from 'node:child_process';

const OWNER = 'matthewdonsemail-lab';
const EMAILS = [
  '242104473+matthewdonsemail-lab@users.noreply.github.com',
  'matthewdonsemail-lab@users.noreply.github.com',
];

function ident(kind) {
  try {
    const out = execSync(`git var GIT_${kind}_IDENT`, { encoding: 'utf8' }).trim();
    const m = out.match(/^(.*) <([^>]*)>/);
    return m ? { name: m[1], email: m[2] } : { name: out, email: '' };
  } catch {
    return { name: '', email: '' };
  }
}

const bad = [];
for (const kind of ['AUTHOR', 'COMMITTER']) {
  const { name, email } = ident(kind);
  if (name !== OWNER || !EMAILS.includes(email)) bad.push(`${kind.toLowerCase()} is "${name} <${email}>"`);
}
if (bad.length) {
  console.error('pre-commit: FAIL — commits here go out as matthewdonsemail-lab <242104473+matthewdonsemail-lab@users.noreply.github.com>.');
  for (const b of bad) console.error(`  - ${b}`);
  console.error('  From an agent session, prefix git with GIT_CONFIG_COUNT=0 (e.g. GIT_CONFIG_COUNT=0 git commit ...).');
  process.exit(1);
}
console.log('check-commit-identity: matthewdonsemail-lab.');
