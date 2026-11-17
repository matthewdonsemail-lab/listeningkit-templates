"""20min-v12 (matt, 2026-11-17): 20min-v11 plus
  - the intro without its burn to white (introEC/intro_render.mp4 re-rendered, exposure ramp removed) and instead a
    really quick white flash in FilmCraft on the cut into the body: a white Color Matte on V4, 1048-1054 (60 fps),
    the last 4 frames dissolving out
  - cutaways to the launch film (listeningkit-templates/textAnimations/renders/launch_film_final_full.mp4, picture only)
    when he talks about it, on V4 over the screen and the face: the opener at "to point out the importance ... The Big
    Short", and the matching part of the film for the camera shots, the Playground UI, the trim-path typing, the
    caricatures, the lines, the eyes, the 12 variations, the CRT, the seed lines, the Hermes girl, the transitions and
    "a day and a half"
Writes effectcraftEditing-20min-v12.fcproj (a copy of v11)."""
import json, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
CLI = str(ROOT.parents[1] / "target/release/filmcraft-cli.exe")
P = ROOT / "effectcraftEditing-20min-v12.fcproj"
LAUNCH = r"C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/renders/launch_film_final_full.mp4"
TPS = 254_016_000_000
TPF = TPS // 60
# (edit time s, length s, launch film from s, what he's saying)
CUTAWAYS = [(201.38, 8.0, 0.0, "to point out the importance ... The Big Short: the opener"),
            (240.56, 5.0, 3.5, "the camera shots: Sam at the desk, the blinds"),
            (320.0, 2.2, 2.0, "the Playground UI rebuilt: MAGICAL"),
            (390.39, 2.2, 2.0, "trim path, 'my name's Sam': the typing"),
            (446.22, 5.0, 8.0, "caricatures, 'like aliens': the cyberpsycho men"),
            (464.75, 5.0, 28.0, "the effect done with numpy: the busts with lines"),
            (526.23, 4.0, 18.0, "the eyes bulging: the girl's eyes"),
            (543.8, 5.0, 9.0, "12 variations, eyes cut in boxes: the men"),
            (735.2, 4.0, 22.0, "the CRT: the Hermes girl section"),
            (762.94, 5.0, 29.0, "lines from a seed: the busts"),
            (903.57, 5.0, 44.0, "it cuts through the Hermes girl: the ending"),
            (931.8, 6.0, 37.0, "the transitions: the ending's"),
            (1264.79, 5.0, 57.5, "a day and a half: the end card")]
if P.exists():
    raise SystemExit("v12 exists; not overwriting")
shutil.copy(ROOT / "effectcraftEditing-20min-v11.fcproj", P)


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


seq = run(["--project", str(P), "inspect", "sequence", "--compact"])[0]["id"]
launch = run(["--project", str(P), "--save", "import", LAUNCH])[0]["items"][0]
res = run(["--project", str(P), "--save", "run", "-"], json.dumps({"id": "file.newColorMatte", "params": {"color": "#ffffff", "seconds": 1.0}}) + "\n")
white = res[0]["result"]["item"] if "item" in res[0]["result"] else res[0]["result"]["items"][0]
cmds = [{"id": "sequence.open", "params": {"item": seq}}, {"id": "sequence.addTracks", "params": {"video": 1}}]
cmds += [{"id": "timeline.setTargeting", "params": {"track": t, "sourcePatch": False}} for t in ("A1", "A2", "A3", "A4", "A5")]
for t, ln, src, _ in CUTAWAYS:
    cmds.append({"id": "timeline.place", "params": {"item": launch, "track": "V4", "frame": round(t * 60),
                                                    "sourceIn": round(src * TPS), "duration": round(ln * 60) * TPF}})
cmds.append({"id": "timeline.place", "params": {"item": white, "track": "V4", "frame": 1048, "sourceIn": 0, "duration": 6 * TPF}})
res = run(["--project", str(P), "--save", "run", "-"], "\n".join(json.dumps(c) for c in cmds) + "\n")
placed = [r["result"]["clips"][0] for r in res if r.get("id") == "timeline.place"]
run(["--project", str(P), "--save", "run", "-"],
    json.dumps({"id": "sequence.applyVideoTransition", "params": {"clip": placed[-1], "effect": "cross_dissolve", "frames": 4, "edge": "out"}}) + "\n")
out = json.loads(subprocess.run([CLI, "--project", str(P), "inspect", "sequence", "--compact"], capture_output=True, text=True, cwd=ROOT.parents[1]).stdout)
v4 = [c for t in out["video"] if t["name"] in ("V4", "Video 4") for c in t["items"]]
print("V4:", len(v4), "clips:", [(c["startFrame"], c["endFrame"], c["name"][:20]) for c in v4])
print("audio clips on A1-A5:", sum(len(t["items"]) for t in out["audio"]), "| duration %.1f s" % (out["durationFrames"] / 60))
