"""The cold open's background as the launch film's numpy cut-up (matt, 2026-11-16: "the numpy thing as a background ...
crazy distorted"), the way make_collage_shots.py / make_cyberpunk_collage.py cut up Intro 1 and the cyberpunk
overhead: the screen-only plate (intro_screen.mp4), every 2 frames a new layout over the current frame: sometimes a
whole other version, otherwise 4-9 rectangles cut from other versions (the same screen 5-60 frames away, inverted, its
channels swapped, posterised, crushed) pasted in place, some blown up around their centre, some nudged, each a touch
brighter or darker so the edges show, and 2-6 thin horizontal slices shifted sideways. The screen keeps its own time.
Writes intro_screen_collage.mp4 (1920x1080, 30 fps, 525 frames).
  uv run --no-project --with "opencv-python-headless<5" --with "numpy<3" python make_screen_collage.py"""
import os
import random
import subprocess

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, N = 1920, 1080, 525
SW, SH = 960, 540                     # worked at half size: it's a background under a gradient and the CRT
cap = cv2.VideoCapture(os.path.join(HERE, "intro_screen.mp4"))
frames = []
while len(frames) < N:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(cv2.resize(f, (SW, SH), interpolation=cv2.INTER_AREA))
n = len(frames)


def variant(img, kind):
    if kind == 0:
        return 255 - img                                                  # inverted
    if kind == 1:
        return img[:, :, [2, 0, 1]]                                       # channels swapped
    if kind == 2:
        return (img // 64) * 64 + 32                                      # posterised
    if kind == 3:
        return np.clip((img.astype(np.int16) - 90) * 2, 0, 255).astype(np.uint8)   # crushed
    return img[:, :, [1, 2, 0]]


ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
                       "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                       os.path.join(HERE, "intro_screen_collage.mp4")], stdin=subprocess.PIPE)
layout = None
for i in range(n):
    if i % 2 == 0:                                                        # a new layout every 2 frames
        rnd = random.Random("screen collage %d" % i)
        layout = {"whole": rnd.random() < 0.18, "wk": rnd.randint(0, 4), "wo": rnd.choice([-40, -20, 20, 40]),
                  "rects": [], "slices": []}
        for _ in range(rnd.randint(4, 9)):
            w_, h_ = int(SW * rnd.uniform(0.12, 0.5)), int(SH * rnd.uniform(0.1, 0.45))
            x, y = rnd.randint(0, SW - w_), rnd.randint(0, SH - h_)
            layout["rects"].append((x, y, w_, h_, rnd.choice([-60, -30, -10, 10, 30, 60]), rnd.randint(-1, 4),
                                    rnd.choice([1.0, 1.0, 1.3, 1.7, 0.7]), rnd.randint(-30, 30), rnd.randint(-20, 20),
                                    rnd.uniform(0.8, 1.25)))
        for _ in range(rnd.randint(2, 6)):
            layout["slices"].append((rnd.randrange(SH), rnd.randint(3, 30), rnd.randint(-120, 120)))
    cur = frames[i]
    out = variant(frames[min(max(i + layout["wo"], 0), n - 1)], layout["wk"]).copy() if layout["whole"] else cur.copy()
    for x, y, w_, h_, off, kind, zoom, nx, ny, bri in layout["rects"]:
        src = frames[min(max(i + off, 0), n - 1)]
        if kind >= 0:
            src = variant(src, kind)
        patch = src[y:y + h_, x:x + w_]
        if zoom != 1.0:                                                   # blown up / shrunk around its centre
            zw, zh = max(2, int(w_ * zoom)), max(2, int(h_ * zoom))
            patch = cv2.resize(patch, (zw, zh))
            cx, cy = x + w_ // 2, y + h_ // 2
            x, y, w_, h_ = cx - zw // 2, cy - zh // 2, zw, zh
        patch = np.clip(patch.astype(np.float32) * bri, 0, 255).astype(np.uint8)
        x, y = x + nx, y + ny
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w_, SW), min(y + h_, SH)
        if x1 > x0 and y1 > y0:
            out[y0:y1, x0:x1] = patch[y0 - y:y1 - y, x0 - x:x1 - x]
    for y, bh, dx in layout["slices"]:
        out[y:y + bh] = np.roll(out[y:y + bh], dx, axis=1)
    ff.stdin.write(cv2.resize(out, (W, H), interpolation=cv2.INTER_LINEAR).tobytes())
ff.stdin.close(); ff.wait()
print("intro_screen_collage.mp4:", n, "frames")
