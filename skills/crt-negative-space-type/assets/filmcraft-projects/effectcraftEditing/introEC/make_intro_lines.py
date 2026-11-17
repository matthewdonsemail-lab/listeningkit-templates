"""The cold open's red lines (matt, 2026-11-16), with the launch film's generator (listeningkit-templates
textAnimations/plugins/redlines), redrawn every frame:
  * slashes: the cyberpsycho lines looping round matt (his cutout matte for that frame, placed as the comp places it:
    scale 225%, position 1442,270), weaving behind him in a band that moves every few frames
  * cracks: running top to bottom down through the card's words on the even cards, bending round each letter (and him)
Mattes: mattes/card_N.png (the cards alone, full text, transparent); cutouts/beat_NN/c_NNN.png (make_face_cutouts.py).
Writes lines/l_NNN.png (RGBA, one per comp frame 0-524).
  uv run --no-project --with "opencv-python-headless<5" --with "numpy<3" python make_intro_lines.py"""
import glob
import json
import os
import shutil
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"C:\Users\0\.buzz\REPOS\listeningkit-templates\textAnimations\plugins\redlines")
import redlines as RL  # noqa: E402

W, H, N = 1920, 1080, 525
STARTS = [0, 68, 83, 176, 221, 290, 344, 351, 437, 481]
BEATS = json.load(open(os.path.join(HERE, "beats.json")))
S, PX, PY = 2.25, 1442, 270                       # the cutout layers' scale and position (anchor 640,360)
M = np.float32([[S, 0, PX - 640 * S], [0, S, PY - 360 * S]])
OUT = os.path.join(HERE, "lines")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)


def person(f):
    """matt's matte in comp space at comp frame f (0 if no cutout there)"""
    t = f / 30
    for j, b in enumerate(BEATS):
        if b["p0"] <= t < b["p1"]:
            k = f - int(round(b["p0"] * 30))
            p = os.path.join(HERE, "cutouts", "beat_%02d" % (j + 1), "c_%03d.png" % k)
            if not os.path.exists(p):
                ps = sorted(glob.glob(os.path.join(HERE, "cutouts", "beat_%02d" % (j + 1), "c_*.png")))
                p = ps[-1]
            a = cv2.imread(p, cv2.IMREAD_UNCHANGED)[:, :, 3]
            return cv2.warpAffine(a, M, (W, H))
    return np.zeros((H, W), np.uint8)


def over(dst, src):
    a = src[:, :, 3:4].astype(np.float32) / 255
    out = dst.astype(np.float32)
    out[:, :, :3] = src[:, :, :3] * a + out[:, :, :3] * (1 - a)
    out[:, :, 3:4] = 255 * (a + out[:, :, 3:4] / 255 * (1 - a))
    return out.astype(np.uint8)


for i, a in enumerate(STARTS):
    b = STARTS[i + 1] if i + 1 < len(STARTS) else N
    m = cv2.imread(os.path.join(HERE, "mattes", "card_%d.png" % (i + 1)), cv2.IMREAD_UNCHANGED)
    text = (m[:, :, 3] > 40).astype(np.uint8) * 255
    ys, xs = np.nonzero(text)
    wl, top, ww, wh = xs.min(), ys.min(), xs.max() - xs.min(), ys.max() - ys.min()
    cx, cy = wl + ww / 2, top + wh / 2
    for j in range(b - a):
        f = a + j
        pm = person(f)
        pmask = (pm > 120).astype(np.uint8) * 255
        im = np.zeros((H, W, 4), np.uint8)
        if pmask.any():
            hug = cv2.dilate(pmask, np.ones((25, 25), np.uint8))
            sl = RL.slashes("intro matt %d" % f, matte=hug, n=3)
            # weave: in a band that moves every 3 frames the slashes go behind him
            rr = np.random.default_rng(f // 3)
            ys2, xs2 = np.nonzero(pmask)
            bx = int(rr.uniform(xs2.min(), xs2.max())); bw_ = int((xs2.max() - xs2.min()) * rr.uniform(0.15, 0.35))
            band = np.zeros((H, W), np.float32); band[:, max(0, bx - bw_):bx + bw_] = 1
            sl[:, :, 3] = (sl[:, :, 3].astype(np.float32) * (1 - band * (pm.astype(np.float32) / 255))).astype(np.uint8)
            im = over(im, sl)
        if i % 2 == 0:
            x0 = cx + (ww * 0.18 if (i // 2) % 2 else -ww * 0.22)
            path = [(x0 + 60, -20), (x0, cy), (x0 - 40, H + 20)]
            cr = RL.cracks("intro card %d f %d" % (i, j), path, avoid=cv2.bitwise_or(text, pmask))
            im = over(im, cr)
        cv2.imwrite(os.path.join(OUT, "l_%03d.png" % f), cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA))
    print("card", i + 1, b - a, "frames", flush=True)
print(len(glob.glob(os.path.join(OUT, "*.png"))), "frames")
