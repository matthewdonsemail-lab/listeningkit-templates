// Gate: every skill in skills/ is complete and its docs work (matt, 2026-11-17).
//
// For each skills/<name>/ (folders starting with _ are not skills):
//   - SKILL.md exists and starts with frontmatter whose `name:` is the folder name and has a `description:`
//   - every relative link and image in SKILL.md / README.md / assets/MANIFEST.md points at a file that exists
//   - treg is always linked with matt's referral URL: any treg.to URL other than the install script and hosted
//     media (treg.to/m/...) must be exactly https://treg.to/?ref=matthewdonse-aebsh
//   - pictures in images/ stay small: JPEG/PNG/GIF under 3 MB each
// Also checks skills/README.md's links, and that it lists every skill.
// Usage: node scripts/hooks/check-skills.mjs
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';

const ROOT = 'skills';
const REF = 'https://treg.to/?ref=matthewdonse-aebsh';
const bad = [];

function links(file) {
  const s = readFileSync(file, 'utf8');
  for (const m of s.matchAll(/\]\(([^)\s]+)\)/g)) {
    const target = m[1].split('#')[0];
    if (!target || /^(https?:|mailto:)/.test(target)) continue;
    if (!existsSync(join(dirname(file), target))) bad.push(`${file}: broken link ${m[1]}`);
  }
  for (const m of s.matchAll(/https?:\/\/treg\.to[^\s)`"'>]*/g)) {
    const url = m[0].replace(/[.,;:]+$/, '');
    if (url === REF || url.startsWith('https://treg.to/install.sh') || url.includes('treg.to/m/') || url.includes('treg\\.to/m/')) continue;
    bad.push(`${file}: treg link "${url}" is not the referral link ${REF}`);
  }
  return s;
}

if (!existsSync(ROOT)) process.exit(0);
const skills = readdirSync(ROOT).filter((d) => !d.startsWith('_') && statSync(join(ROOT, d)).isDirectory());
for (const d of skills) {
  const skill = join(ROOT, d, 'SKILL.md');
  if (!existsSync(skill)) { bad.push(`${ROOT}/${d}: no SKILL.md`); continue; }
  const s = links(skill);
  const fm = s.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) bad.push(`${skill}: no frontmatter`);
  else {
    const name = (fm[1].match(/^name:\s*(.+)$/m) || [])[1];
    if (name?.trim() !== d) bad.push(`${skill}: frontmatter name "${name}" should be "${d}"`);
    if (!/^description:\s*\S/m.test(fm[1])) bad.push(`${skill}: frontmatter has no description`);
  }
  for (const extra of ['README.md', 'assets/MANIFEST.md']) {
    const f = join(ROOT, d, extra);
    if (existsSync(f)) links(f);
  }
  const imgs = join(ROOT, d, 'images');
  if (existsSync(imgs)) {
    for (const f of readdirSync(imgs)) {
      const size = statSync(join(imgs, f)).size;
      if (size > 3 * 1048576) bad.push(`${imgs}/${f} is ${(size / 1048576).toFixed(1)} MB: shrink it (max 1600 px, JPEG q85)`);
    }
  }
}
const index = join(ROOT, 'README.md');
if (existsSync(index)) {
  const s = links(index);
  for (const d of skills) if (!s.includes(`${d}/`)) bad.push(`${index}: doesn't list the skill ${d}`);
}
if (bad.length) {
  console.error('FAIL — skills:');
  for (const b of bad) console.error(`  - ${b.replace(/\\/g, '/')}`);
  process.exit(1);
}
console.log(`check-skills: ${skills.length} skills complete, links and treg referral OK.`);
