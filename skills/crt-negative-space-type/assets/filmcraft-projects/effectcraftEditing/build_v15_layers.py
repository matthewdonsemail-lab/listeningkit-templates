"""20min-v15 (matt, 2026-11-17): "make the audio gaps shorter, there are moments where I'm not talking; the J-cut stuff
isn't being done with the few frames so it can cut into the next one". The base edit is rebuilt by build_edit.py
(VARIANT=20min TAG=-20min-v15): pauses split on the cleaned dialogue at 0.30 s (PAUSE_SPLIT_S, silent_split) and every
body cut a J-cut of at least 8 frames (JCUT, picture_lag / picture_tail). This script puts back everything v11-v14
added on top of the old 20min-v10 timing, each moved to where the same words now sit:
  - the intro (V3, 0-1050) and the riser (A5, 428, -8 dB): the cold open is unchanged, frame for frame
  - the captions without the intro's cues
  - the white flash (V4, 1048-1054, dissolving out over 4 frames)
  - the launch-film cutaways, the actual Big Short and the 23 breakdown inserts (V4), their edit times mapped
    v10 timeline -> source time -> v15 timeline through the two EDLs
Writes into effectcraftEditing-20min-v15.fcproj (the base is kept as effectcraftEditing-20min-v15-base.fcproj)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLI = str(ROOT.parents[1] / "target/release/filmcraft-cli.exe")
P = ROOT / "effectcraftEditing-20min-v15.fcproj"
shutil.copy(ROOT / "effectcraftEditing-20min-v15-base.fcproj", P)
TPS = 254_016_000_000
TPF = TPS // 60
LAUNCH = r"C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/renders/launch_film_final_full.mp4"
BIGSHORT = r"C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/ref/styleref.mp4"
# from build_v13.py (v10 timing): (edit time s, length s, launch film from s, what he's saying)
CUTAWAYS = [(201.38, 4.4, 0.0, "the opener"), (240.56, 5.0, 3.5, "the camera shots"), (320.0, 2.2, 2.0, "Playground UI"),
            (390.39, 2.2, 2.0, "trim path typing"), (446.22, 5.0, 8.0, "caricatures"), (464.75, 5.0, 28.0, "busts with lines"),
            (526.23, 4.0, 18.0, "the girl's eyes"), (543.8, 5.0, 9.0, "12 variations"), (735.2, 4.0, 22.0, "the CRT"),
            (762.94, 5.0, 29.0, "lines from a seed"), (903.57, 5.0, 44.0, "the Hermes girl"), (931.8, 6.0, 37.0, "transitions"),
            (1264.79, 5.0, 57.5, "a day and a half")]
BIG = (205.8, 234.8)

old = json.load(open(ROOT / "effectcraftEditing-edl-20min-v10.json"))["segments"]
new = json.load(open(ROOT / "effectcraftEditing-edl-20min-v15.json"))["segments"]
body_old = [s for s in old if not s["hook"]]
body_new = [s for s in new if not s["hook"]]


def to_src(t):
    s = [x for x in body_old if x["timeline_start_s"] <= t + 1e-6][-1]
    return s["source_start_s"] + (t - s["timeline_start_s"])


def to_new(t):
    src = to_src(t)
    for s in body_new:
        if s["source_start_s"] - 1e-6 <= src < s["source_end_s"]:
            return s["timeline_start_s"] + (src - s["source_start_s"])
    return [s for s in body_new if s["source_start_s"] > src][0]["timeline_start_s"]


def run(args, payload=None):
    p = subprocess.run([CLI, *args], input=payload, capture_output=True, text=True, cwd=ROOT.parents[1])
    out = []
    for line in p.stdout.splitlines():
        try:
            v = json.loads(line)
            if isinstance(v, dict):
                out.append(v)
        except json.JSONDecodeError:
            pass
    if not out:
        v = json.loads(p.stdout)
        out = [v] if isinstance(v, dict) else v
    bad = [r for r in out if not r.get("ok", True)]
    if p.returncode or bad:
        raise SystemExit(f"failed: {bad[:2]} {p.stderr[-400:]}")
    return out


# captions without the intro's cues
blocks = (ROOT / "effectcraftEditing-captions-20min-v15.srt").read_text(encoding="utf-8").strip().split("\n\n")
keep = []
for b in blocks:
    L = b.split("\n")
    h, m, s, ms = map(int, re.match(r"(\d+):(\d+):(\d+),(\d+)", L[1]).groups())
    if h * 3600 + m * 60 + s + ms / 1000 >= 17.5:
        keep.append("\n".join([str(len(keep) + 1)] + L[1:]))
cap = ROOT / "effectcraftEditing-captions-20min-v15-nointro.srt"
cap.write_text("\n\n".join(keep) + "\n", encoding="utf-8")

# V4 placements in the new timing: (frame, duration frames, item key, source in s)
v4 = [(round(to_new(t) * 60), round(ln * 60), "launch", src) for t, ln, src, _ in CUTAWAYS]
b0, b1 = to_new(BIG[0]), to_new(BIG[1])
v4.append((round(b0 * 60), round((b1 - b0) * 60), "big", 0.0))
ins = json.load(open(ROOT / "breakdowns/inserts.json"))
v4 += [(round(to_new(i["t"]) * 60), round(i["d"] * 60), i["file"], 0.0) for i in ins]
v4.sort()
for k in range(len(v4) - 1):  # never run into the next one
    f, d, it, s = v4[k]
    if f + d > v4[k + 1][0]:
        v4[k] = (f, v4[k + 1][0] - f, it, s)

seq = run(["--project", str(P), "inspect", "sequence", "--compact"])[0]["id"]
files = [str(ROOT / "introEC/intro_render.mp4"), str(ROOT / "sfx_riser/riser_stretched.wav"), LAUNCH, BIGSHORT] + [i["file"] for i in ins]
items = run(["--project", str(P), "--save", "import", *files])[0]["items"]
assert len(items) == len(files), (len(items), len(files))
item = {"intro": items[0], "riser": items[1], "launch": items[2], "big": items[3]}
item.update({i["file"]: items[4 + n] for n, i in enumerate(ins)})
res = run(["--project", str(P), "--save", "run", "-"], json.dumps({"id": "file.newColorMatte", "params": {"color": "#ffffff", "seconds": 1.0}}) + "\n")
white = res[0]["result"]["item"] if "item" in res[0]["result"] else res[0]["result"]["items"][0]

cmds = [{"id": "sequence.open", "params": {"item": seq}}, {"id": "sequence.addTracks", "params": {"video": 2, "audio": 1}}]
cmds += [{"id": "timeline.setTargeting", "params": {"track": t, "sourcePatch": False}} for t in ("A1", "A2", "A3", "A4", "A5")]
cmds += [{"id": "timeline.place", "params": {"item": item["intro"], "track": "V3", "frame": 0, "sourceIn": 0, "duration": 1050 * TPF}},
         {"id": "timeline.place", "params": {"item": item["riser"], "track": "A5", "frame": 428, "sourceIn": 0, "duration": 683 * TPF}},
         {"id": "timeline.place", "params": {"item": white, "track": "V4", "frame": 1048, "sourceIn": 0, "duration": 6 * TPF}}]
for f, d, it, s in v4:
    cmds.append({"id": "timeline.place", "params": {"item": item[it], "track": "V4", "frame": f, "sourceIn": round(s * TPS), "duration": d * TPF}})
cmds += [{"id": "captions.deleteTrack", "params": {"track": "C1"}},
         {"id": "captions.import", "params": {"path": str(cap), "name": "EffectCraft Walkthrough captions"}},
         {"id": "captions.setStyle", "params": {"track": "C1", "align": "left", "anchor": "bottom", "margin": 0.05, "background": True, "size": 36}}]
res = run(["--project", str(P), "--save", "run", "-"], "\n".join(json.dumps(c) for c in cmds) + "\n")
placed = [r["result"]["clips"][0] for r in res if r.get("id") == "timeline.place"]
riser_clip, white_clip, v4clips = placed[1], placed[2], placed[3:]
big_clip = v4clips[[k for k, x in enumerate(v4) if x[2] == "big"][0]]
fx = [{"id": "clip.audioGain", "params": {"clips": [riser_clip], "mode": "set", "db": -8}},
      {"id": "effects.setParam", "params": {"clip": big_clip, "effect": "motion", "param": "scale", "value": 300}},
      {"id": "sequence.applyVideoTransition", "params": {"clip": white_clip, "effect": "cross_dissolve", "frames": 4, "edge": "out"}}]
run(["--project", str(P), "--save", "run", "-"], "\n".join(json.dumps(c) for c in fx) + "\n")

out = json.loads(subprocess.run([CLI, "--project", str(P), "inspect", "sequence", "--compact"], capture_output=True, text=True, cwd=ROOT.parents[1]).stdout)
for name in ("V3", "V4"):
    cl = sorted((c["startFrame"], c["endFrame"], c["name"][:24]) for t in out["video"] if t["name"] in (name, "Video " + name[1:]) for c in t["items"])
    print(name, len(cl), "clips")
    for a, b, n in cl:
        print("   %8.2f-%8.2f %s" % (a / 60, b / 60, n))
print("audio clips:", sum(len(t["items"]) for t in out["audio"]), "| captions:", len(keep), "| duration %.1f s" % (out["durationFrames"] / 60))
