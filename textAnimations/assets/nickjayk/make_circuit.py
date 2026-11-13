"""Circuit-board wall in the nickjaykdesign.com style: traces drawn in glowing blue particles,
pads at the joints, and bright data pulses running along the traces. 4 s loop, 4800x1600, on black."""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS, N = 4800, 1600, 30, 120
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(11)
STEP = 40  # trace grid


def trace():
    """A Manhattan trace with 45° doglegs, as a list of points."""
    x, y = rng.integers(0, W // STEP) * STEP, rng.integers(0, H // STEP) * STEP
    pts = [(x, y)]
    d = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    for _ in range(rng.integers(3, 8)):
        n = rng.integers(2, 12)
        if rng.random() < 0.35 and d[0] != 0:
            dd = (d[0], rng.choice([-1, 1]))
        else:
            dd = d
        x, y = x + dd[0] * n * STEP, y + dd[1] * n * STEP
        pts.append((x, y))
        if rng.random() < 0.5:
            d = (d[1], d[0]) if rng.random() < 0.5 else (-d[1], -d[0])
    return pts


def sample(pts, spacing):
    """Points every `spacing` px along a polyline, and its total length."""
    out, total = [], 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L // spacing))
        for i in range(k):
            out.append((x0 + (x1 - x0) * i / k, y0 + (y1 - y0) * i / k))
        total += L
    out.append(pts[-1])
    return out, total


traces = [trace() for _ in range(260)]
static = Image.new("L", (W, H))
d = ImageDraw.Draw(static)
paths = []
for t in traces:
    dots, total = sample(t, 7)
    paths.append((dots, total))
    for (x, y) in dots:
        b = int(rng.uniform(70, 150))
        d.ellipse([x - 1.3, y - 1.3, x + 1.3, y + 1.3], fill=b)
    for (x, y) in (t[0], t[-1]):  # pads
        d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=200, width=2)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=230)
static_a = np.asarray(static, np.float32) / 255
static_glow = static_a + np.asarray(static.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255 * 0.9 \
              + np.asarray(static.filter(ImageFilter.GaussianBlur(18)), np.float32) / 255 * 0.6

# pulses: each trace carries 1-2 pulses that make whole laps per loop
pulses = [(i, rng.uniform(0, 1), int(rng.integers(1, 3))) for i in range(len(paths)) for _ in range(rng.integers(1, 3))]
BLUE = np.array([40, 140, 255], np.float32) / 255

p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
                      os.path.join(HERE, "circuit_wall.mp4")], stdin=subprocess.PIPE)
for f in range(N):
    img = Image.new("L", (W, H))
    dd = ImageDraw.Draw(img)
    for (i, phase, laps) in pulses:
        dots, _ = paths[i]
        pos = ((phase + laps * f / N) % 1) * (len(dots) - 1)
        for k in range(10):  # head and a short tail
            j = int(pos) - k
            if j < 0:
                break
            x, y = dots[j]
            r = 2.6 - k * 0.2
            dd.ellipse([x - r, y - r, x + r, y + r], fill=int(255 * (1 - k / 10)))
    a = np.asarray(img, np.float32) / 255
    g = a + np.asarray(img.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255 * 1.2 \
        + np.asarray(img.filter(ImageFilter.GaussianBlur(20)), np.float32) / 255 * 0.8
    lum = np.clip(static_glow + g, 0, 1.8)
    rgb = lum[..., None] * BLUE * 1.2 + np.clip(static_a + a - 0.6, 0, 1)[..., None] * 1.3
    p.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
p.stdin.close()
p.wait()
print("circuit_wall")
