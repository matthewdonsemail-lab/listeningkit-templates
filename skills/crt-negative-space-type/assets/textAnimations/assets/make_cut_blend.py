"""The blend between clips on the launch film's cuts (matt, 2026-11-15), as the reference edits do it
(projects/opening/ref/tt_elements*/: almost every frame has two shots in it). Read off their frames:
  - luma blend: one shot's dark shapes printed into the other's blown-out whites (screen / lighten, overexposed), the
    pair tinted to one colour (cyan, magenta, blue);
  - displacement: one shot pushes the other's pixels around by its brightness, smeared along the rows;
  - datamosh: blocks of the new shot carrying the old shot's pixels, slipping;
  - rectangles of the other shot cut in, echo trails stepping out from the cut;
  - hard 1-frame flicks between the two clips.
For each cut this renders the film's frames around it (from --project, the film without the cut effects), builds an
opaque PNG sequence of the blend (A, the outgoing shot, run backwards past the cut; B, the incoming one, pulled in
early), and writes plugins/launchCutBlend.jsx, which lays them over "launch film" (a rerun replaces them).
  python textAnimations/assets/make_cut_blend.py --project <a .ecproj with the film built, no cut fx>"""
import argparse
import json
import os
import random
import subprocess

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = "C:/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe"
FPS = 30
OUT = os.path.join(HERE, "collage", "cutblend")
ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True)
ap.add_argument("--cuts", default="", help="only these cut indices (comma list), for checking")
a = ap.parse_args()

edit = json.load(open(os.path.join(HERE, "opening_edit.json")))
cuts = sorted({s["in"] for s in edit["shots"] if s["track"] == 1 and s["in"] > 0} | {308})
outro = 711
cuts += [450, 510, outro, 826] + [outro + 211 + round(k * 30 * 201 / 180) for k in range(6)] + [1123, 1749]
cuts = sorted(set(cuts))
only = {int(x) for x in a.cuts.split(",") if x != ""}

# the tints the reference uses, BGR
TINTS = [(255, 230, 120), (240, 90, 230), (255, 140, 40), (230, 255, 200)]


def lum(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255


def tint(img, col, amt):
    """duotone: the frame's brightness mapped from near black to the colour to white"""
    g = lum(img)[:, :, None]
    c = np.array(col, np.float32)[None, None] / 255
    dark = c * 0.08
    duo = np.where(g < 0.6, dark + (c - dark) * (g / 0.6), c + (1 - c) * ((g - 0.6) / 0.4))
    f = img.astype(np.float32) / 255
    return np.clip((f * (1 - amt) + duo * amt) * 255, 0, 255).astype(np.uint8)


def expose(img, stops):
    return np.clip(img.astype(np.float32) * (2 ** stops), 0, 255).astype(np.uint8)


def luma_blend(A, B, m):
    """B's dark shapes printed into A's blown whites (and the other way round as m passes the middle)"""
    hi = A if m < 0.5 else B
    lo = B if m < 0.5 else A
    # both stay readable: the bright one lifted, the other's line work and dark shapes multiplied into it,
    # its highlights screened back on top (a double exposure, as the reference's frames are)
    h = expose(hi, 0.5).astype(np.float32) / 255
    l = lo.astype(np.float32) / 255
    mul = h * np.clip(l * 1.6 + 0.15, 0, 1)
    scr = 1 - (1 - mul) * (1 - np.clip(l - 0.7, 0, 1) * 1.5)
    return np.clip(scr * 255, 0, 255).astype(np.uint8)


def displace(A, B, amt, rnd):
    """A pushed around by B's brightness, along the rows mostly, then smeared"""
    h, w = A.shape[:2]
    g = cv2.GaussianBlur(lum(B), (0, 0), 6)
    xs, ys = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    dx = (g - 0.5) * amt * w * 0.25
    dy = (cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=5)) * amt * 40
    out = cv2.remap(A, xs + dx, ys + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    k = max(3, int(amt * rnd.uniform(40, 120)) | 1)
    smear = cv2.blur(out, (k, 1))
    band = (np.random.default_rng(rnd.randint(0, 1 << 30)).random(h // 6 + 1) < 0.5).repeat(6)[:h][:, None, None]
    return np.where(band, smear, out)


def datamosh(A, B, prevB, amt, rnd):
    """blocks of B carrying A's pixels: where B moved (against its previous frame) A's block slips instead"""
    h, w = A.shape[:2]
    out = B.copy()
    bs = rnd.choice([32, 48, 64])
    diff = cv2.absdiff(lum(B), lum(prevB)) if prevB is not None else np.ones((h, w), np.float32)
    for y in range(0, h, bs):
        for x in range(0, w, bs):
            d = float(diff[y:y + bs, x:x + bs].mean())
            if rnd.random() < amt * (0.4 + 4 * d):
                sx = int(np.clip(x + rnd.randint(-2, 2) * bs, 0, w - bs))
                sy = int(np.clip(y + rnd.randint(-1, 1) * bs // 2, 0, h - bs))
                blk = A[sy:sy + bs, sx:sx + bs]
                out[y:y + blk.shape[0], x:x + blk.shape[1]] = blk[:min(bs, h - y), :min(bs, w - x)]
    return out


def rects(base, other, n, rnd):
    h, w = base.shape[:2]
    out = base.copy()
    for _ in range(n):
        rw, rh = int(w * rnd.uniform(0.1, 0.55)), int(h * rnd.uniform(0.05, 0.35))
        x, y = rnd.randint(0, w - rw), rnd.randint(0, h - rh)
        sx = int(np.clip(x + rnd.uniform(-0.1, 0.1) * w, 0, w - rw))
        out[y:y + rh, x:x + rw] = other[y:y + rh, sx:sx + rw]
    return out


def echo(img, prev, side, rnd):
    """the last frame stepping out behind this one (lighten), a few copies"""
    if prev is None:
        return img
    out = img.copy()
    for s in range(1, rnd.randint(2, 4)):
        sh = np.roll(prev, side * s * rnd.randint(30, 90), axis=1)
        out = np.maximum(out, (sh.astype(np.float32) * (0.75 ** s)).astype(np.uint8))
    return out


def blend_frame(A, B, prevB, prev, k, n, rnd, col):
    """frame k of the window (-n..n, the cut at 0)"""
    m = (k + n) / (2 * n)                       # 0 all A .. 1 all B
    heat = 1 - abs(k) / (n + 1)                 # strongest at the cut
    # the hard flicks: some frames are just one of the two, pushed
    if rnd.random() < 0.22:
        pick = B if rnd.random() < m else A
        return tint(expose(pick, rnd.uniform(0.1, 0.5) * heat), col, 0.3 + 0.3 * heat)
    out = luma_blend(A, B, m)
    if rnd.random() < 0.7:
        src, drv = (out, B) if m < 0.5 else (out, A)
        out = displace(src, drv, 0.3 + 0.9 * heat, rnd)
    if rnd.random() < 0.3 * heat:
        out = datamosh(A if m < 0.5 else out, out if m < 0.5 else B, prevB, 0.15 + 0.5 * heat, rnd)
    if rnd.random() < 0.45:
        out = rects(out, B if m < 0.5 else A, rnd.randint(1, 4), rnd)
    if rnd.random() < 0.5:
        out = echo(out, prev, rnd.choice([-1, 1]), rnd)
    out = expose(out, 0.35 * heat * rnd.uniform(0.5, 1.2))
    return tint(out, col, 0.2 + 0.35 * heat)


os.makedirs(OUT, exist_ok=True)
seqs = []
for ci, c in enumerate(cuts):
    gaps = [c - p for p in cuts if p < c] + [q - c for q in cuts if q > c]
    n = max(3, min(6, (min(gaps) - 1) // 2)) if gaps else 6
    if only and ci not in only:
        seqs.append((c - n, os.path.join(OUT, "cut_%02d" % ci, "b_01.png").replace("\\", "/"), 2 * n + 1))
        continue
    d = os.path.join(OUT, "cut_%02d" % ci)
    os.makedirs(d, exist_ok=True)
    fr = {}
    for f in range(c - n - 1, c + n + 1):
        p = os.path.join(d, "src_%d.png" % f)
        if not os.path.exists(p):
            subprocess.run([CLI, "--project", a.project, "render-frame", "--comp", "launch film", "--frame", str(f),
                            "--out", p], capture_output=True)
        fr[f] = cv2.imread(p)
    rnd = random.Random("blend %d" % c)
    col = TINTS[ci % len(TINTS)]
    prev = None
    for i, k in enumerate(range(-n, n + 1)):
        A = fr[c + k] if k < 0 else fr[max(c - n, c - 1 - k)]            # the outgoing shot, run back past the cut
        B = fr[c + k] if k >= 0 else fr[min(c + n, c - k - 1)]            # the incoming shot, pulled in early
        pB = fr.get(c + k - 1) if k >= 1 else None
        out = blend_frame(A, B, pB, prev, k, n, rnd, col)
        cv2.imwrite(os.path.join(d, "b_%02d.png" % (i + 1)), out)
        prev = out
    seqs.append((c - n, os.path.join(d, "b_01.png").replace("\\", "/"), 2 * n + 1))
    print("cut", ci, c, "window", n)

JSX = r"""// GENERATED by assets/make_cut_blend.py: the blend between clips on the launch film's cuts (luma blend, displacement,
// datamosh, cut-in rectangles, echoes, flicks, tinted), one opaque image sequence per cut over "launch film", under
// the cut fx (launchCutFx.jsx) if they're there. Rerun replaces them.
var D=__DATA__, F=30;
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
var LF=null; for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==="launch film") LF=it;}
if(!LF) throw new Error("no launch film");
for (var k=LF.numLayers;k>=1;k--) if(/^cutblend /.test(LF.layer(k).name)) LF.layer(k).remove();
// below the lowest cut-fx layer, else on top
var below=null; for (var k=LF.numLayers;k>=1;k--) if(/^cutfx /.test(LF.layer(k).name)){ below=LF.layer(k); break; }
for (var i=0;i<D.length;i++){ var s=D[i];
  var f=findFile(s[1]); if(f) f.replace(new File(s[1])); else { var o=new ImportOptions(new File(s[1])); try{o.sequence=true;}catch(e){} f=app.project.importFile(o); }
  try{ f.mainSource.conformFrameRate=F; }catch(e){}
  var L=LF.layers.add(f); L.name="cutblend "+i; L.startTime=s[0]/F; L.inPoint=s[0]/F; L.outPoint=(s[0]+s[2])/F;
  if(below) L.moveAfter(below); else L.moveToBeginning();
}
writeLn("launch film: clip blends on "+D.length+" cuts");
"""
with open(os.path.join(HERE, "..", "plugins", "launchCutBlend.jsx"), "w", encoding="ascii", newline="\n") as fh:
    fh.write(JSX.replace("__DATA__", json.dumps(seqs)))
print("wrote plugins/launchCutBlend.jsx")
