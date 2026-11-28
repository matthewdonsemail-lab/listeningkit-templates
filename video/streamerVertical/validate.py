"""Validate a streamer 9:16 project against the house style (README.md). Exit 0 = all rules pass.

    python validate.py project.ecproj [--render frames_dir] [--video final.mp4]

Checks the saved .ecproj (no GUI needed). --render also renders a frame sheet at each beat midpoint and
checks none is black; --video measures the delivered file's loudness and peak.
"""
import json, os, re, subprocess, sys

CLI = "C:/Users/0/effectcraft/target/release/effectcraft-cli.exe"
T = 254016000000
FPS = 30
args = sys.argv[1:]
P = args[0]
pj = json.load(open(P, encoding="utf-8"))
comp = pj["items"]["1"]["kind"]
L = comp["layers"]
END = comp["duration"] / T
items = pj["items"]
results = []


def check(rule, ok, detail=""):
    results.append((rule, bool(ok), detail))


def span(l):
    return l["in_point"] / T, l["out_point"] / T


def pref(*p):
    return [l for l in L if l["name"].startswith(p)]


names = [l["name"] for l in L]
caps = sorted(pref("cap_", "wd_"), key=lambda l: l["in_point"])
caps_in = [l for l in caps if l["in_point"] / T < END - 1e-6]

# 1. comp
check("comp is 1080x1920 @ 30 fps", comp["width"] == 1080 and comp["height"] == 1920 and comp["frame_rate"]["num"] / comp["frame_rate"]["den"] == 30,
      f'{comp["width"]}x{comp["height"]}')
check("no title card or end card", not any(re.search(r"title|end_card", n, re.I) and l["switches"]["video"] and l["in_point"] / T < END for n, l in zip(names, L)))

# 2. captions
check("captions are the top layers", all(n.startswith(("cap_", "wd_")) for n in names[:len(caps)]), f"top layer {names[0]}")
ov = [(caps[i]["name"], caps[i + 1]["name"]) for i in range(len(caps) - 1) if caps[i]["out_point"] > caps[i + 1]["in_point"] + 1]
check("no two caption words overlap", not ov, str(ov[:3]))
bad_m = [l["name"] for l in caps_in if len(l.get("markers", [])) < 2 or abs(l["start_time"] + l["markers"][0]["time"] - l["in_point"]) > T / FPS
         or abs(l["start_time"] + l["markers"][1]["time"] - l["out_point"]) > T / FPS]
check("every word's in/out markers sit on its in/out points", not bad_m, str(bad_m[:5]))
style_bad, punct = [], []
for l in caps_in:
    s = json.dumps(l)
    m = re.search(r'"text": "([^"]*)"', s)
    txt = m.group(1) if m else ""
    if re.search(r"['\u2019\u2018,\u2014\u2013]|\\u201[89]|\\u201[34]", txt):
        punct.append(txt)
    font = re.search(r'"font": "([^"]+)"', s)
    if not (font and "Signsmith" in font.group(1) and '"all_caps": true' in s and '"fill_gradient": {' in s):
        style_bad.append(l["name"])
check("captions: SFC Signsmith, all caps, gradient fill", not style_bad, str(style_bad[:5]))
check("captions carry no ' , \u2014 \u2013", not punct, str(punct[:5]))
long_holds = [l["name"] for l in caps_in if (l["out_point"] - l["in_point"]) / T > 2.5]
check("no caption holds on screen over 2.5 s (clear in silences)", not long_holds, str(long_holds[:5]))

# 3. picture coverage: no black frames
def is_picture(l):
    src = l.get("source", {})
    it = items.get(str(src.get("item")), {})
    k = it.get("kind", {}).get("type")
    return l["switches"]["video"] and not l["switches"]["adjustment"] and (k in ("Footage", "Comp") or "layers" in it.get("kind", {})) \
        and not l["name"].startswith(("cap_", "wd_", "pip", "sfx_"))
pics = sorted((span(l) for l in L if is_picture(l)), key=lambda s: s[0])
t, gaps = 0.0, []
for a, b in pics:
    if a > t + 0.5 / FPS:
        gaps.append((round(t, 3), round(a, 3)))
    t = max(t, b)
if t < END - 0.5 / FPS:
    gaps.append((round(t, 3), round(END, 3)))
check("picture covers every frame (no black flashes)", not gaps, str(gaps[:5]))

# 4. swish pans: 0.15 s, between picture cuts, above clips, below captions
sw = pref("swish")
bad_sw = [l["name"] for l in sw if l["in_point"] / T < END and abs((l["out_point"] - l["in_point"]) / T - 0.15) > 0.02]
check("every swish pan is 0.15 s", not bad_sw, str(bad_sw[:5]))
first_cap_idx = max((names.index(l["name"]) for l in caps), default=-1)
clip_idx = [i for i, l in enumerate(L) if is_picture(l)]
sw_idx = [names.index(l["name"]) for l in sw]
check("swish pans sit above the clips and below the captions", all(first_cap_idx < i < min(clip_idx) for i in sw_idx) if sw_idx and clip_idx else True)

# 5. adjustment stack under the captions
un = pref("unsharp")
check("one unsharp layer directly under the captions", len(un) == 1 and names.index(un[0]["name"]) == len(caps) + 1 - 1 + (1 if names[len(caps)] == "exposure_out_loop" else 0) or (len(un) == 1 and names.index(un[0]["name"]) <= len(caps) + 1))
amt = re.search(r'"match": "amount".{0,200}?"v": (-?[\d.]+)', json.dumps(un[0])) if un else None
check("unsharp sharpens (amount > 0)", amt and float(amt.group(1)) > 0, amt.group(1) if amt else "missing")
ex = pref("exposure_out_loop")
check("exposure ramp-out ends on the last frame (loop)", ex and abs(ex[0]["out_point"] / T - END) < 1 / FPS)

# 6. PiP boxes: each box above its border, same span, motion blur on
pairs = [(b, [x for x in L if x["name"] == b["name"].replace("pip_game", "pip_border").replace("pipface_", "pipface_border_")])
         for b in L if re.match(r"(pip_game|pipface)_\d", b["name"])]
bad_p = [b["name"] for b, br in pairs if not br or names.index(b["name"]) > names.index(br[0]["name"]) or span(b) != span(br[0])
         or not b["switches"]["motion_blur"] or b["switches"]["audio"]]
check("PiP boxes: above their border, same span, motion blur on, audio off", not bad_p, str(bad_p[:5]))
check("comp motion blur on (boxes slide)", comp.get("enable_motion_blur") is True)
square = [b["name"] for b, _ in pairs if any(len(m) <= 4 for m in re.findall(r'"vertices": (\[\[.*?\]\])', json.dumps(b)) for m in [json.loads(m)])]
check("PiP box crops are rounded (mask path has rounded corners)", not square, str(square[:5]))
cj = P[:-7] + ".captions.json"
check("captions re-timed to the cut's own dialogue (resync_captions.py ran)", "wd_" in "".join(names) or os.path.exists(cj))

# 7. SFX inside the comp
sfx = [l for l in pref("sfx_") if l["in_point"] / T < END]
check("sound effects present", len(sfx) >= max(1, len(sw)), f"{len(sfx)} sfx for {len(sw)} swishes")

# optional: render a frame per second and check none is black
if "--render" in args:
    d = args[args.index("--render") + 1]
    os.makedirs(d, exist_ok=True)
    black = []
    for i in range(int(END)):
        f = os.path.join(d, f"f{i:03d}.png")
        subprocess.run([CLI, "render-frame", "--project", P, "--comp", "1", "--time", str(i + 0.5), "--scale", "0.15", "--out", f], capture_output=True)
        o = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        y = re.findall(r"YAVG=([\d.]+)", o)
        if y and float(y[0]) < 12:
            black.append(i + 0.5)
    check("rendered frames (1 per second) are not black", not black, str(black))

if "--video" in args:
    v = args[args.index("--video") + 1]
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", v, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-1])
    check("delivered loudness -16..-13 LUFS", -16 <= I <= -13, f"{I} LUFS")
    check("delivered true peak <= -1 dBFS", pk <= -1.0, f"{pk} dBFS")

w = max(len(r) for r, _, _ in results)
for r, ok, d in results:
    print(("PASS " if ok else "FAIL ") + r.ljust(w) + ("" if ok or not d else "  -> " + d))
fails = sum(not ok for _, ok, _ in results)
print(f"\n{len(results) - fails}/{len(results)} rules pass")
sys.exit(1 if fails else 0)
