"""Re-time a project's caption words to the cut's OWN dialogue (never the source clip's transcript).

    uv run --no-project --with pillow python resync_captions.py project.ecproj

1. copies the project, mutes every sfx_ layer, renders comp 1's audio to WAV
2. transcribes it with AssemblyAI (`log transcribe file <wav> --json`)
3. rewrites the cap_NNN layers: one per spoken word, text + size + in/out + markers, adding or
   clearing layers so the count matches. Each word leaves 0.12 s after it is spoken, or when the
   next word starts.
"""
import json, os, shutil, subprocess, sys, tempfile
from PIL import ImageFont

CLI = "C:/Users/0/effectcraft/target/release/effectcraft-cli.exe"
FONT = "C:/Users/0/AppData/Local/Microsoft/Windows/Fonts/SFC-Signsmith.ttf"
T, FPS = 254016000000, 30
STRIP = "'\u2019\u2018,\u2014\u2013"
P = sys.argv[1]
fr = lambda t: round(t * FPS) / FPS
tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))


def run(project, steps, save=True):
    f = os.path.join(tmp, "steps.json")
    json.dump([{"command": "comp.open", "params": {"comp": 1}}] + steps, open(f, "w"))
    o = subprocess.run([CLI, "run", "--commands", f, "--project", project] + (["--save"] if save else []) + ["--json"], capture_output=True, text=True)
    if o.returncode:
        raise SystemExit(o.stderr[-600:])
    return [r["result"] for r in json.loads(o.stdout)["result"]][1:]


def cmd(c, **p):
    p.setdefault("comp", 1)
    return {"command": c, "params": p}


def layers(project):
    return json.load(open(project, encoding="utf-8"))["items"]["1"]["kind"]["layers"]


# 1. dialogue-only audio
dlg = os.path.join(tmp, "dialog.ecproj")
shutil.copy(P, dlg)
run(dlg, [cmd("layer.setSwitch", layers=[l["id"] for l in layers(dlg) if l["name"].startswith("sfx_")], switch="audio", value=False)])
wav = os.path.join(tmp, "dialog.wav")
subprocess.run([CLI, "render", "--project", dlg, "--comp", "1", "--out", wav, "--format", "wav"], capture_output=True, check=True)
END = json.load(open(P, encoding="utf-8"))["items"]["1"]["kind"]["duration"] / T

# 2. transcribe
o = subprocess.run(["log", "transcribe", "file", wav, "--json"], capture_output=True, text=True, encoding="utf-8")
words = json.loads(o.stdout[o.stdout.index("{"):o.stdout.rindex("}") + 1])["transcript"]["words"]
caps = []
for w in words:
    txt = "".join(c for c in w["text"] if c not in STRIP).upper()
    if txt.strip(".!?"):
        caps.append(dict(text=txt, a=fr(w["start"] / 1000), e=w["end"] / 1000))
for i, c in enumerate(caps):
    if i and c["a"] <= caps[i - 1]["a"]:
        c["a"] = caps[i - 1]["a"] + 1 / FPS
font = ImageFont.truetype(FONT, 100)
for i, c in enumerate(caps):
    nxt = caps[i + 1]["a"] if i + 1 < len(caps) else END
    c["b"] = min(fr(c["e"] + 0.12), nxt, END)
    c["b"] = max(c["b"], min(c["a"] + 2 / FPS, nxt))
    c["size"] = round(min(260, (864 / 1.132 - 56) / (font.getlength(c["text"]) * 1.06 / 100)), 1)

# 3. rewrite caption layers
cur = sorted([l for l in layers(P) if l["name"].startswith("cap_")], key=lambda l: l["name"])
ids = [l["id"] for l in cur]
if len(caps) > len(ids):
    ids += [r[0] for r in run(P, [cmd("edit.duplicate", layers=[ids[0]]) for _ in range(len(caps) - len(ids))])]
elif len(caps) < len(ids):
    run(P, [cmd("edit.clear", layers=ids[len(caps):])])
    ids = ids[:len(caps)]
steps = []
for i, (lid, c) in enumerate(zip(ids, caps)):
    steps += [cmd("layer.setText", layer=lid, text=c["text"], size=c["size"], strokeWidth=round(56 * c["size"] / 260, 2)),
              cmd("prop.set", layer=lid, path="transform/anchor", value=[0.0779 * c["size"], -0.39 * c["size"], 0]),
              cmd("layer.timing", layers=[lid], start=c["a"]),
              cmd("layer.timing", layers=[lid], **{"in": c["a"]}), cmd("layer.timing", layers=[lid], out=c["b"]),
              cmd("layer.timing", layers=[lid], **{"in": c["a"]}), cmd("layer.timing", layers=[lid], out=c["b"]),
              cmd("markers.set", layer=lid, index=1, time=c["b"]), cmd("markers.set", layer=lid, index=0, time=c["a"]),
              cmd("layer.rename", layer=lid, name=f"cap_{i:03d}")]
steps.append(cmd("layer.arrange", layers=ids, to="front"))
run(P, steps)
shutil.rmtree(tmp)
json.dump(caps, open(P[:-7] + ".captions.json", "w"), indent=1)
print(f"{len(caps)} caption words re-timed to the cut's own dialogue:", " ".join(f'{c["text"]}@{c["a"]:.2f}' for c in caps))
