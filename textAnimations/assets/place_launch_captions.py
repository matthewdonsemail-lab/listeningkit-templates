"""Places the launch film's caption cards (make_launch_captions.py CARDS) in each shot's real empty space, measured
from the film itself, and makes them move with it (matt, 2026-11-15: "not going into empty space and moving around").

Input: a caption-free frame sequence of "launch film" (render it at quarter size, 6 fps: --frames DIR). For every card,
each frame in its window gets a busyness map (edges + local contrast, blurred, 0 where the picture is flat); the card's
text box (its width from the words and size) is slid over the frame and the spot with the least busyness wins, kept
inside the 4:3 picture before the drop (the VHS side bars) and off the frame edge. It is found twice, over the first
and the second half of the window, so the card glides from one empty spot to the next as the shot changes; a card too
big for any clean spot shrinks until it fits. Writes assets/launch_captions_placed.json, which make_launch_captions.py
reads for x, y, size and the move.
  python assets/place_launch_captions.py --frames <dir of f_00000.png ...> [--fps 6]"""
import argparse
import glob
import importlib.util
import json
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
ap.add_argument("--fps", type=float, default=6)
a = ap.parse_args()

spec = importlib.util.spec_from_file_location("caps", os.path.join(HERE, "make_launch_captions.py"))
src = open(os.path.join(HERE, "make_launch_captions.py"), encoding="utf8").read()
ns = {"__file__": os.path.join(HERE, "make_launch_captions.py")}
exec(src[:src.index("# each card's words reveal")], ns)  # just CARDS (and what it needs), not the writer
CARDS = ns["CARDS"]

files = sorted(glob.glob(os.path.join(a.frames, "f_*.png")))
frames = [cv2.imread(f) for f in files]
h, w = frames[0].shape[:2]
k = 1920 / w  # frame px -> comp px
DROP = 308 / 30


def busy(img):
    img = cv2.medianBlur(img, 5)  # the VHS grain and the CRT's RGB stripes are not "busy": only real picture is
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    ed = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
    mu = cv2.blur(g, (9, 9)); var = cv2.blur(g * g, (9, 9)) - mu * mu
    b = cv2.GaussianBlur(ed / 255 + np.sqrt(np.maximum(var, 0)) / 40, (0, 0), 3)
    return b


def text_box(text, size):
    return (len(text) * size * 0.70 + 60) / k, size * 1.05 / k  # with the tracking and the glow  # comp size -> frame px (Satoshi bold, caps, tight)


def best(maps, text, size, t):
    bw, bh = text_box(text, size)
    m = np.max(maps, axis=0).copy()  # busy at any moment in this half: avoid it
    if 48.40 <= t < 52.72:  # the research cards: only the bands above and below them are free
        m[int(170 / k):int(950 / k), :] += 5
    elif 37.43 <= t < 58.30:  # the Hermes card fills the frame below its header: captions go above it
        m[int(150 / k):, :] += 5
    x0, x1 = (240 / k, w - 240 / k) if t < DROP else (0, w)
    x0, x1, y0, y1 = x0 + 12, x1 - 12, 10, h - 10
    if bw > x1 - x0 or bh > y1 - y0:
        return None
    ii = cv2.integral(m)
    best_s, best_xy = 1e9, None
    for cy in np.arange(y0 + bh / 2, y1 - bh / 2 + 1, 4):
        for cx in np.arange(x0 + bw / 2, x1 - bw / 2 + 1, 4):
            l, r, tp, bt = int(cx - bw / 2), int(cx + bw / 2), int(cy - bh / 2), int(cy + bh / 2)
            s = (ii[bt, r] - ii[tp, r] - ii[bt, l] + ii[tp, l]) / max(1, (r - l) * (bt - tp))
            s += 0.0004 * ((cx - w / 2) ** 2 + (cy - h / 2) ** 2) / (w * h) * 100  # a nudge toward the frame, not its edge
            if s < best_s:
                best_s, best_xy = s, (cx, cy)
    return best_s, best_xy


out = []
for text, t0, t1, x, y, size, j, note in CARDS:
    f0, f1 = int(t0 * a.fps), max(int(t0 * a.fps) + 1, int(t1 * a.fps))
    idx = [i for i in range(f0, min(f1, len(frames)))] or [min(f0, len(frames) - 1)]
    mid = max(1, len(idx) // 2)
    halves = [idx[:mid], idx[mid:] or idx[:mid]]
    sz = size
    while True:
        res = [best([busy(frames[i]) for i in hh], text, sz, t0) for hh in halves]
        if all(r is not None for r in res) and all(r[0] < 0.55 for r in res) or sz <= int(size * 0.75):
            break
        sz = int(sz * 0.88)
    res = [r if r is not None else (0, (w / 2, h / 2)) for r in res]
    (a_x, a_y), (b_x, b_y) = res[0][1], res[1][1]
    # the move: from the first spot to the second; when the shot hardly changes, a gentle drift so it never sits still
    if np.hypot(b_x - a_x, b_y - a_y) < 6:
        b_x, b_y = a_x + (8 if a_x < w / 2 else -8), a_y - 4
    out.append({"text": text, "t0": t0, "t1": t1, "size": sz, "from": [round(a_x * k), round(a_y * k)],
                "to": [round(b_x * k), round(b_y * k)], "score": round(float(max(res[0][0], res[1][0])), 3), "note": note})
    print("%-22s %5.2f-%5.2f size %3d  %s -> %s  busy %.2f" % (text, t0, t1, sz, out[-1]["from"], out[-1]["to"], out[-1]["score"]))
json.dump(out, open(os.path.join(HERE, "launch_captions_placed.json"), "w"), indent=1)
print("wrote assets/launch_captions_placed.json")
