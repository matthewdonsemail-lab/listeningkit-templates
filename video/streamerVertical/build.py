"""Build a 9:16 streamer clip in the house style by cloning every style layer from a finished
template project (the NickEh30 GTA 6 v2 edit) onto a new source clip.

    uv run --no-project --with numpy --with pillow python build.py clip.json

clip.json:
{
  "template": ".../projects/nickeh30-gta6-v2.ecproj",
  "out":      ".../projects/<name>.ecproj",
  "source":   ".../<clip>.mp4",                 # full 1280x720 stream clip, webcam top-left
  "transcript": ".../assembly_<clip>.json",     # AssemblyAI words (ms)
  "eyes": [153, 246],                           # findPerson.py --task pose --pick left -> summary.eyes
  "ranges": [[14.9, 20.0], [24.6, 29.5]],       # source spans kept, in order; joins between them are cuts
  "endPad": 0.4,                                # comp ends this long after the last kept word
  "upscaleCloseups": true                       # Real-ESRGAN x4 on the face crops of close-up beats
}

Everything is done headlessly with `effectcraft-cli run --project ... --save` (the GUI crashes under
bursts of edits). Shot rules, captions, swish pans, tile zooms, PiP boxes, SFX and the loop ending all
come from the template layers, so the style can't drift. Run validate.py on the result.
"""
import json, os, re, shutil, subprocess, sys, time

CLI = "C:/Users/0/effectcraft/target/release/effectcraft-cli.exe"
RE = os.path.expandvars("$LOCALAPPDATA") + "/listeningkit/realesrgan/realesrgan-ncnn-vulkan.exe"
FONT = "C:/Users/0/AppData/Local/Microsoft/Windows/Fonts/SFC-Signsmith.ttf"
T = 254016000000  # EffectCraft time units per second
FPS = 30
EMPH = {"no", "wait", "what", "oh", "bro", "dude", "yo", "hey", "stop", "please", "god", "why", "huh", "okay", "ok", "nah", "boom"}
GAME = {"phone", "police", "911", "bus", "car", "cop", "cops", "train", "gun", "station", "driver", "ticket",
        "family-friendly", "experience", "situation", "trouble", "boy", "dog", "dogs", "swim", "fetch", "fudge"}
ROT = {"split": "face", "face": "game", "game": "split"}
STRIP = "'\u2019\u2018,\u2014\u2013"

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
OUT, SRC = cfg["out"], cfg["source"]
EX, EY = cfg["eyes"]
fr = lambda t: round(t * FPS) / FPS


def run(steps, timeout=600):
    f = os.path.join(os.path.dirname(OUT), "_build_steps.json")
    json.dump(steps, open(f, "w"))
    o = subprocess.run([CLI, "run", "--commands", f, "--project", OUT, "--save", "--json"], capture_output=True, text=True, timeout=timeout)
    os.remove(f)
    if o.returncode:
        raise SystemExit("effectcraft-cli failed: " + o.stderr[-800:])
    return [r["result"] for r in json.loads(o.stdout)["result"]]


def comp1(steps):
    return run([{"command": "comp.open", "params": {"comp": 1}}] + steps)[1:]


def cmd(c, **p):
    p.setdefault("comp", 1)
    return {"command": c, "params": p}


def span_steps(lid, a, b):
    """in, out, in, out: works whichever way the layer moves (a single out before in is silently
    clamped when the new out lands before the old in)."""
    return [cmd("layer.timing", layers=[lid], **{"in": a}), cmd("layer.timing", layers=[lid], out=b),
            cmd("layer.timing", layers=[lid], **{"in": a}), cmd("layer.timing", layers=[lid], out=b)]


def project():
    return json.load(open(OUT, encoding="utf-8"))


def get(lid, path):
    o = subprocess.run([CLI, "get", "1", str(lid), path, "--project", OUT], capture_output=True, text=True)
    return json.loads(o.stdout)


t0 = time.time()
say = lambda *a: print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)
shutil.copy(cfg["template"], OUT)
pj = project()
L = pj["items"]["1"]["kind"]["layers"]
orig_ids = [l["id"] for l in L]
byname = {l["name"]: l for l in L}


def scale_of(l):
    g = get(l["id"], "transform/scale")
    return g["value"][0], g.get("expression") or ""


# ---- 1. template layers -------------------------------------------------------------------
tpl = {}
for l in L:
    src = l.get("source", {})
    if l["name"].startswith(("B3PfPBKrfAAR.mp4", "t23yuOW-Ns-6.mp4")) and l["switches"]["video"]:
        s, e = scale_of(l)
        kind = "face" if "Slow push" in e else "game" if abs(s - 266.6667) < 0.1 else "split_bottom" if abs(s - 133.3333) < 0.1 else "split_top" if abs(s - 300) < 0.1 else None
        if kind and kind not in tpl:
            tpl[kind] = l
for k, n in [("caption", "wd_005"), ("swishL", "swish_01_L"), ("swishR", "swish_02_R"), ("tilezoom", "tilezoom_split_01"),
             ("pip_game", "pip_game_05"), ("pip_border", "pip_border_05"), ("pipface", "pipface_01"),
             ("pipface_border", "pipface_border_01"), ("closeup", "closeup_x4_01")]:
    tpl[k] = byname[n]
missing = [k for k in ("face", "game", "split_bottom", "split_top") if k not in tpl]
assert not missing, f"template is missing beat kinds {missing}"
keep = {byname[n]["id"] for n in ("Intro Facecam", "intro_vignette", "unsharp_110_r5", "exposure_out_loop", "sfx_intro_whoosh", "sfx_intro_flash", "sfx_loop_riser")}
# SFX offsets measured on the template: sfx layer start relative to its event
def first(prefix):
    return sorted([l for l in L if l["name"].startswith(prefix)], key=lambda l: l["in_point"])
sw0, tz0 = first("swish")[0], first("tilezoom")[0]
pg = byname["pip_game_05"]
sfx_tpl = {}
for n, ev in [("sfx_whoosh", (sw0["in_point"] + sw0["out_point"]) / 2), ("sfx_tilezoom", tz0["in_point"]),
              ("sfx_boxup", pg["in_point"]), ("sfx_boxpop", pg["in_point"]), ("sfx_boxdown", pg["out_point"])]:
    cand = min((l for l in L if l["name"].startswith(n)), key=lambda l: abs(l["start_time"] - ev))
    sfx_tpl[n] = (cand, (cand["start_time"] - ev) / T, (cand["out_point"] - cand["in_point"]) / T)
say("templates:", {k: v["name"] for k, v in tpl.items()})

# ---- 2. EDL: beats -----------------------------------------------------------------------
words = [dict(t=w["text"], s=w["start"] / 1000, e=w["end"] / 1000) for w in json.load(open(cfg["transcript"], encoding="utf-8"))["words"]]
beats, T_ = [], 0.0
for a, b in cfg["ranges"]:
    ws = [w for w in words if a <= w["s"] < b]
    # split a range into beats at sentence ends (no time removed inside a range)
    cuts = [a]
    for p, w in zip(ws, ws[1:]):
        if p["t"].endswith((".", "!", "?")) and w["s"] - p["e"] >= 0.1 and w["s"] - cuts[-1] >= 1.0:
            cuts.append(fr((p["e"] + w["s"]) / 2))
    cuts.append(b)
    for s0, s1 in zip(cuts, cuts[1:]):
        bw = [w for w in ws if s0 <= w["s"] < s1]
        beats.append(dict(sin=fr(s0), sout=fr(s1), T=fr(T_), words=bw))
        T_ += fr(s1) - fr(s0)
END = fr(beats[-1]["T"] + beats[-1]["sout"] - beats[-1]["sin"])
prev = "face"
for i, bt in enumerate(beats):
    if i == 0:
        bt["kind"] = "face"  # the intro tile zoom lands on his face
        continue
    lw = [w["t"].lower().strip(".,!?") for w in bt["words"]]
    k = "game" if any(w in GAME for w in lw) else "face" if (any(w["t"].endswith(("!", "?")) for w in bt["words"]) or any(w in EMPH for w in lw)) else "split"
    if not bt["words"]:
        k = "game"
    if k == prev:
        k = ROT[k]
    bt["kind"] = prev = k
say("beats:", [(b["kind"], b["T"], round(b["sout"] - b["sin"], 2), " ".join(w["t"] for w in b["words"])) for b in beats], "END", END)

# ---- 3. import + beats -------------------------------------------------------------------
item = run([{"command": "file.import", "params": {"paths": [SRC]}}])[0]["items"][0]
EYEPOS = f"var s=transform.scale[0]/100;[540+(640-{EX})*s,680+(360-{EY})*s,0]"
beat_layers, closeups = [], []
face_n = 0
for i, bt in enumerate(beats):
    if i == 0:
        continue
    dur = bt["sout"] - bt["sin"]
    kinds = ["split_bottom", "split_top"] if bt["kind"] == "split" else [bt["kind"]]
    ids = [comp1([cmd("edit.duplicate", layers=[tpl[k]["id"]])])[0][0] for k in kinds]
    steps = []
    for k, lid in zip(kinds, ids):
        steps += [cmd("layer.replaceSource", layer=lid, item=item),
                  cmd("layer.timing", layers=[lid], start=bt["T"] - bt["sin"]),
                  *span_steps(lid, bt["T"], bt["T"] + dur),
                  cmd("layer.setSwitch", layers=[lid], switch="audio", value=(k != "split_top")),
                  cmd("layer.setSwitch", layers=[lid], switch="video", value=True),
                  cmd("layer.rename", layer=lid, name=f"beat_{i:02d}_{k}")]
        if k == "face":
            s0, s1 = (700, 790) if face_n % 2 == 0 else (790, 700)
            steps += [cmd("prop.setExpression", layer=lid, path="transform/scale",
                          expression=f"// Slow push {'in on' if s0 < s1 else 'out of'} his face across the beat.\n"
                                     f"var u=Math.min(1,Math.max(0,(time-inPoint)/Math.max(0.001,outPoint-inPoint)));var s={s0}+({s1}-{s0})*u;[s,s,100]"),
                      cmd("prop.setExpression", layer=lid, path="transform/position", expression=f"// Eyes ({EX},{EY}) held on the eyeline y=680.\n" + EYEPOS)]
            bt["push"] = (s0, s1)
            face_n += 1
        if k == "split_top":
            steps += [cmd("prop.set", layer=lid, path="transform/position", value=[540 + (640 - 180) * 3, 680 + (360 - EY) * 3, 0]),
                      cmd("layer.mask.shape", layer=lid, mask=1, rect=[0, EY - 680 / 3, 360, 320])]
    comp1(steps)
    bt["ids"] = ids
    beat_layers += ids
say("beats laid:", len(beat_layers))

# ---- 4. intro (beat 0) -------------------------------------------------------------------
b0 = beats[0]
d0 = b0["sout"] - b0["sin"]
intro = byname["Intro Facecam"]["id"]
inner = pj["items"]["13212"]["kind"]["layers"][0]["id"]
run([{"command": "comp.open", "params": {"comp": 13212}},
     {"command": "layer.replaceSource", "params": {"comp": 13212, "layer": inner, "item": item}},
     {"command": "layer.timing", "params": {"comp": 13212, "layers": [inner], "start": -b0["sin"]}},
     {"command": "layer.timing", "params": {"comp": 13212, "layers": [inner], "out": d0}},
     {"command": "layer.timing", "params": {"comp": 13212, "layers": [inner], "in": 0}},
     {"command": "comp.settings", "params": {"comp": 13212, "duration": max(d0, 1.0)}}])
o = subprocess.run([CLI, "get", "13212", str(inner), "transform/position", "--project", OUT], capture_output=True, text=True)
ie = json.loads(o.stdout)["expression"] or ""
ie = re.sub(r"\b152\b", str(EX), re.sub(r"\b254\b", str(EY), ie))
run([{"command": "comp.open", "params": {"comp": 13212}},
     {"command": "prop.setExpression", "params": {"comp": 13212, "layer": inner, "path": "transform/position", "expression": ie}}])
vig = byname["intro_vignette"]["id"]
comp1(span_steps(intro, 0, d0) + span_steps(vig, 0, d0))
say("intro retimed to", d0)

# ---- 5. captions -------------------------------------------------------------------------
meas = subprocess.run(["uv", "run", "--no-project", "--with", "pillow", "python", "-c",
                       "import json,sys;from PIL import ImageFont;f=ImageFont.truetype(sys.argv[1],100);"
                       "print(json.dumps([f.getlength(t) for t in json.loads(sys.argv[2])]))",
                       FONT, json.dumps([("".join(c for c in w["t"] if c not in STRIP)).upper() for bt in beats for w in bt["words"]])],
                      capture_output=True, text=True).stdout
widths = json.loads(meas)
caps, k = [], 0
for bt in beats:
    for w in bt["words"]:
        txt = "".join(c for c in w["t"] if c not in STRIP)
        a = bt["T"] + (w["s"] - bt["sin"])
        caps.append(dict(text=txt, a=fr(a), e=a + (w["e"] - w["s"]), w100=widths[k]))
        k += 1
for i, c in enumerate(caps):
    if i and c["a"] <= caps[i - 1]["a"]:
        c["a"] = caps[i - 1]["a"] + 1 / FPS
for i, c in enumerate(caps):
    nxt = caps[i + 1]["a"] if i + 1 < len(caps) else END
    c["b"] = min(fr(c["e"] + 0.12), nxt, END)
    c["b"] = max(c["b"], min(c["a"] + 2 / FPS, nxt))
    c["size"] = round(min(260, (864 / 1.132 - 56) / (c["w100"] * 1.06 / 100)), 1)
cap_ids = comp1([cmd("edit.duplicate", layers=[tpl["caption"]["id"]]) for _ in caps])
cap_ids = [r[0] for r in cap_ids]
steps = []
for i, (lid, c) in enumerate(zip(cap_ids, caps)):
    steps += [cmd("layer.setText", layer=lid, text=c["text"], size=c["size"], strokeWidth=round(56 * c["size"] / 260, 2)),
              cmd("prop.set", layer=lid, path="transform/anchor", value=[0.0779 * c["size"], -0.39 * c["size"], 0]),
              cmd("layer.timing", layers=[lid], start=c["a"]),
              *span_steps(lid, c["a"], c["b"]),
              cmd("markers.set", layer=lid, index=1, time=c["b"]),
              cmd("markers.set", layer=lid, index=0, time=c["a"]),
              cmd("layer.rename", layer=lid, name=f"cap_{i:03d}")]
comp1(steps)
say("captions:", len(caps))

# ---- 6. swish per cut, tile zoom per split -----------------------------------------------
cuts = [bt["T"] for bt in beats[1:]]
sw_ids = [r[0] for r in comp1([cmd("edit.duplicate", layers=[tpl["swishL" if i % 2 == 0 else "swishR"]["id"]]) for i in range(len(cuts))])]
steps = []
for i, (lid, c) in enumerate(zip(sw_ids, cuts)):
    steps += [*span_steps(lid, c - 0.075, c + 0.075),
              cmd("layer.rename", layer=lid, name=f"swish_{i+1:02d}_{'L' if i % 2 == 0 else 'R'}")]
splits = [bt for bt in beats if bt["kind"] == "split"]
tz_ids = [r[0] for r in comp1([cmd("edit.duplicate", layers=[tpl["tilezoom"]["id"]]) for _ in splits])] if splits else []
for i, (lid, bt) in enumerate(zip(tz_ids, splits)):
    steps += [*span_steps(lid, bt["T"], bt["T"] + bt["sout"] - bt["sin"]),
              cmd("layer.rename", layer=lid, name=f"tilezoom_split_{i+1:02d}")]
comp1(steps)
say("swishes", len(sw_ids), "tile zooms", len(tz_ids))

# ---- 7. PiP boxes ------------------------------------------------------------------------
FX, FY, FS = EX - 130, EY - 150, 300
pips, borders, boxes = [], [], []
for i, bt in enumerate(beats):
    if i == 0 or bt["kind"] not in ("face", "game"):
        continue
    a, b = bt["T"], bt["T"] + bt["sout"] - bt["sin"]
    kb, kd = ("pip_game", "pip_border") if bt["kind"] == "face" else ("pipface", "pipface_border")
    box, brd = [r[0] for r in comp1([cmd("edit.duplicate", layers=[tpl[kb]["id"]]), cmd("edit.duplicate", layers=[tpl[kd]["id"]])])]
    steps = [cmd("layer.replaceSource", layer=box, item=item),
             cmd("layer.timing", layers=[box], start=bt["T"] - bt["sin"])]
    for lid in (box, brd):
        steps += [*span_steps(lid, a, b)]
    # pipface keeps the template's ROUNDED mask path untouched (layer.mask.shape rect would replace it with a
    # square). The webcam sits at the same spot in every NickEh30 clip; re-centre only if the eyes moved > 20 px.
    if kb == "pipface" and (abs(EX - 145) > 20 or abs(EY - 255) > 20):
        steps += [cmd("prop.set", layer=box, path="transform/anchor", value=[165 + EX - 145, 255 + EY - 255, 0])]
    steps += [cmd("layer.rename", layer=box, name=f"{kb}_{i:02d}"), cmd("layer.rename", layer=brd, name=f"{kd}_{i:02d}")]
    comp1(steps)
    boxes.append(box); borders.append(brd); pips.append((a, b))
say("PiP boxes", len(boxes))

# ---- 8. close-up upscale -----------------------------------------------------------------
CX, CY, CW, CH = EX - 105, EY - 115, 224, 312
if cfg.get("upscaleCloseups", True):
    work = os.path.join(os.path.dirname(OUT), "_upscale")
    for i, bt in enumerate(beats):
        if i == 0 or bt["kind"] != "face":
            continue
        f0, f1 = max(0, int(round((bt["sin"] - 0.1) * FPS))), int(round((bt["sout"] + 0.1) * FPS))
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work + "/i"); os.makedirs(work + "/o")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", SRC, "-vf", f"select='between(n\\,{f0}\\,{f1})',crop={CW}:{CH}:{CX}:{CY}",
                        "-fps_mode", "passthrough", work + "/i/%05d.png"], check=True)
        subprocess.run([RE, "-i", work + "/i", "-o", work + "/o", "-n", "realesrgan-x4plus", "-f", "png"], capture_output=True)
        mp4 = os.path.join(os.path.dirname(OUT), "upscaled", f"{os.path.basename(OUT)[:-7]}_closeup_{i:02d}_x4.mp4")
        os.makedirs(os.path.dirname(mp4), exist_ok=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30", "-i", work + "/o/%05d.png", "-c:v", "libx264",
                        "-crf", "14", "-pix_fmt", "yuv420p", mp4], check=True)
        shutil.rmtree(work)
        up = run([{"command": "file.import", "params": {"paths": [mp4]}}])[0]["items"][0]
        lid = comp1([cmd("edit.duplicate", layers=[tpl["closeup"]["id"]])])[0][0]
        s0, s1 = bt["push"]
        dur = bt["sout"] - bt["sin"]
        comp1([cmd("layer.replaceSource", layer=lid, item=up),
               cmd("layer.timing", layers=[lid], start=bt["T"] - bt["sin"] + f0 / FPS),
               *span_steps(lid, bt["T"], bt["T"] + dur),
               cmd("prop.set", layer=lid, path="transform/anchor", value=[(EX - CX) * 4, (EY - CY) * 4, 0]),
               cmd("prop.set", layer=lid, path="transform/position", value=[540, 680, 0]),
               cmd("prop.setExpression", layer=lid, path="transform/scale",
                   expression=f"// Upscaled 4x (Real-ESRGAN x4plus), so scale/4. Slow push.\nvar u=Math.min(1,Math.max(0,(time-inPoint)/Math.max(0.001,outPoint-inPoint)));var s={s0}+({s1}-{s0})*u;[s/4,s/4,100]"),
               cmd("layer.setSwitch", layers=[lid], switch="audio", value=False),
               cmd("layer.setSwitch", layers=[bt["ids"][0]], switch="video", value=False),
               cmd("layer.rename", layer=lid, name=f"closeup_x4_{i:02d}"),
               cmd("layer.arrange", layers=[lid], above=bt["ids"][0])])
        closeups.append(lid)
    say("close-ups upscaled", len(closeups))

# ---- 9. SFX ------------------------------------------------------------------------------
events = [("sfx_whoosh", c) for c in cuts] + [("sfx_tilezoom", bt["T"]) for bt in splits]
for a, b in pips:
    events += [("sfx_boxup", a), ("sfx_boxpop", a), ("sfx_boxdown", b)]
dups = [r[0] for r in comp1([cmd("edit.duplicate", layers=[sfx_tpl[n][0]["id"]]) for n, _ in events])]
steps = []
for j, (lid, (n, ev)) in enumerate(zip(dups, events)):
    st = ev + sfx_tpl[n][1]
    steps += [cmd("layer.timing", layers=[lid], start=st), *span_steps(lid, max(0, st), min(END, st + sfx_tpl[n][2] + max(0, -st))),
              cmd("layer.rename", layer=lid, name=f"{n}_{j:02d}")]
comp1(steps)
say("sfx", len(dups))

# ---- 10. loop ending, cleanup, stack -----------------------------------------------------
exp = byname["exposure_out_loop"]["id"]
riser = byname["sfx_loop_riser"]["id"]
rl = byname["sfx_loop_riser"]
r_dur = (rl["out_point"] - rl["in_point"]) / T
comp1([cmd("comp.settings", duration=END),
       cmd("prop.setExpression", layer=exp, path="effects/#1/master/exposure",
           expression=f"// Exposure ramps out (expo in) over the last 0.6 s to +4, the intro's opening value, so it loops.\n"
                      f"var a={END-0.6:.4f},b={END-1/FPS:.4f};var u=Math.min(1,Math.max(0,(time-a)/(b-a)));u<=0?0:4*Math.pow(2,10*(u-1))"),
       *span_steps(exp, END - 0.7, END),
       cmd("layer.timing", layers=[riser], start=END - r_dur), *span_steps(riser, END - r_dur, END)])
gone = [i for i in orig_ids if i not in keep]
comp1([cmd("edit.clear", layers=gone)])
order = [beat_layers, closeups, borders, boxes, tz_ids, sw_ids, [exp], [byname["unsharp_110_r5"]["id"]], cap_ids]
steps = [cmd("layer.arrange", layers=[lid], to="back") for bt in beats[1:] for lid in bt["ids"]]
steps += [cmd("layer.arrange", layers=[intro], to="back")]
for g in order[2:]:
    steps.append(cmd("layer.arrange", layers=g, to="front"))
steps += [cmd("layer.arrange", layers=[c], above=beats[i]["ids"][0]) for c, i in zip(closeups, [i for i, bt in enumerate(beats) if i and bt["kind"] == "face"])]
comp1(steps)
say("done ->", OUT, f"{len(beats)} beats, {len(caps)} captions, {END:.2f} s")
# captions from the SOURCE transcript are only a first pass: re-time them to the cut's own dialogue
r = subprocess.run(["uv", "run", "--no-project", "--with", "pillow", "python", os.path.join(os.path.dirname(os.path.abspath(__file__)), "resync_captions.py"), OUT],
                   capture_output=True, text=True)
say(r.stdout.strip() or r.stderr[-600:])
json.dump(dict(end=END, beats=[{k: v for k, v in b.items() if k != "words"} | {"words": [w["t"] for w in b["words"]]} for b in beats]),
          open(OUT[:-7] + ".build.json", "w"), indent=1)
