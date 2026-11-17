// Pre-commit gate: media stays local (.gitignore: "the scripts and prompts that make them are committed").
//
// Fails when a staged file is over 20 MB (GitHub rejects 100 MB, and the repo stays cloneable), or is a render,
// project or audio file: .mp4 .mov .wav .mp3 .ecproj .fcproj .aep. The one exception is the CRT plugin's
// displacement map bundled in skills (skills/*/assets/**/CRTGRID/*.mp4), which the CRT needs to work, and the
// shipped textAnimations/textAnimations.ecproj (GitHub's hard limit is 100 MB).
// Usage: node scripts/hooks/check-staged-media.mjs [files...]  (lefthook passes {staged_files})
import { existsSync, statSync } from 'node:fs';
import { execSync } from 'node:child_process';

const LIMIT = 20 * 1024 * 1024;
const MEDIA = /\.(mp4|mov|wav|mp3|m4a|ecproj|fcproj|aep)$/i;
const ALLOWED = /^skills\/[^/]+\/assets\/.*\/CRTGRID\/[^/]+\.mp4$/;
// the shipped template project the README tells people to open (tracked since the start, about 70 MB)
const SHIPPED = new Set(['textAnimations/textAnimations.ecproj']);

let files = process.argv.slice(2);
if (!files.length) {
  files = execSync('git diff --cached --name-only --diff-filter=ACMR', { encoding: 'utf8' }).split('\n').filter(Boolean);
}
const bad = [];
for (const f of files.map((p) => p.replace(/\\/g, '/'))) {
  if (!existsSync(f) || SHIPPED.has(f)) continue;
  const size = statSync(f).size;
  if (size > LIMIT) bad.push(`${f} is ${(size / 1048576).toFixed(1)} MB (limit 20 MB)`);
  else if (MEDIA.test(f) && !ALLOWED.test(f)) bad.push(`${f} is a render/project/audio file: keep it local and commit the script that makes it`);
}
if (bad.length) {
  console.error('pre-commit: FAIL — media in the commit:');
  for (const b of bad) console.error(`  - ${b}`);
  process.exit(1);
}
console.log(`check-staged-media: ${files.length} files, no media over the line.`);
