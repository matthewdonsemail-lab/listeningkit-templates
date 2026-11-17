"""The launch film's captions (matt, 2026-11-15). Every word of the VO (projects/cyberpunk/audio_words.json) is on
screen, a few words at a time: the VO is cut into cards of 1-3 words (a card never runs across a full stop or comma
break), and each card cuts on at its first word, sits still (it never moves or scales), and is cut away by the next
card, which lands in a DIFFERENT negative space. Typography, not subtitles: the fewer the words, the bigger the type.

Where each card goes is measured from the film itself (a caption-free render of "launch film", --frames): every
frame in the card's time gets a busyness map (edges + local contrast, after a median blur so the VHS grain and the
CRT's RGB stripes don't count), and the card's text box is slid over it; the least busy spot that doesn't overlap the
last card's spot wins, inside the 4:3 picture before the drop; the ending is type on black (plugins/endingType.jsx). If the empty space there is bright (over 45% grey), the card is black instead of white.

The cards go INSIDE each part of the film, under its look: in "opening" under the VHS look, side bars and CRT, in
"cyberpunk" under its CRT, in "ending" under its thermogram flashes, so the CRT runs over the type too.
Writes plugins/launchCaptions.jsx (a rerun replaces every caption layer it made) and assets/launch_captions_placed.json.
  python assets/make_launch_captions.py --frames <dir of a caption-free quarter render at 6 fps: f_00000.png ...>
  effectcraft-cli --project textAnimations.ecproj script plugins/launchCaptions.jsx --save   (or File > Scripts)"""
import argparse
import glob
import json
import os
import re

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
ap.add_argument("--fps", type=float, default=6)
a = ap.parse_args()

SECTIONS = [("opening", 0.0, 15.0, 0.0), ("cyberpunk", 15.0, 37.43, 263 / 30), ("ending", 37.43, 61.30, 37.43)]  # comp, from, to, its start in launch film
DROP = 308 / 30
SMALL = 46  # Intro 1's connectives: small, wide tracking


def key_size(word):  # Intro 1's key word: huge, the shorter the bigger
    n = len(word)
    return 280 if n <= 3 else 230 if n <= 5 else 190 if n <= 8 else 150


def fix(word):  # the transcript's mishearing
    return word.replace("Noose", "Nous")


words = [(fix(w["w"].strip()), w["s"], w["e"]) for w in json.load(open(os.path.join(ROOT, "projects", "cyberpunk", "audio_words.json"), encoding="utf8"))]

# --- the cards: 1-3 words, broken at punctuation, "Listening Kit" kept together
raw, cur = [], []
for i, (w, s, e) in enumerate(words):
    cur.append((w, s, e))
    nxt = words[i + 1][0] if i + 1 < len(words) else ""
    brk = bool(re.search(r"[.,?!]$", w)) or len(cur) == 3 or (len(cur) == 2 and len(w) + len(cur[0][0]) > 14)
    if w.startswith("Listening") and nxt.startswith("Kit"):
        brk = False
    if brk or i + 1 == len(words):
        raw.append(cur); cur = []
cards = []
for ci, c in enumerate(raw):
    t0 = c[0][1]
    t1 = raw[ci + 1][0][1] if ci + 1 < len(raw) else c[-1][2] + 0.6
    t1 = min(t1, c[-1][2] + 0.9)  # a long pause after it: the type goes, the frame breathes
    cards.append({"words": c, "text": " ".join(w.upper() for w, _, _ in c), "t0": t0, "t1": t1})

# --- the film's empty space
files = sorted(glob.glob(os.path.join(a.frames, "f_*.png")))
frames = [cv2.imread(f) for f in files]
h, w = frames[0].shape[:2]
k = 1920 / w


def busy(img):
    img = cv2.medianBlur(img, 5)
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    ed = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
    mu = cv2.blur(g, (9, 9)); var = cv2.blur(g * g, (9, 9)) - mu * mu
    return cv2.GaussianBlur(ed / 255 + np.sqrt(np.maximum(var, 0)) / 40, (0, 0), 3)


def layout(c, scale):
    """Intro 1's stacked card: the key word (the longest) huge, the words before it small above, the words after it
    small below. Lines: [(words, size)]; returns lines and the block's width and height in frame px."""
    ws = c["words"]
    ki = max(range(len(ws)), key=lambda i: len(ws[i][0].strip(".,?!")))
    big = int(key_size(ws[ki][0].strip(".,?!")) * scale)
    lines = [(ws[:ki], SMALL), (ws[ki:ki + 1], big), (ws[ki + 1:], SMALL)]
    lines = [(l, z) for l, z in lines if l]
    width = max(len(" ".join(x[0] for x in l)) * z * (0.66 if z >= 100 else 0.80) + 40 for l, z in lines)
    height = sum(z * (0.92 if z >= 100 else 1.25) for _, z in lines)
    return lines, width / k, height / k


placed, prev = [], None
for c in cards:
    t0, t1 = c["t0"], c["t1"]
    idx = list(range(int(t0 * a.fps), min(len(frames), max(int(t0 * a.fps) + 1, int(t1 * a.fps)))))
    m = np.max([busy(frames[i]) for i in idx], axis=0).copy()
    # a card across a cut: prefer a spot whose brightness holds, so black or white stays readable the whole time
    lums = [cv2.GaussianBlur(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255, (0, 0), 6) for i in idx]
    if len(lums) > 1:
        m += 2.5 * np.std(lums, axis=0)
    x0, x1 = (240 / k + 12, w - 240 / k - 12) if t0 < DROP else (12, w - 12)
    blank = float(np.percentile(m, 95)) < 0.08  # nothing on screen (the ending's black): compose instead of measure
    if blank:
        ci_ = len(placed)
        spots = [(0.27, 0.30), (0.73, 0.70), (0.27, 0.72), (0.73, 0.28), (0.5, 0.5), (0.30, 0.50), (0.70, 0.50)]
        order = spots[ci_ % len(spots):] + spots[:ci_ % len(spots)]
        m = np.ones_like(m)
        for j_, (fx, fy) in enumerate(order):  # the first spot in this card's turn is emptiest; never the last card's
            yy_, xx_ = np.mgrid[0:h, 0:w]
            m = np.minimum(m, 0.02 * j_ + 0.6 * np.hypot((xx_ - fx * w) / w, (yy_ - fy * h) / h))
    ii = cv2.integral(m)
    scale = 1.5 if blank else 1.0
    while True:
        lines, bw, bh = layout(c, scale)
        bestv, best = 1e9, None
        if bw < x1 - x0:
            for cy in np.arange(10 + bh / 2, h - 10 - bh / 2 + 1, 4):
                for cx in np.arange(x0 + bw / 2, x1 - bw / 2 + 1, 4):
                    l, r, tp, bt = int(cx - bw / 2), int(cx + bw / 2), int(cy - bh / 2), int(cy + bh / 2)
                    v = (ii[bt, r] - ii[tp, r] - ii[bt, l] + ii[tp, l]) / max(1, (r - l) * (bt - tp))
                    if prev is not None:  # cut to a different negative space: never where the last card was
                        px, py, pw, ph = prev
                        ox = max(0, min(r, px + pw / 2) - max(l, px - pw / 2)); oy = max(0, min(bt, py + ph / 2) - max(tp, py - ph / 2))
                        if ox * oy > 0:
                            v += 3
                    if v < bestv:
                        bestv, best = v, (cx, cy, bw, bh)
        if (best is not None and (bestv < 0.5 or scale <= 0.8)) or scale < 0.3 or (blank and best is not None):
            break
        scale *= 0.9
    if best is None:
        lines, bw, bh = layout(c, scale); best = (w / 2, h / 2, bw, bh)
    cx, cy, bw, bh = best
    prev = best
    reg = [cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)[max(0, int(cy - bh / 2)):int(cy + bh / 2), max(0, int(cx - bw / 2)):int(cx + bw / 2)] for i in idx]
    lum = float(np.mean([r.mean() for r in reg])) / 255
    # aligned like Intro 1: to the side of the frame the block sits on, its lines stacked from the block's top
    just = "L" if cx < w / 2 else "R"
    ax = round((cx - bw / 2) * k + 20) if just == "L" else round((cx + bw / 2) * k - 20)
    yy, out_lines = (cy - bh / 2) * k, []
    for l, z in lines:
        lh = z * (0.92 if z >= 100 else 1.25)
        out_lines.append({"words": [[w_.upper(), s_] for w_, s_, _ in l], "size": z, "y": round(yy + lh * 0.82)})
        yy += lh
    c.update({"x": ax, "just": just, "lines": out_lines, "ink": "black" if lum > 0.45 else "white",
              "lum": round(lum, 2), "busy": round(float(bestv), 2)})
    placed.append(c)
    print("%-26s %5.2f-%5.2f %s at %4d  %s  %s" % (c["text"], t0, t1, just, ax,
          " / ".join("%s@%d" % (" ".join(x[0] for x in L["words"]), L["size"]) for L in out_lines), c["ink"]))
json.dump([{k_: v for k_, v in c.items() if k_ != "words"} for c in placed],
          open(os.path.join(HERE, "launch_captions_placed.json"), "w"), indent=1)

# --- the script
JSX = r"""// GENERATED by assets/make_launch_captions.py: edit that and rerun it. Every word of the launch film's VO, a few at a
// time, each card still and cut into its own negative space, inside "opening" / "cyberpunk" / "ending" under their CRT.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
var LOOK={"Global Scale":1,"Lens Distortions":1,"Monitor":1,"CRT Glow":1,"CRT Effects":1,"Channel Blur":1,"CC":1,"Posterize Time":1,
  "Position Flicker":1,"CRT_LINE":1,"CRT_LINE 2":1,"CRT Mask":1,"Glitches":1,"Distortions":1,"Glow":1,"CC 2":1,"CRT ExposureFIX":1,
  "VHS look":1,"bar left":1,"bar right":1,"exposure cuts":1,"thermal orange":1,"thermal green":1};
var C={}, names=["launch film","opening","cyberpunk","ending"];
for (var n=0;n<names.length;n++){ var c=findComp(names[n]); if(!c) continue; C[names[n]]=c;
  for (var k=c.numLayers;k>=1;k--) if(/^cap /.test(c.layer(k).name)) c.layer(k).remove(); }
function under(c){ var low=null; for (var k=1;k<=c.numLayers;k++) if(LOOK[c.layer(k).name]) low=c.layer(k); return low; }
var count=0;
function cap(comp,name,full,list,tin,tout,x,y,size,ink,just){
  var c=C[comp]; if(!c) return;
  var T=c.layers.addText(full); T.name=name; T.startTime=0; T.inPoint=tin; T.outPoint=tout;
  var u=under(c); if(u) T.moveAfter(u); else T.moveToBeginning();
  var st=T.property('Source Text'), td=st.value;
  td.font='Satoshi'; td.fauxBold=true; td.fontSize=size; td.tracking=size>=100?10:140;   // Intro 1: key tight, connectives wide
  td.fillColor=ink==='black'?[0,0,0]:[1,1,1];
  td.justification=just==='R'?ParagraphJustification.RIGHT_JUSTIFY:ParagraphJustification.LEFT_JUSTIFY;
  st.setValue(td);
  st.expression='var w='+list+',s="";for(var i=0;i<w.length;i++)if(time>=w[i][1])s+=(s?" ":"")+w[i][0];s';
  T.property('Transform').property('Position').setValue([x,y]);   // still: it never moves
  if(ink==='white'){
    var sh=T.property('Effects').addProperty('ADBE Drop Shadow');
    try{ sh.property('Opacity').setValue(60); sh.property('Distance').setValue(0); sh.property('Softness').setValue(24); }catch(e){}
    var ex=T.property('Effects').addProperty('ec.color.exposure'); ex.property('master').property('exposure').setValue(2.4);
    T.property('Effects').addProperty('ADBE Glo2'); }
  count++;
}
__CAPS__
writeLn('launch captions: '+count+' cards, inside opening / cyberpunk / ending under their CRT');
"""
lines = []
for ci, c in enumerate(placed):
    for comp, a0, a1, start in SECTIONS:
        t0, t1 = max(c["t0"], a0), min(c["t1"], a1)
        if t1 - t0 < 0.02:
            continue
        for li, L in enumerate(c["lines"]):
            rev = [[w_, round(s_ - start, 3)] for w_, s_ in L["words"]]
            lines.append("cap(%s,%s,%s,%s,%.3f,%.3f,%d,%d,%d,%s,%s);" % (json.dumps(comp), json.dumps("cap %03d.%d" % (ci + 1, li + 1)),
                         json.dumps(" ".join(x[0] for x in L["words"]), ensure_ascii=True), json.dumps(json.dumps(rev, ensure_ascii=True)),
                         t0 - start, t1 - start, c["x"], L["y"], L["size"], json.dumps(c["ink"]), json.dumps(c["just"])))
with open(os.path.join(HERE, "..", "plugins", "launchCaptions.jsx"), "w", encoding="ascii", newline="\n") as fh:
    fh.write(JSX.replace("__CAPS__", "\n".join(lines)))
print("%d cards, every VO word (%d) placed; wrote plugins/launchCaptions.jsx" % (len(placed), sum(len(c["words"]) for c in placed)))
