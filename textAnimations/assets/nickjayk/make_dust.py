"""Dust motes drifting through the window-light beam of the demo background (images/demo_bg_room.png).
4 s loop, 1920x1080 on black, composite with Add. Motes are brighter inside the beam band (upper-left to lower-right)."""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS, N = 1920, 1080, 30, 120
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(5)
n = 420
x0, y0 = rng.uniform(0, W, n), rng.uniform(0, H, n)
r = rng.uniform(0.8, 3.2, n)
amp = rng.uniform(8, 40, n)
ph = rng.uniform(0, 2 * math.pi, n)
drift = rng.integers(-1, 2, n) * W / 6  # whole-frame drift per loop keeps it seamless (wraps)


def beam(x, y):
    """1 inside the diagonal light band, falling to 0.15 outside."""
    d = abs((y - 0.55 * x) - 120) / 420
    return 0.15 + 0.85 * math.exp(-d * d * 3)


p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                      os.path.join(HERE, "dust_beam.mp4")], stdin=subprocess.PIPE)
for f in range(N):
    t = f / N
    img = Image.new("L", (W, H))
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = (x0[i] + drift[i] * t) % W
        y = (y0[i] + amp[i] * math.sin(2 * math.pi * t + ph[i]) - 60 * t) % H
        b = int(200 * beam(x, y) * (0.6 + 0.4 * math.sin(2 * math.pi * (2 * t) + ph[i])))
        d.ellipse([x - r[i], y - r[i], x + r[i], y + r[i]], fill=b)
    a = np.asarray(img.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    g = np.asarray(img.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    lum = np.clip(a + g * 0.8, 0, 1)
    rgb = lum[..., None] * np.array([0.55, 0.75, 1.0], np.float32)
    p.stdin.write((rgb * 255).astype(np.uint8).tobytes())
p.stdin.close()
p.wait()
print("dust_beam")
