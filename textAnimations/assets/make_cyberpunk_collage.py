"""Cyberpunk: the glitch cut-up that ends the opening, over the crowd moments around her (projects/cyberpunk/
open_c-g.png, a new one every 4 frames, her held in the centre), cut around her the way make_collage_shots.py cut up
Intro 1's stills. The other overheads (the anime girl,
the light being) and the opening's other moments share the composition, so a slice from any of them lands in place.
Every 2 frames a new layout over open_c: 4-9 rectangles centred on her (some shrunk, some blown up around their
centre, some nudged, each a touch brighter or darker so the edges show) and 2-5 thin horizontal slices through her,
shifted sideways. The last 4 frames are clean, so the push lands on her face for the thermogram match cut.
Writes assets/collage/cyberpunk_overhead_glitch.mp4 (1920x1080, 30 fps)."""
import random
import subprocess

from PIL import Image, ImageEnhance

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/cyberpunk_overhead_glitch.mp4"
W, H, FPS = 1920, 1080, 30
FRAMES, CLEAN_FROM = 18, 14
BOX = (0.42, 0.33, 0.57, 0.90)  # her, as fractions of the frame


def load(path):
    return Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)


pool = {k: load(CP + "open_%s.png" % k) for k in "abcdefg"}
pool["anime"], pool["being"] = load(CP + "shot3.png"), load(CP + "shot1.png")
BASES = ["g", "c", "d", "e"]  # the crowd keeps moving around her underneath, a new moment every 4 frames
SOURCES = ["anime", "anime", "being", "being", "a", "b", "f"]
base = pool["g"]
rnd = random.Random("cyberpunk overhead glitch")


def rect(frame):
    l, t, r, b = BOX
    cx, cy = rnd.uniform(l - 0.03, r + 0.03) * W, rnd.uniform(t, b) * H
    w, h = int(W * rnd.uniform(0.05, 0.20)), int(H * rnd.uniform(0.05, 0.26))
    x, y = int(min(max(cx - w / 2, 0), W - w)), int(min(max(cy - h / 2, 0), H - h))
    src = pool[rnd.choice(SOURCES)]
    s = rnd.choice([0.55, 0.75, 1.0, 1.0, 1.4, 1.8])
    sw, sh = w / s, h / s
    sx = min(max(x + w / 2 - sw / 2, 0), W - sw)
    sy = min(max(y + h / 2 - sh / 2, 0), H - sh)
    patch = src.crop((int(sx), int(sy), int(sx + sw), int(sy + sh))).resize((w, h), Image.LANCZOS)
    patch = ImageEnhance.Brightness(patch).enhance(rnd.choice([0.75, 0.9, 1.15, 1.3]))
    dx, dy = int(rnd.uniform(-0.03, 0.03) * W), int(rnd.uniform(-0.03, 0.03) * H)
    frame.paste(patch, (min(max(x + dx, 0), W - w), min(max(y + dy, 0), H - h)))


def band(frame):
    l, t, r, b = BOX
    h = max(4, int(H * rnd.uniform(0.012, 0.05)))
    y = min(int(rnd.uniform(t, b) * H), H - h)
    x0, x1 = int(max(0, (l - 0.06) * W)), int(min(W, (r + 0.06) * W))
    strip = ImageEnhance.Brightness(pool[rnd.choice(SOURCES)].crop((x0, y, x1, y + h))).enhance(rnd.choice([0.8, 1.0, 1.25]))
    shift = int(rnd.uniform(-0.06, 0.06) * W)
    frame.paste(strip, (min(max(x0 + shift, 0), W - (x1 - x0)), y))


p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", OUT],
                     stdin=subprocess.PIPE)
frame = base
for f in range(FRAMES):
    base = pool[BASES[(f // 4) % len(BASES)]]
    if f >= CLEAN_FROM:
        frame = base
    elif f % 2 == 0:
        frame = base.copy()
        for _ in range(rnd.randint(4, 9)):
            rect(frame)
        for _ in range(rnd.randint(2, 5)):
            band(frame)
    p.stdin.write(frame.tobytes())
p.stdin.close()
p.wait()
print(FRAMES, "frames ->", OUT)
