"""20min-v11 (matt, 2026-11-17): 20min-v10 plus the EffectCraft intro and a riser.
  - the intro (introEC/intro_render.mp4, introEC.ecproj comp "intro", 17.5 s) on a new top track V3 over 0-17.5 s
  - a riser (sfx_riser/riser_stretched.wav: YouTube 8p0Tt8yTJqU "Riser Sound Effect | No Copyright Free To Use",
    stretched 2x with atempo, peak at 10.25 s) on a new A5 from 7.13 s, so it peaks on the drop into the body (17.38 s),
    -8 dB so it sits under the voice
  - the captions without the intro's cues (the intro has its own type): effectcraftEditing-captions-20min-v11.srt
Writes into effectcraftEditing-20min-v11.fcproj (a copy of v10)."""
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
CLI = str(ROOT.parents[1] / "target/release/filmcraft-cli.exe")
P = str(ROOT / "effectcraftEditing-20min-v11.fcproj")
TPF = 254_016_000_000 // 60
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
seq = run(["--project", P, "inspect", "sequence", "--compact"])[0]["id"]
intro = run(["--project", P, "--save", "import", str(ROOT / "introEC/intro_render.mp4")])[0]["items"][0]
riser = run(["--project", P, "--save", "import", str(ROOT / "sfx_riser/riser_stretched.wav")])[0]["items"][0]
cmds = [{"id": "sequence.open", "params": {"item": seq}}, {"id": "sequence.addTracks", "params": {"video": 1, "audio": 1}}]
cmds += [{"id": "timeline.setTargeting", "params": {"track": t, "sourcePatch": False}} for t in ("A1", "A2", "A3", "A4", "A5")]
cmds += [{"id": "timeline.place", "params": {"item": intro, "track": "V3", "frame": 0, "sourceIn": 0, "duration": 1050 * TPF}},
         {"id": "timeline.place", "params": {"item": riser, "track": "A5", "frame": 428, "sourceIn": 0, "duration": 683 * TPF}},
         {"id": "captions.deleteTrack", "params": {"track": "C1"}},
         {"id": "captions.import", "params": {"path": str(ROOT / "effectcraftEditing-captions-20min-v11.srt"), "name": "EffectCraft Walkthrough captions"}},
         {"id": "captions.setStyle", "params": {"track": "C1", "align": "left", "anchor": "bottom", "margin": 0.05, "background": True, "size": 36}}]
res = run(["--project", P, "--save", "run", "-"], "\n".join(json.dumps(c) for c in cmds) + "\n")
rclip = [r["result"]["clips"][0] for r in res if r.get("id") == "timeline.place"][1]
run(["--project", P, "--save", "run", "-"], json.dumps({"id": "clip.audioGain", "params": {"clips": [rclip], "mode": "set", "db": -8}}) + "\n")
out = json.loads(subprocess.run([CLI, "--project", P, "inspect", "sequence", "--compact"], capture_output=True, text=True, cwd=ROOT.parents[1]).stdout)
v3 = [c for t in out["video"] if t["name"] in ("V3", "Video 3") for c in t["items"]]
a5 = [c for t in out["audio"] if t["name"] in ("A5", "Audio 5") for c in t["items"]]
print("V3:", [(c["startFrame"], c["endFrame"], c["name"]) for c in v3])
print("A5:", [(c["startFrame"], c["endFrame"], c["name"], c.get("gainDb")) for c in a5])
print("duration %.1f s" % (out["durationFrames"] / 60))
