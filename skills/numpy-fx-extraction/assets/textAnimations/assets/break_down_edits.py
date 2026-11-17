"""Break reference edits down so their looks can be read and reused (matt, 2026-11-15): for each video in a folder
(<dir>/<id>/video.mp4, downloaded with yt-dlp), with numpy / OpenCV
  - cuts: frame-difference peaks, written to cuts.txt (frame, seconds)
  - sheet_NN.jpg: contact sheets, every frame at 6 fps for short edits (<= 70 s), one per shot plus the frames either
    side of each cut for longer ones (trailers), numbered with the source frame
  - stats.json: per shot the mean colour, the share of each colour family, how saturated / bright it is, and how
    busy (edge density), so the palettes and pacing can be compared
  python textAnimations/assets/break_down_edits.py <dir>"""
import glob
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

TW, TH, COLS = 240, 135, 10


def sheet(frames, path):
    rows = (len(frames) + COLS - 1) // COLS
    sh = Image.new("RGB", (COLS * TW, rows * TH))
    for i, (n, f) in enumerate(frames):
        im = Image.fromarray(cv2.cvtColor(cv2.resize(f, (TW, TH), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 44, 12), fill=(0, 0, 0)); d.text((2, 0), str(n), fill=(255, 255, 0))
        sh.paste(im, ((i % COLS) * TW, (i // COLS) * TH))
    sh.save(path, quality=85)


def families(hsv):
    h, s, v = hsv[:, :, 0].astype(int), hsv[:, :, 1], hsv[:, :, 2]
    col = (s > 90) & (v > 60)
    fam = {"red": (h < 8) | (h >= 170), "orange": (h >= 8) & (h < 20), "yellow": (h >= 20) & (h < 35),
           "green": (h >= 35) & (h < 85), "cyan": (h >= 85) & (h < 100), "blue": (h >= 100) & (h < 130),
           "magenta": (h >= 130) & (h < 170)}
    out = {k: round(float((m & col).mean()), 3) for k, m in fam.items()}
    out["black"] = round(float((v < 40).mean()), 3)
    out["white"] = round(float(((s < 40) & (v > 210)).mean()), 3)
    return out


for vid in sorted(glob.glob(os.path.join(sys.argv[1], "*", "video.mp4"))):
    d = os.path.dirname(vid)
    cap = cv2.VideoCapture(vid)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    small, frames = [], []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.resize(f, (320, 180), interpolation=cv2.INTER_AREA))
    n = len(frames)
    diff = np.array([0.0] + [float(np.abs(frames[i].astype(np.int16) - frames[i - 1]).mean()) for i in range(1, n)])
    cuts = [0]
    for i in range(1, n):
        med = float(np.median(diff[max(0, i - 8):i + 8]))
        if diff[i] > 28 and diff[i] > 2.2 * med and i - cuts[-1] >= 2:
            cuts.append(i)
    with open(os.path.join(d, "cuts.txt"), "w") as fh:
        for c in cuts:
            fh.write("%d\t%.2f\n" % (c, c / fps))
    dur = n / fps
    if dur <= 70:
        step = max(1, int(round(fps / 6)))
        pick = list(range(0, n, step))
    else:
        pick = sorted({c for c in cuts} | {max(0, c - 1) for c in cuts} | {min(n - 1, c + 1) for c in cuts})
    per = 100
    for k in range(0, len(pick), per):
        sheet([(i, frames[i]) for i in pick[k:k + per]], os.path.join(d, "sheet_%02d.jpg" % (k // per)))
    shots = []
    bounds = cuts + [n]
    for a, b in zip(bounds, bounds[1:]):
        mid = frames[(a + b) // 2]
        hsv = cv2.cvtColor(mid, cv2.COLOR_BGR2HSV)
        edges = cv2.Canny(cv2.cvtColor(mid, cv2.COLOR_BGR2GRAY), 80, 160)
        shots.append({"from": a, "frames": b - a, "mean_rgb": [int(x) for x in mid.reshape(-1, 3).mean(0)[::-1]],
                      "sat": round(float(hsv[:, :, 1].mean() / 255), 3), "bright": round(float(hsv[:, :, 2].mean() / 255), 3),
                      "busy": round(float((edges > 0).mean()), 3), "colours": families(hsv)})
    lens = [s["frames"] for s in shots]
    json.dump({"fps": fps, "frames": n, "seconds": round(dur, 2), "shots": len(shots),
               "median_shot_frames": float(np.median(lens)), "shots_detail": shots}, open(os.path.join(d, "stats.json"), "w"), indent=1)
    print(os.path.basename(d), "%.1fs" % dur, len(shots), "shots, median", float(np.median(lens)), "frames;",
          len(pick), "thumbs")
