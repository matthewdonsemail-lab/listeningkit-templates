"""The red flash, seeded from the teaser's own frames (matt, 2026-11-15): numpy pulls the shapes out of Edgerunners 2
Teaser #2 at 1:24, frames 23-29 (projects/opening/ref/cyberpunk_edits/QBlPg818lGI/at124/), and the generator makes
new frames from those seeds.

extract  for each frame: the red mask (hue near red, bright, saturated), cleaned; the dark line work inside the red
         (dark pixels enclosed by red, thinned to a skeleton and traced into paths); written to seeds/ as
         seed_NN.png (the red mask) and seed_NN.json (the line paths, the red shapes' outlines)
generate a new frame from a seed: the red mask warped by a smooth random displacement field (big slow folds plus a
         finer tear), flipped / tilted / scaled / slid by the variation, optionally lined up to a path (its main axis
         turned onto the path) and pulled towards a matte's centre; the line paths warped the same way and redrawn
         with the cyberpsycho pen (jittered, new on twos); flat red on near-black, CRT stripe, glow
    generate(seed_index, variation, size=(1920, 1080), path=None) -> BGR uint8
    flash(variation, size, path) -> the 7 seeds in order, each varied
CLI: python seed.py extract
     python seed.py sheet out.jpg       (the 7 teaser frames, then their seed masks, then 3 generated flashes)"""
import glob
import json
import math
import os
import random
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cyberpsycho"))
import cyberpsycho as CP  # noqa: E402

SRC = os.path.normpath(os.path.join(HERE, "..", "..", "..", "projects", "opening", "ref", "cyberpunk_edits", "QBlPg818lGI", "at124"))
SEEDS = os.path.join(HERE, "seeds")
FRAMES = list(range(23, 30))
W, H = 1920, 1080
RED = np.array([75, 30, 235], np.float32)
DARK = np.array([10, 3, 18], np.float32)


def red_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0].astype(int), hsv[:, :, 1], hsv[:, :, 2]
    m = (((h < 12) | (h > 160)) & (s > 110) & (v > 120)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))       # the CRT stripe closes up
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), 1.0)


def skeleton(m):
    sk = np.zeros_like(m)
    el = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    x = m.copy()
    while cv2.countNonZero(x):
        e = cv2.erode(x, el)
        sk |= cv2.subtract(x, cv2.dilate(e, el))
        x = e
    return sk


def trace(sk, min_len=25):
    """skeleton pixels to polylines: contours of the dilated skeleton, halved (each line is traced both ways)"""
    cs, _ = cv2.findContours(cv2.dilate(sk, np.ones((3, 3), np.uint8)), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        c = c[:, 0, :]
        if len(c) < min_len * 2:
            continue
        half = c[:len(c) // 2 + 1:3]
        out.append(half.tolist())
    return out


def extract():
    os.makedirs(SEEDS, exist_ok=True)
    for i, f in enumerate(FRAMES):
        img = cv2.resize(cv2.imread(os.path.join(SRC, "f_%02d.png" % f)), (W, H))
        m = red_mask(img)
        mb = (m > 128).astype(np.uint8) * 255
        # the dark line work inside the red: dark pixels whose surroundings are mostly red
        dark = (255 - mb)
        enclosed = cv2.blur(mb.astype(np.float32) / 255, (41, 41)) > 0.55
        lines = ((dark > 0) & enclosed).astype(np.uint8) * 255
        lines = cv2.morphologyEx(lines, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        paths = trace(skeleton(lines))
        outl, _ = cv2.findContours(mb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imwrite(os.path.join(SEEDS, "seed_%02d.png" % (i + 1)), m)
        json.dump({"frame": f, "red_share": round(float((mb > 0).mean()), 3), "lines": paths,
                   "outlines": [c[:, 0, :].tolist() for c in outl if cv2.contourArea(c) > 400]},
                  open(os.path.join(SEEDS, "seed_%02d.json" % (i + 1)), "w"))
        print("seed", i + 1, "from frame", f, "red", round(float((mb > 0).mean()), 2), len(paths), "line paths")


def field(rnd, cells, amp):
    r = np.random.default_rng(rnd.randrange(1 << 30))
    def one():
        return cv2.resize(r.standard_normal((cells * H // W + 2, cells + 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    return one() * amp, one() * amp


def generate(si, variation, size=(W, H), path=None):
    rnd = random.Random("seed %d %s" % (si, variation))
    m = cv2.imread(os.path.join(SEEDS, "seed_%02d.png" % si), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    meta = json.load(open(os.path.join(SEEDS, "seed_%02d.json" % si)))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # the variation: a flip, a tilt, a scale, a slide; turned onto the path when there is one
    flip = rnd.random() < 0.5
    ang = rnd.uniform(-18, 18)
    if path is not None:
        (x0, y0), (x1, y1) = path[0], path[-1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    sc = rnd.uniform(0.9, 1.25)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), -ang, sc)
    M[0, 2] += rnd.uniform(-0.12, 0.12) * W; M[1, 2] += rnd.uniform(-0.1, 0.1) * H
    if path is not None:
        c = np.mean(np.asarray(path, np.float32), axis=0); M[0, 2] += c[0] - W / 2; M[1, 2] += c[1] - H / 2
    Minv = cv2.invertAffineTransform(M)
    # the warp: big slow folds and a finer tear
    fx1, fy1 = field(rnd, 3, rnd.uniform(40, 90))
    fx2, fy2 = field(rnd, 14, rnd.uniform(6, 16))
    dx, dy = fx1 + fx2, fy1 + fy2
    sx = Minv[0, 0] * (xx + dx) + Minv[0, 1] * (yy + dy) + Minv[0, 2]
    sy = Minv[1, 0] * (xx + dx) + Minv[1, 1] * (yy + dy) + Minv[1, 2]
    if flip:
        sx = W - 1 - sx
    border = 255 if meta["red_share"] > 0.9 else 0
    wm = cv2.remap(m, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=border)
    wm = np.clip((wm - 128) * 3 + 128, 0, 255)                       # crisp edges again
    # the line work: the seed's paths, sent through the same transform, redrawn with the cyberpsycho pen
    pen = CP.Pen(W, H, rnd); pen.k = W / CP.REF_W
    for p in meta["lines"]:
        p = np.asarray(p, np.float32)
        if flip:
            p[:, 0] = W - 1 - p[:, 0]
        q = (M[:, :2] @ p.T).T + M[:, 2]
        ix, iy = np.clip(q[:, 0].astype(int), 0, W - 1), np.clip(q[:, 1].astype(int), 0, H - 1)
        q = q - np.stack([dx[iy, ix], dy[iy, ix]], 1)
        pen.poly(q, [rnd.choice([3, 4, 5]) for _ in q])
    img = np.empty((H, W, 3), np.float32); img[:] = DARK
    a = (wm / 255)[:, :, None]
    img = img * (1 - a) + RED * a
    l = (pen.mask.astype(np.float32) / 255)[:, :, None] * a
    img = img * (1 - l) + DARK * l
    if si == 7:                                                       # the full-red frame: its glitch rows, new each time
        for _ in range(rnd.randint(18, 40)):
            y, bh = rnd.randrange(H), rnd.randint(2, 14)
            x0, x1 = sorted([rnd.randrange(W), rnd.randrange(W)])
            img[y:y + bh, x0:x1] = np.clip(RED + rnd.choice([-60, 45, 80]), 0, 255)
    img *= (0.86 + 0.14 * (np.arange(W) % 3 != 0))[None, :, None]
    img += cv2.GaussianBlur(img, (0, 0), 14) * 0.35
    img += np.random.default_rng(rnd.randrange(1 << 30)).normal(0, 4, (H, W, 1))
    out = np.clip(img, 0, 255).astype(np.uint8)
    return out if size == (W, H) else cv2.resize(out, size, interpolation=cv2.INTER_AREA)


def flash(variation, size=(W, H), path=None):
    return [generate(i, "%s %d" % (variation, i), size, path) for i in range(1, 8)]


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        extract()
    elif sys.argv[1] == "sheet":
        T = (320, 180)
        rows = [np.hstack([cv2.resize(cv2.imread(os.path.join(SRC, "f_%02d.png" % f)), T) for f in FRAMES])]
        rows.append(np.hstack([cv2.cvtColor(cv2.resize(cv2.imread(os.path.join(SEEDS, "seed_%02d.png" % i)), T), cv2.COLOR_BGR2RGB) for i in range(1, 8)]))
        for v in ("a", "b", "c"):
            rows.append(np.hstack(flash(v, T)))
        sheet = np.vstack(rows)
        for r, lab in enumerate(["teaser", "seeds (numpy)", "generated a", "generated b", "generated c"]):
            cv2.putText(sheet, lab, (6, r * 180 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imwrite(sys.argv[2], sheet)
