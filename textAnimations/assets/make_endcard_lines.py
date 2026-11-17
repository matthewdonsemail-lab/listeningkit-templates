"""The end card's cyberpsycho lines (matt, 2026-11-16), as the outro's Nous logo match cut has them
(make_cyberpunk_outro.py lines_over: cyberpsycho.frame out of the logo's matte, (225, 240, 255) with a black edge,
glitched, redrawn on twos):
  nous/  the Nous logo alone, centred (h 700): the lines shooting out of it, 46 frames (the first two loops)
  log/   the Log mark alone, centred (h 760, assets/endcard/log_mark_solo_1080.png rendered from EffectCraft): the
         lines wrapping round it: its own outline pushed out and traced shaky, several times, plus a few jags off it,
         52 frames (the shorter loops up to the glitch)
Writes assets/collage/endcard_lines/<nous|log>/l_NN.png (RGBA); plugins/endingCardSeq.jsx places them.
  python textAnimations/assets/make_endcard_lines.py"""
import math
import os
import random
import shutil
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugins", "cyberpsycho"))
import cyberpsycho as CP  # noqa: E402

OUT = os.path.join(HERE, "collage", "endcard_lines")
W, H = 1920, 1080
COL = (225, 240, 255)

nous = cv2.imread(os.path.join(HERE, "endcard", "nous_logo_white.png"), cv2.IMREAD_UNCHANGED)
s = 700 / nous.shape[0]
nous = cv2.resize(nous, (int(nous.shape[1] * s), 700), interpolation=cv2.INTER_AREA)
nm = np.zeros((H, W), np.uint8)
y0, x0 = (H - 700) // 2, (W - nous.shape[1]) // 2
nm[y0:y0 + 700, x0:x0 + nous.shape[1]] = (nous[:, :, 3] > 128).astype(np.uint8) * 255
lm = (cv2.imread(os.path.join(HERE, "endcard", "log_mark_solo_1080.png"), cv2.IMREAD_GRAYSCALE) > 128).astype(np.uint8) * 255

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for d in ("nous", "log"):
    os.makedirs(os.path.join(OUT, d))

matte = cv2.dilate(nm, np.ones((25, 25), np.uint8))
for f in range(46):
    on2 = f - f % 2
    l = CP.frame("end nous %d" % on2, (W, H), matte, COL, 0.5, outline=(0, 0, 0), outline_px=2)
    l = CP.glitch(l, "end nous %d" % on2, 1.0)
    cv2.imwrite(os.path.join(OUT, "nous", "l_%02d.png" % (f + 1)), cv2.cvtColor(l, cv2.COLOR_RGBA2BGRA))

for f in range(52):
    on2 = f - f % 2
    rnd = random.Random("end log %d" % on2)
    pen = CP.Pen(W, H, rnd)
    for _ in range(rnd.randint(3, 6)):                            # its outline, pushed out, traced round it
        CP.trace(pen, lm, int(rnd.uniform(20, 90) * pen.k) | 1)
    ys, xs = np.nonzero(lm)
    cx, cy = xs.mean(), ys.mean()
    for _ in range(rnd.randint(2, 5)):                            # a few jags and blades off it
        i = rnd.randrange(len(xs))
        o = np.array([xs[i], ys[i]], np.float32)
        a = math.atan2(o[1] - cy, o[0] - cx) + rnd.uniform(-0.7, 0.7)
        (CP.jag if rnd.random() < 0.6 else CP.blade)(pen, o, a)
    l = CP._finish(pen, COL, (0, 0, 0), 2)
    l = CP.glitch(l, "end log %d" % on2, 1.0)
    cv2.imwrite(os.path.join(OUT, "log", "l_%02d.png" % (f + 1)), cv2.cvtColor(l, cv2.COLOR_RGBA2BGRA))
print("end card lines: nous 46, log 52 frames")
