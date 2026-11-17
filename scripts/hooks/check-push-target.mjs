// Pre-push gate: who may push what (ported from listeningkit-frontend).
//
// The owner, matthewdonsemail-lab, may push any branch. Everyone else (an agent identity, a contributor) may only
// push feature branches named `template/*`, never main. matt's own pushes from an agent session go out under his
// identity by prefixing git with GIT_CONFIG_COUNT=0 (see ~/.buzz/AGENTS.md). Set LEFTHOOK=0 only in an emergency.
import { execSync } from 'node:child_process';

const OWNER_IDENTITY = 'matthewdonsemail-lab';

function git(command) {
  try {
    return execSync(`git ${command}`, { encoding: 'utf8' }).trim();
  } catch {
    return '';
  }
}

const user = git('config user.name');
const branch = git('branch --show-current');
if (!branch) {
  console.log('check-push-target: detached HEAD (automation), skipping branch rules.');
  process.exit(0);
}
if (user === OWNER_IDENTITY) {
  console.log(`check-push-target: owner identity, branch "${branch}" allowed.`);
  process.exit(0);
}
if (branch === 'main' || branch === 'master') {
  console.error(`pre-push: FAIL — branch "${branch}" is review-only.`);
  console.error(`  You are pushing as "${user || '(no user.name)'}", not ${OWNER_IDENTITY}.`);
  console.error('  Push a template/* branch and open a PR, or prefix git with GIT_CONFIG_COUNT=0 to use matt\'s identity.');
  process.exit(1);
}
if (!branch.startsWith('template/')) {
  console.error(`pre-push: FAIL — branch "${branch}" breaks the naming rule: non-owner branches are template/<name>.`);
  process.exit(1);
}
console.log(`check-push-target: contributor branch "${branch}" allowed (PR + review required to land).`);
