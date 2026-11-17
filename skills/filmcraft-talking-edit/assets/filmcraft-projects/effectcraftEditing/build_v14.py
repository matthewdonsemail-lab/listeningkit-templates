"""20min-v14 (matt, 2026-11-17): v13 plus the launch film's breakdowns cut in where he talks about them ("we have
other reference material that we can show, like the actual breakdowns of what I was doing"): the 23 full-screen
inserts from make_breakdown_inserts.py (breakdowns/inserts.json), picture only, on V4 between the launch-film cutaways.
Writes effectcraftEditing-20min-v14.fcproj (a copy of v13)."""
import json, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
CLI = str(ROOT.parents[1] / "target/release/filmcraft-cli.exe")
P = ROOT / "effectcraftEditing-20min-v14.fcproj"
TPF = 254_016_000_000 // 60
if P.exists():
    raise SystemExit("v14 exists; not overwriting")
shutil.copy(ROOT / "effectcraftEditing-20min-v13.fcproj", P)


def run(args, payload=None):
    p = subprocess.run([CLI, *args], input=payload, capture_output=True, text=True, cwd=ROOT.parents[1])
    out = []
    for line in p.stdout.splitlines():
        try:
            v = json.loads(line); out.append(v) if isinstance(v, dict) else None
        except json.JSONDecodeError:
            pass
    if not out:
        v = json.loads(p.stdout); out = [v] if isinstance(v, dict) else v
    bad = [r for r in out if not r.get("ok", True)]
    if p.returncode or bad:
        raise SystemExit(f"failed: {bad[:2]} {p.stderr[-400:]}")
    return out


ins = json.load(open(ROOT / "breakdowns/inserts.json"))
seq = run(["--project", str(P), "inspect", "sequence", "--compact"])[0]["id"]
items = run(["--project", str(P), "--save", "import", *[i["file"] for i in ins]])[0]["items"]
assert len(items) == len(ins), (len(items), len(ins))
cmds = [{"id": "sequence.open", "params": {"item": seq}}]
cmds += [{"id": "timeline.setTargeting", "params": {"track": t, "sourcePatch": False}} for t in ("A1", "A2", "A3", "A4", "A5")]
for it, i in zip(items, ins):
    cmds.append({"id": "timeline.place", "params": {"item": it, "track": "V4", "frame": round(i["t"] * 60),
                                                    "sourceIn": 0, "duration": round(i["d"] * 60) * TPF}})
run(["--project", str(P), "--save", "run", "-"], "\n".join(json.dumps(c) for c in cmds) + "\n")
out = json.loads(subprocess.run([CLI, "--project", str(P), "inspect", "sequence", "--compact"], capture_output=True, text=True, cwd=ROOT.parents[1]).stdout)
v4 = sorted([(c["startFrame"], c["endFrame"], c["name"][:24]) for t in out["video"] if t["name"] in ("V4", "Video 4") for c in t["items"]])
print("V4:", len(v4), "clips")
for a, b, n in v4:
    print("  %7.2f-%7.2f %s" % (a / 60, b / 60, n))
bad = [(x, y) for x, y in zip(v4, v4[1:]) if y[0] < x[1]]
print("overlaps:", bad)
print("audio clips:", sum(len(t["items"]) for t in out["audio"]), "| duration %.1f s" % (out["durationFrames"] / 60))
