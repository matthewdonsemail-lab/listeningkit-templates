"""The opening's layers, cut from its stills (projects/opening/, made by images/gen/make_opening_dawn.py):
  layers/being_NN.png   each person as a gold light-being (dawn_light), full-frame RGBA, found where dawn_light and
                        dawn_crowd differ (the people) and grown a little for the glow
  layers/walker_NN.png  the same person from dawn_crowd, for the slow-shutter streak
  layers/crack.png      the black crack from split_cold (dark there, bright marble in dawn_lookup), full-frame RGBA
  layers/beams.png      soft gold sunbeams at the angle of the beams in the stills, to sweep across the floor
  layers/opening.json   the people's boxes, the crack's centre line (for the two halves' masks) and the beam angle"""
import json
import math
import os

import cv2
import numpy as np

OP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "projects", "opening")) + "/"
LY = OP + "layers/"
os.makedirs(LY, exist_ok=True)
W, H = 1920, 1080
im = {n: cv2.imread(OP + n + ".png") for n in ("dawn_empty", "dawn_crowd", "dawn_light", "dawn_lookup", "split_cold")}

# the people: where the light-beings differ from the walkers
lab = lambda x: cv2.cvtColor(cv2.GaussianBlur(x, (5, 5), 0), cv2.COLOR_BGR2LAB).astype(np.float32)
d = np.linalg.norm(lab(im["dawn_light"]) - lab(im["dawn_crowd"]), axis=2)
m = (d > 28).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
n, lab_, stats, _ = cv2.connectedComponentsWithStats(m)
people = []
for k in range(1, n):
    x, y, w, h, a = stats[k]
    if a < 2500 or h < 60:
        continue
    pm = (lab_ == k).astype(np.uint8) * 255
    pm = cv2.dilate(pm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    alpha = cv2.GaussianBlur(pm, (0, 0), 6)
    i = len(people)
    cv2.imwrite(LY + "being_%02d.png" % i, np.dstack([im["dawn_light"], alpha]))
    cv2.imwrite(LY + "walker_%02d.png" % i, np.dstack([im["dawn_crowd"], alpha]))
    people.append({"i": i, "box": [int(x), int(y), int(w), int(h)], "cx": float(x + w / 2), "cy": float(y + h / 2)})

# the crack: near-black in split_cold where dawn_lookup is bright marble
v_split = cv2.cvtColor(im["split_cold"], cv2.COLOR_BGR2HSV)[:, :, 2]
v_look = cv2.cvtColor(im["dawn_lookup"], cv2.COLOR_BGR2HSV)[:, :, 2]
c = ((v_split < 45) & (v_look > 105)).astype(np.uint8)
c = cv2.morphologyEx(c, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
n, cl, st, _ = cv2.connectedComponentsWithStats(c)
keep = np.zeros_like(c)
for k in range(1, n):
    x, y, w, h, a = st[k]
    if a > 150 and max(w, h) > 60:  # long thin pieces, not specks
        keep[cl == k] = 1
crack_a = cv2.GaussianBlur(keep * 255, (3, 3), 0)
cv2.imwrite(LY + "crack.png", np.dstack([np.zeros((H, W, 3), np.uint8) + 8, crack_a]))
ys, xs = np.nonzero(keep)
# its centre line: bin along the diagonal it runs (top right to bottom left), the median across each bin
u = (xs - ys)  # along: x falls as y rises
order = np.argsort(-u)
pts = []
for chunk in np.array_split(order, 16):
    if len(chunk):
        pts.append([float(np.median(xs[chunk])), float(np.median(ys[chunk]))])
pts.sort(key=lambda p: p[1])  # top to bottom
# carry it off both edges of the frame
(x0, y0), (x1, y1) = pts[0], pts[1]
pts.insert(0, [x0 + (x0 - x1) * 50, y0 + (y0 - y1) * 50])
(xa, ya), (xb, yb) = pts[-2], pts[-1]
pts.append([xb + (xb - xa) * 50, yb + (yb - ya) * 50])

# the beams' angle: the dominant orientation of the large bright streaks in the empty hall
g = cv2.cvtColor(im["dawn_empty"], cv2.COLOR_BGR2GRAY).astype(np.float32)
band = cv2.GaussianBlur(g, (0, 0), 6) - cv2.GaussianBlur(g, (0, 0), 40)
gx, gy = cv2.Sobel(band, cv2.CV_32F, 1, 0, 5), cv2.Sobel(band, cv2.CV_32F, 0, 1, 5)
jxx, jyy, jxy = (gx * gx).sum(), (gy * gy).sum(), (gx * gy).sum()
grad = 0.5 * math.atan2(2 * jxy, jxx - jyy)  # the gradient's direction; the beams run across it
beam = math.degrees(grad) + 90
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = math.radians(beam)
across = -xx * math.sin(t) + yy * math.cos(t)
rng = np.random.default_rng(5)
b = np.zeros((H, W), np.float32)
for _ in range(9):  # soft stripes of different widths and strengths
    c0, wdt, s = rng.uniform(-W, 2 * W), rng.uniform(25, 110), rng.uniform(0.35, 1.0)
    b += s * np.exp(-((across - c0) / wdt) ** 2)
b = np.clip(b, 0, 1)
gold = np.zeros((H, W, 3), np.float32) + np.array([120, 200, 255], np.float32)  # BGR warm gold
cv2.imwrite(LY + "beams.png", np.dstack([gold, b * 200]).astype(np.uint8))

json.dump({"people": people, "crack": pts, "beamAngle": beam}, open(LY + "opening.json", "w"), indent=1)
print(len(people), "people,", int(keep.sum()), "crack px, beam angle %.1f" % beam)
