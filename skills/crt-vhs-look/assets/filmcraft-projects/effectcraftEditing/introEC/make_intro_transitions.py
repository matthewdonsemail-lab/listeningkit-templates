"""The cold open's transitions (matt, 2026-11-16: "we're not doing the datamosh with our custom transitions"): the launch
film ending's own (listeningkit-templates textAnimations/assets/make_ending_transitions.py), on every card change of the
intro, from the intro rendered clean (no CRT, so the CRT stays on top in EffectCraft):
  - most cuts: the clip blend (make_cut_blend.py: double exposure, displacement, datamosh, cut-in rectangles, echoes,
    flicks, tint) between the outgoing card and the incoming one, with a pixel-sort burst (make_cut_fx.py) on the cut
  - every third cut: the Edgerunners 2 Teaser #2 red flash (plugins/redflash/seed.py), 5 frames over the cut
Writes trans/cut_NN/t_NN.jpg and trans/cuts.json; intro_trans.jsx places them.
  uv run --no-project --with "opencv-python-headless<5" --with "numpy<3" python make_intro_transitions.py --frames clean"""
import argparse
import json
import os
import random
import shutil
import sys

import cv2
import numpy as np

TA = r"C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TA, "..", "plugins", "redflash"))
import seed as RF  # noqa: E402

OUT = os.path.join(HERE, "trans")
W, H, END = 1920, 1080, 525
ALL = json.load(open(os.path.join(HERE, "all_cuts.json"), encoding="utf-8-sig"))   # [frame, kind]: every cut (matt: "on every cut")
ALL.sort()
CUTS = [c for c, k in ALL]
KIND = {c: k for c, k in ALL}
CARDS = [68, 83, 176, 221, 290, 344, 351, 437, 481]
RED = {CARDS[i] for i in range(len(CARDS)) if i % 3 == 1}                       # the red flash stays on its 3 card changes

# the blend and the pixel sort, from their scripts without running them (as make_ending_transitions.py does)
src = open(os.path.join(TA, "make_cut_blend.py"), encoding="utf8").read()
B = {"np": np, "cv2": cv2, "random": random}
exec(compile(src[src.index("# the tints"):src.index("os.makedirs(OUT, exist_ok=True)")], "make_cut_blend.py", "exec"), B)
fxsrc = open(os.path.join(TA, "make_cut_fx.py"), encoding="utf8").read()
Pn = {"np": np, "cv2": cv2, "random": random}
exec(compile(fxsrc[fxsrc.index("def pixel_sort"):fxsrc.index("for ci, c in enumerate(cuts):")], "make_cut_fx.py", "exec"), Pn)

ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
a = ap.parse_args()


def fr(n):
    return cv2.imread(os.path.join(a.frames, "f_%05d.jpg" % n))


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
placed = []
for ci, c in enumerate(CUTS):
    gp = c - (CUTS[ci - 1] if ci else 0)
    gn = (CUTS[ci + 1] if ci + 1 < len(CUTS) else END) - c
    d = os.path.join(OUT, "cut_%02d" % ci); os.makedirs(d)
    rnd = random.Random("introtrans %d" % c)
    if c in RED and min(gp, gn) >= 6:                           # the red flash
        fl = RF.flash("intro %d" % c)
        pick = [0, 1, 3, 5, 6]                                  # bar, slab, eye, rings, fill
        for j, k in enumerate(pick):
            cv2.imwrite(os.path.join(d, "t_%02d.jpg" % (j + 1)), fl[k], [cv2.IMWRITE_JPEG_QUALITY, 92])
        placed.append({"cut": c, "first": c - 2, "n": len(pick), "kind": "redflash"})
    else:                                                       # the clip blend
        n = max(1, min(4, (min(gp, gn) - 1) // 2))            # tight between the word cards
        fs = {f: fr(f) for f in range(c - n - 1, c + n + 1) if 0 <= f < END}
        col = B["TINTS"][ci % len(B["TINTS"])]
        prev = None
        for j, k in enumerate(range(-n, n + 1)):
            A = fs.get(c + k) if k < 0 else fs.get(max(c - n, c - 1 - k))
            Bf = fs.get(c + k) if k >= 0 else fs.get(min(c + n, c - k - 1))
            img = B["blend_frame"](A, Bf, fs.get(c + k - 1) if k >= 1 else None, prev, k, n, rnd, col)
            if abs(k) <= 1:
                ps = Pn["pixel_sort"](img, "intro %d %d" % (c, k))
                al = ps[:, :, 3:4].astype(np.float32) / 255
                img = (img * (1 - al) + ps[:, :, :3] * al).astype(np.uint8)
            cv2.imwrite(os.path.join(d, "t_%02d.jpg" % (j + 1)), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
            prev = img
        placed.append({"cut": c, "first": c - n, "n": 2 * n + 1, "kind": "blend"})
    print(ci, c, placed[-1]["kind"], placed[-1]["n"], "frames", flush=True)
for p in placed:
    p["path"] = os.path.join(OUT, "cut_%02d" % placed.index(p), "t_01.jpg").replace("\\", "/")
json.dump(placed, open(os.path.join(OUT, "cuts.json"), "w"), indent=1)
