"""Crazy transitions between the ending's cards (matt, 2026-11-16), from the ending rendered clean (no CRT, so the CRT
stays on top in EffectCraft):
  - most cuts: the clip blend (make_cut_blend.py: double exposure, displacement, datamosh, cut-in rectangles, echoes,
    flicks, tint) between the outgoing card and the incoming one, a few frames either side, with a pixel-sort burst
    (make_cut_fx.py) on the cut frames
  - every third cut: the red flash from Edgerunners 2 Teaser #2 (plugins/redflash/seed.py, seeded from its frames
    23-29 with numpy), 5 frames over the cut, a new variation each time
Writes assets/collage/endtrans/cut_NN/t_NN.jpg and cuts.json; plugins/endingTransitions.jsx places them.
  python textAnimations/assets/make_ending_transitions.py --frames <dir of f_NNNNN.jpg> --project <.ecproj>"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugins", "redflash"))
import seed as RF  # noqa: E402

CLI = "C:/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe"
OUT = os.path.join(HERE, "collage", "endtrans")
W, H = 1920, 1080

# the blend and the pixel sort, from their scripts without running them
src = open(os.path.join(HERE, "make_cut_blend.py"), encoding="utf8").read()
B = {"np": np, "cv2": cv2, "random": random}
exec(compile(src[src.index("# the tints"):src.index("os.makedirs(OUT, exist_ok=True)")], "make_cut_blend.py", "exec"), B)
fxsrc = open(os.path.join(HERE, "make_cut_fx.py"), encoding="utf8").read()
Pn = {"np": np, "cv2": cv2, "random": random}
exec(compile(fxsrc[fxsrc.index("def pixel_sort"):fxsrc.index("for ci, c in enumerate(cuts):")], "make_cut_fx.py", "exec"), Pn)

DUMP = r"""var C;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==="ending") C=it;}
var s={};for(var k=1;k<=C.numLayers;k++){var L=C.layer(k); if(/^cap /.test(L.name)) s[Math.round(L.inPoint*30)]=1;}
var o=[];for(var f in s) o.push(+f); o.sort(function(a,b){return a-b;}); writeLn("STARTS ["+o.join(",")+"]");"""

ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
ap.add_argument("--project", required=True)
a = ap.parse_args()
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "_d.jsx"); open(tmp, "w").write(DUMP)
r = subprocess.run([CLI, "--project", a.project, "script", tmp], capture_output=True, text=True)
os.remove(tmp)
starts = json.loads(next(l for l in r.stdout.splitlines() if l.startswith("STARTS "))[7:])
cuts = [c for c in starts if c > 0] + [626]                     # every card change, and into the end card
cuts = sorted(set(cuts))


def fr(n):
    return cv2.imread(os.path.join(a.frames, "f_%05d.jpg" % n))


for d in os.listdir(OUT):
    if d.startswith("cut_"):
        shutil.rmtree(os.path.join(OUT, d))
placed = []
for ci, c in enumerate(cuts):
    gp = c - (cuts[ci - 1] if ci else 0)
    gn = (cuts[ci + 1] if ci + 1 < len(cuts) else 716) - c
    d = os.path.join(OUT, "cut_%02d" % ci); os.makedirs(d)
    rnd = random.Random("endtrans %d" % c)
    if ci % 3 == 1 and min(gp, gn) >= 6:                        # the red flash
        fl = RF.flash("end %d" % c)
        pick = [0, 1, 3, 5, 6]                                  # bar, slab, eye, rings, fill
        first = c - 2
        for j, k in enumerate(pick):
            cv2.imwrite(os.path.join(d, "t_%02d.jpg" % (j + 1)), fl[k], [cv2.IMWRITE_JPEG_QUALITY, 92])
        placed.append({"cut": c, "first": first, "n": len(pick), "kind": "redflash"})
    else:                                                       # the clip blend
        n = max(2, min(5, (min(gp, gn) - 1) // 2))
        fs = {f: fr(f) for f in range(c - n - 1, c + n + 1) if 0 <= f < 716}
        col = B["TINTS"][ci % len(B["TINTS"])]
        prev = None
        for j, k in enumerate(range(-n, n + 1)):
            A = fs.get(c + k) if k < 0 else fs.get(max(c - n, c - 1 - k))
            Bf = fs.get(c + k) if k >= 0 else fs.get(min(c + n, c - k - 1))
            img = B["blend_frame"](A, Bf, fs.get(c + k - 1) if k >= 1 else None, prev, k, n, rnd, col)
            if abs(k) <= 1:
                ps = Pn["pixel_sort"](img, "end %d %d" % (c, k))
                al = ps[:, :, 3:4].astype(np.float32) / 255
                img = (img * (1 - al) + ps[:, :, :3] * al).astype(np.uint8)
            cv2.imwrite(os.path.join(d, "t_%02d.jpg" % (j + 1)), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
            prev = img
        placed.append({"cut": c, "first": c - n, "n": 2 * n + 1, "kind": "blend"})
    print(ci, c, placed[-1]["kind"], placed[-1]["n"], "frames")
for p in placed:
    p["path"] = os.path.join(OUT, "cut_%02d" % placed.index(p), "t_01.jpg").replace("\\", "/")
json.dump(placed, open(os.path.join(OUT, "cuts.json"), "w"), indent=1)
