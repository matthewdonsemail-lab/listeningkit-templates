"""Background elements in the style of nickjaykdesign.com (references/nickjaykdesign):
objects built from glowing electric-blue particles on black, warp streaks, falling code, HUD brackets.
Each loop is 4 s at 30 fps, 1920x1080, on black (composite with Add / Screen)."""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SECONDS = 1920, 1080, 30, 4
N = FPS * SECONDS
HERE = os.path.dirname(os.path.abspath(__file__))
BLUE = np.array([40, 140, 255], np.float32)
rng = np.random.default_rng(7)


def glow(img):
    """Particle glow: tight bloom plus a wide halo, tinted electric blue, white-hot cores."""
    a = np.asarray(img, np.float32) / 255
    near = np.asarray(img.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    far = np.asarray(img.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    lum = np.clip(a + near * 0.9 + far * 0.8, 0, 1.6)
    rgb = lum[..., None] * BLUE / 255 * 1.25
    rgb += np.clip(a - 0.55, 0, 1)[..., None] * 1.4  # hot cores
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def encode(name, frames):
    path = os.path.join(HERE, name + ".mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print(name)


def warp_tunnel():
    """Hyperspace: dots streaming out of the centre, stretching into streaks as they pass."""
    n = 2600
    ang = rng.uniform(0, 2 * math.pi, n)
    z0 = rng.uniform(0, 1, n)
    rad = rng.uniform(0.15, 1.0, n)
    for f in range(N):
        img = Image.new("L", (W, H))
        d = ImageDraw.Draw(img)
        z = (z0 - f / N) % 1 + 0.02  # loops: each dot travels exactly once per loop
        for i in range(n):
            r1 = rad[i] * 260 / z[i]
            r0 = rad[i] * 260 / (z[i] + 0.035)
            if r0 > 1300:
                continue
            c, s = math.cos(ang[i]), math.sin(ang[i])
            b = int(min(255, 40 + 220 * (1 - z[i])))
            d.line([(W / 2 + c * r0, H / 2 + s * r0), (W / 2 + c * r1, H / 2 + s * r1)], fill=b,
                   width=1 if z[i] > 0.3 else 2)
        yield glow(img)


def code_rain():
    """Columns of glyphs falling, bright heads with fading trails."""
    font = ImageFont.truetype("consola.ttf", 20)
    chars = "01アイウエオカキクケコｱｲｳｴｵ<>/{}#$%&*+=LOG"
    cols = W // 18
    speed = rng.integers(1, 4, cols) * 9  # rows per loop multiple, so it loops
    head0 = rng.uniform(0, H, cols)
    glyphs = rng.integers(0, len(chars), (cols, H // 22 + 2))
    for f in range(N):
        img = Image.new("L", (W, H))
        d = ImageDraw.Draw(img)
        for c in range(cols):
            head = (head0[c] + f / N * speed[c] * 22 * 4) % (H + 400)
            for k in range(0, 18):
                y = head - k * 22
                if y < -22 or y > H:
                    continue
                row = int(y // 22) % glyphs.shape[1]
                g = chars[(glyphs[c, row] + (f // 3 if k == 0 else 0)) % len(chars)]
                b = 255 if k == 0 else int(170 * (1 - k / 18))
                d.text((c * 18, y), g, font=font, fill=b)
        yield glow(img)


def dot_globe():
    """A globe made of particles: meridians and parallels in dots, turning, twinkling."""
    pts = []
    for lat in np.linspace(-80, 80, 17):
        for lon in np.arange(0, 360, 2.2):
            pts.append((lat, lon))
    for lon in np.arange(0, 180, 15):
        for lat in np.arange(-90, 90, 2.2):
            pts.append((lat, lon))
    pts = np.radians(np.array(pts))
    tw = rng.uniform(0, 2 * math.pi, len(pts))
    R = 400
    for f in range(N):
        img = Image.new("L", (W, H))
        d = ImageDraw.Draw(img)
        rot = 2 * math.pi * f / N / 3  # a third of a turn per loop: meridians every 15° repeat
        lat, lon = pts[:, 0], pts[:, 1] + rot
        x = np.cos(lat) * np.sin(lon)
        y = np.sin(lat)
        z = np.cos(lat) * np.cos(lon)
        tilt = math.radians(18)
        y2 = y * math.cos(tilt) - z * math.sin(tilt)
        z2 = y * math.sin(tilt) + z * math.cos(tilt)
        for i in range(len(pts)):
            front = z2[i] > 0
            b = (150 if front else 45) * (0.6 + 0.4 * math.sin(tw[i] + f * 0.5))
            px, py = W / 2 + x[i] * R, H / 2 - y2[i] * R
            s = 1.6 if front else 1.0
            d.ellipse([px - s, py - s, px + s, py + s], fill=int(b))
        yield glow(img)


def hud_frame():
    """Static HUD brackets and ticks, transparent PNG."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (90, 175, 255, 230)
    m, L = 70, 90
    for (x, y, sx, sy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        d.line([(x, y), (x + sx * L, y)], fill=col, width=3)
        d.line([(x, y), (x, y + sy * L)], fill=col, width=3)
    for i in range(41):
        x = W / 2 - 400 + i * 20
        d.line([(x, H - m), (x, H - m - (14 if i % 5 == 0 else 7))], fill=col, width=2)
    font = ImageFont.truetype("consola.ttf", 18)
    d.text((m + 10, m + 14), "LOG // LISTENINGKIT", font=font, fill=col)
    d.text((W - m - 230, m + 14), "SIGNAL  ▮▮▮▮▯  LIVE", font=font, fill=col)
    d.text((m + 10, H - m - 36), "CH 06   REC ●", font=font, fill=col)
    img.save(os.path.join(HERE, "hud_frame.png"))
    print("hud_frame")


if __name__ == "__main__":
    hud_frame()
    encode("warp_tunnel", warp_tunnel())
    encode("code_rain", code_rain())
    encode("dot_globe", dot_globe())
