// Pre-commit gate: staged Python scripts compile (the generators, builders and skill assets are all Python).
// Only checks syntax (py_compile), so it needs no numpy/OpenCV. Usage: node scripts/hooks/check-python.mjs [files...]
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';

const files = process.argv.slice(2).filter((f) => f.endsWith('.py') && existsSync(f));
if (!files.length) process.exit(0);
const py = ['python', 'python3', 'py'].find((p) => spawnSync(p, ['--version']).status === 0);
if (!py) {
  console.log('check-python: no python on PATH, skipped.');
  process.exit(0);
}
const code = 'import os,py_compile,sys,tempfile\nc=os.path.join(tempfile.gettempdir(),"lefthook_check_python.pyc")\nbad=0\nfor f in sys.argv[1:]:\n    try: py_compile.compile(f, doraise=True, cfile=c)\n    except py_compile.PyCompileError as e: print(e.msg); bad=1\nsys.exit(bad)';
const r = spawnSync(py, ['-c', code, ...files], { encoding: 'utf8' });
if (r.status !== 0) {
  console.error('pre-commit: FAIL — Python that does not compile:');
  console.error((r.stdout + r.stderr).trim());
  process.exit(1);
}
console.log(`check-python: ${files.length} file(s) compile.`);
